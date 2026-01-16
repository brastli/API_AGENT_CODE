#!/usr/bin/env python3
import os
import sys
import argparse
import configparser
import mysql.connector


DDL = [
    """
    CREATE TABLE IF NOT EXISTS users (
      id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(50) NOT NULL,
      email VARCHAR(255) NULL,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uq_users_username (username),
      UNIQUE KEY uq_users_email (email)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS api_registry (
      id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      api_name VARCHAR(128) NULL,
      method VARCHAR(16) NOT NULL,
      path VARCHAR(255) NOT NULL,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uq_api_registry_method_path (method, path)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS api_audit_log (
      id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      method VARCHAR(16) NOT NULL,
      path VARCHAR(255) NOT NULL,
      status_code INT NOT NULL,
      latency_ms INT NOT NULL,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_api_audit_log_created_at (created_at)
    ) ENGINE=InnoDB
    """,
]


def load_ini(path: str) -> configparser.ConfigParser:
    if not os.path.exists(path):
        raise RuntimeError(f"INI not found: {path}")

    cp = configparser.ConfigParser()
    # 用 utf-8-sig 兼容 Windows 写 ini 时可能带 BOM 的情况
    with open(path, "r", encoding="utf-8-sig") as f:
        cp.read_file(f)
    return cp


def connect(host: str, port: int, user: str, password: str, database: str | None = None):
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        autocommit=True,
        connection_timeout=10,
    )


def exec_one(cur, sql: str):
    cur.execute(sql)
    # mysql-connector 会自动提交（autocommit=True）


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ini", default=os.environ.get("CONFIG_INI"), help="Path to config ini (or set CONFIG_INI)")
    args = ap.parse_args()

    if not args.ini:
        print("Missing --ini or CONFIG_INI env var", file=sys.stderr)
        sys.exit(2)

    cp = load_ini(args.ini)

    # admin/master credentials
    host = cp.get("mysql_admin", "host")
    port = cp.getint("mysql_admin", "port", fallback=3306)
    admin_user = cp.get("mysql_admin", "user")
    admin_password = cp.get("mysql_admin", "password")

    # app settings
    db_name = cp.get("mysql", "database", fallback="api_agent_db")
    app_user = cp.get("mysql", "app_user", fallback="api_agent")
    app_password = cp.get("mysql", "app_password")

    print(f"[1/4] Connecting as admin to {host}:{port} ...")
    cnx = connect(host, port, admin_user, admin_password)
    cur = cnx.cursor()

    print(f"[2/4] Creating database if not exists: {db_name}")
    exec_one(cur, f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

    cur.close()
    cnx.close()

    print(f"[3/4] Creating tables in {db_name}")
    cnx2 = connect(host, port, admin_user, admin_password, database=db_name)
    cur2 = cnx2.cursor()
    for sql in DDL:
        exec_one(cur2, sql)
    cur2.close()
    cnx2.close()

    print(f"[4/4] Creating app user + grants: {app_user}@%")
    cnx3 = connect(host, port, admin_user, admin_password)
    cur3 = cnx3.cursor()

    # 兼容 MySQL 8：不存在则创建；存在则不报错
    exec_one(cur3, f"CREATE USER IF NOT EXISTS '{app_user}'@'%' IDENTIFIED BY %s",)
    # 上面这句 mysql-connector 对参数化 DDL 支持不好，所以用下面这种安全方式处理：
    # 注意：如果你的密码包含单引号，请避免或自行转义；生产建议走 Secrets Manager/SSM
    safe_pw = app_password.replace("'", "\\'")
    exec_one(cur3, f"CREATE USER IF NOT EXISTS '{app_user}'@'%' IDENTIFIED BY '{safe_pw}'")

    exec_one(cur3, f"GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX ON `{db_name}`.* TO '{app_user}'@'%'")
    exec_one(cur3, "FLUSH PRIVILEGES")

    cur3.close()
    cnx3.close()

    print("DONE: database + tables + app user are ready.")


if __name__ == "__main__":
    main()
