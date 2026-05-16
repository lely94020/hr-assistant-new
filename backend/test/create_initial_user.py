"""
创建初始测试用户的脚本
运行方式: python create_initial_user.py
"""
import bcrypt
import pymysql
from datetime import datetime

# 生成密码哈希
password = "admin123"
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password_bytes, salt)
hashed_password_str = hashed_password.decode('utf-8')

print("=" * 60)
print("创建 HR 系统初始用户")
print("=" * 60)
print(f"用户名: admin")
print(f"密码: {password}")
print(f"加密哈希: {hashed_password_str[:50]}...")
print("=" * 60)

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678',
    'database': 'hr_assistant',
    'charset': 'utf8mb4'
}

try:
    # 连接数据库
    print("\n正在连接数据库...")
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    print("✅ 数据库连接成功")

    # 检查用户是否已存在
    check_sql = "SELECT id, username, status FROM sys_user WHERE username = %s"
    cursor.execute(check_sql, ('admin',))
    existing_user = cursor.fetchone()

    if existing_user:
        print(f"\n⚠️  用户 'admin' 已存在 (ID: {existing_user[0]}, 状态: {existing_user[2]})")
        print("正在更新密码...")
        update_sql = "UPDATE sys_user SET password = %s, status = 1, updated_at = %s WHERE username = %s"
        cursor.execute(update_sql, (hashed_password_str, datetime.now(), 'admin'))
        connection.commit()
        print("✅ 用户 'admin' 密码已更新")
        print("✅ 用户状态已设置为正常")
    else:
        print("\n正在创建新用户 'admin'...")
        # 插入新用户
        insert_sql = """
        INSERT INTO sys_user (username, password, real_name, email, phone, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_sql, (
            'admin',
            hashed_password_str,
            '管理员',
            'admin@example.com',
            '13800138000',
            1,
            datetime.now(),
            datetime.now()
        ))

        connection.commit()
        print("✅ 用户 'admin' 创建成功！")

    # 验证用户
    print("\n正在验证用户信息...")
    cursor.execute("SELECT id, username, real_name, email, status FROM sys_user WHERE username = 'admin'")
    user = cursor.fetchone()
    if user:
        print("✅ 用户信息验证成功：")
        print(f"   ID: {user[0]}")
        print(f"   用户名: {user[1]}")
        print(f"   姓名: {user[2]}")
        print(f"   邮箱: {user[3]}")
        print(f"   状态: {'正常' if user[4] == 1 else '禁用'}")

    print("\n" + "=" * 60)
    print("登录信息")
    print("=" * 60)
    print(f"   用户名: admin")
    print(f"   密码: admin123")
    print(f"   访问地址: http://localhost:8000/docs")
    print("=" * 60)
    print("\n请妥善保管密码信息！")

except pymysql.Error as e:
    print(f"\n❌ 数据库错误: {e}")
    if 'connection' in locals():
        connection.rollback()
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    if 'connection' in locals():
        connection.rollback()
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
        print("\n数据库连接已关闭")