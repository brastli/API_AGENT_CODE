# db.py
import os
from pathlib import Path
from configparser import ConfigParser
from typing import Any, Dict, Iterable, Optional, Tuple

from mysql.connector.pooling import MySQLConnectionPool

_POOL: Optional[MySQLConnectionPool] = None
_CFG: Optional[dict] = None


def load_config() -> dict:
    """
    读取 ini 配置（默认：项目根目录下 config.ini）
    也支持通过环境变量 CONFIG_INI 指定 ini 路径。
    """
    global _CFG
    if _CFG is not None:
        return _CFG

    ini_path = os.getenv("CONFIG_INI")
    if ini_path:
        p = Path(ini_path).expanduser()
    else:
        # db.py 在 API_AGENT_CODE/ 目录内，上一级是项目根
        p = Path(__file__).resolve().parent.parent / "config.ini"

    if not p.exists():
        raise RuntimeError(f"INI config not found: {p}")

    cp = ConfigParser()
    cp.read(p, encoding="utf-8")

    if "mysql" not in cp:
        raise RuntimeError("Missing [mysql] section in ini")

    sec = cp["mysql"]
    _CFG = {
        "host": sec.get("host", "localhost"),
        "port": sec.getint("port", 3306),
        "user": sec.get("user"),
        "password": sec.get("password"),
        "database": sec.get("database"),
        "pool_size": sec.getint("pool_size", 5),
    }

    for k in ("user", "password", "database"):
        if not _CFG.get(k):
            raise RuntimeError(f"Missing mysql.{k} in ini")

    return _CFG


def get_pool() -> MySQLConnectionPool:
    global _POOL
    if _POOL is not None:
        return _POOL

    cfg = load_config()
    _POOL = MySQLConnectionPool(
        pool_name="api_agent_pool",
        pool_size=int(cfg["pool_size"]),
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )
    return _POOL


def ping_db() -> bool:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        _ = cur.fetchone()
        return True
    finally:
        conn.close()


def upsert_api_registry(entries: Iterable[Tuple[str, str, str]]) -> None:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor()
        cur.executemany(
            """
            INSERT INTO api_registry (api_name, method, path)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE api_name=VALUES(api_name), updated_at=CURRENT_TIMESTAMP
            """,
            list(entries),
        )
        conn.commit()
    finally:
        conn.close()


def insert_audit_log(method: str, path: str, status_code: int, latency_ms: int) -> None:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO api_audit_log (method, path, status_code, latency_ms) VALUES (%s, %s, %s, %s)",
            (method, path, int(status_code), int(latency_ms)),
        )
        conn.commit()
    finally:
        conn.close()


# ---- users CRUD ----

def fetch_users(limit: int = 50, offset: int = 0) -> list[Dict[str, Any]]:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, username, email, created_at, updated_at FROM users ORDER BY id DESC LIMIT %s OFFSET %s",
            (int(limit), int(offset)),
        )
        return cur.fetchall()
    finally:
        conn.close()


def fetch_user(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, username, email, created_at, updated_at FROM users WHERE id=%s",
            (int(user_id),),
        )
        return cur.fetchone()
    finally:
        conn.close()


def create_user(username: str, email: Optional[str]) -> int:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def update_user(user_id: int, username: Optional[str], email: Optional[str]) -> bool:
    if username is None and email is None:
        return False

    fields = []
    vals = []
    if username is not None:
        fields.append("username=%s")
        vals.append(username)
    if email is not None:
        fields.append("email=%s")
        vals.append(email)
    vals.append(int(user_id))

    conn = get_pool().get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=%s", tuple(vals))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_user(user_id: int) -> bool:
    conn = get_pool().get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (int(user_id),))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
