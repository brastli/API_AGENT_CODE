import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="demo_db",
    auth_plugin="mysql_native_password"
)


    print("Connected:", conn.is_connected())

    cursor = conn.cursor(dictionary=True)

    # 查询 users 表
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    for user in users:
        print(user)

except Error as e:
    print("MySQL error:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()


