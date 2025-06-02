import mysql.connector
from mysql.connector import Error

try:
    # 连接到MySQL服务器（不指定数据库）
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="wanglele060603"  # 使用您的MySQL密码
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS eco_community CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("数据库 'eco_community' 创建成功或已存在")
        
        # 检查是否创建成功
        cursor.execute("SHOW DATABASES LIKE 'eco_community'")
        result = cursor.fetchone()
        if result:
            print("确认数据库已存在")
        else:
            print("警告：创建数据库失败")
            
        # 创建用户并授权（如果需要）
        try:
            cursor.execute("CREATE USER IF NOT EXISTS 'django'@'localhost' IDENTIFIED BY 'django123'")
            cursor.execute("GRANT ALL PRIVILEGES ON eco_community.* TO 'django'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print("用户'django'创建并授权成功")
        except Error as e:
            print(f"创建用户时出错: {e}")
        
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")
        
        print("\n现在您可以使用以下配置在settings.py中设置数据库:")
        print("DATABASES = {")
        print("    'default': {")
        print("        'ENGINE': 'django.db.backends.mysql',")
        print("        'NAME': 'eco_community',")
        print("        'USER': 'root',  # 或使用 'django'")
        print("        'PASSWORD': 'wanglele060603',  # 或使用 'django123'")
        print("        'HOST': 'localhost',")
        print("        'PORT': '3306',")
        print("        'OPTIONS': {")
        print("            'charset': 'utf8mb4',")
        print("        },")
        print("    }")
        print("}")
        
except Error as e:
    print(f"连接MySQL出错: {e}")
    
    if "Can't connect to MySQL server" in str(e):
        print("\n可能的原因:")
        print("1. MySQL服务未运行")
        print("2. MySQL服务器地址错误")
        print("\n解决方案:")
        print("- 安装MySQL服务器: https://dev.mysql.com/downloads/mysql/")
        print("- 启动MySQL服务: 控制面板 -> 管理工具 -> 服务 -> MySQL -> 启动")
        print("- 或通过命令行启动: net start MySQL")
        
    elif "Access denied" in str(e):
        print("\n可能的原因:")
        print("1. 用户名或密码错误")
        print("\n解决方案:")
        print("- 确认MySQL root密码")
        print("- 重置MySQL root密码: https://dev.mysql.com/doc/refman/8.0/en/resetting-permissions.html")
        
    print("\n或者您可以改用SQLite数据库:")
    print("DATABASES = {")
    print("    'default': {")
    print("        'ENGINE': 'django.db.backends.sqlite3',")
    print("        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),")
    print("    }")
    print("}") 