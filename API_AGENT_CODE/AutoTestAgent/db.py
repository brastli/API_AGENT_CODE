import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

def init_db():
    """初始化表结构"""
    conn = get_connection()
    cursor = conn.cursor()
    # 创建测试任务表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255) NOT NULL,
        method VARCHAR(10) DEFAULT 'GET',
        payload_template TEXT,
        status VARCHAR(20) DEFAULT 'pending'
    ) ENGINE=InnoDB;
    """)
    # 创建测试结果表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task_id INT,
        generated_code TEXT,
        execution_output TEXT,
        ai_evaluation TEXT,
        is_pass BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)
    conn.commit()
    conn.close()

def get_pending_tasks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM api_tasks WHERE status = 'pending' LIMIT 1")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def save_result(task_id, code, output, evaluation, is_pass):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO test_results (task_id, generated_code, execution_output, ai_evaluation, is_pass)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (task_id, code, output, evaluation, is_pass))
    
    # 更新任务状态
    cursor.execute("UPDATE api_tasks SET status = 'completed' WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()