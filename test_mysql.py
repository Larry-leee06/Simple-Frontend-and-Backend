import mysql.connector
import sys

try:
    # 尝试连接到MySQL
    print("正在尝试连接MySQL...")
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="wanglele060603",  # 使用settings.py中配置的密码
        database="eco_community"
    )
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"✅ 已成功连接到MySQL服务器，版本: {db_info}")
        
        # 检查数据库是否存在
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print(f"✅ 您已连接到数据库: {record[0]}")
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"✅ 数据库中的表({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 验证是否有需要的表
        required_tables = [
            "main_userprofile", 
            "auth_user", 
            "main_article",
            "main_comment", 
            "main_product",
            "main_productcategory"
        ]
        
        missing_tables = [table for table in required_tables if table not in [t[0] for t in tables]]
        
        if missing_tables:
            print(f"❌ 缺少以下表:")
            for table in missing_tables:
                print(f"  - {table}")
            print("\n需要创建缺失的表，请运行迁移命令:")
            print("python manage.py makemigrations")
            print("python manage.py migrate")
        else:
            print("✅ 所有必要的表都已存在")
        
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")

except mysql.connector.Error as e:
    print(f"❌ 连接MySQL时出错: {e}")
    
    if "Can't connect to MySQL server" in str(e):
        print("\n可能的原因:")
        print("1. MySQL服务未运行")
        print("2. MySQL服务器地址错误")
        print("3. 防火墙阻止了连接")
        print("\n解决方案:")
        print("- 检查MySQL服务是否启动: net start | findstr MySQL")
        print("- 尝试启动MySQL服务: net start MySQL")
        
    elif "Access denied" in str(e):
        print("\n可能的原因:")
        print("1. 用户名或密码错误")
        print("2. 用户没有访问权限")
        print("\n解决方案:")
        print("- 检查settings.py中的数据库用户名和密码")
        print("- 在MySQL中创建新用户或重置密码")
        
    elif "Unknown database" in str(e):
        print("\n可能的原因:")
        print("1. 数据库'eco_community'不存在")
        print("\n解决方案:")
        print("- 在MySQL中创建数据库: CREATE DATABASE eco_community;")
        print("- 然后运行迁移命令: python manage.py migrate")
    
    print("\n您也可以尝试将settings.py中的数据库改为SQLite3进行测试:")
    print("DATABASES = {")
    print("    'default': {")
    print("        'ENGINE': 'django.db.backends.sqlite3',")
    print("        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),")
    print("    }")
    print("}")
    
print("\n正在检查Django是否能启动...")
try:
    import django
    print(f"✅ Django已安装，版本为: {django.get_version()}")
except ImportError:
    print("❌ Django未安装")

# 检查端口8000是否被占用
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("127.0.0.1", 8000))
    print("✅ 端口8000未被占用，可以启动Django服务器")
    s.close()
except socket.error as e:
    print(f"❌ 端口8000已被占用: {e}")
    print("解决方案: 使用其他端口启动Django，例如: python manage.py runserver 8001") 