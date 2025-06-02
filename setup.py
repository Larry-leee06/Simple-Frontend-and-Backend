import os
import sys
import time
import subprocess
import webbrowser
import importlib.util

# 检查MySQL库是否安装
mysql_connector_installed = importlib.util.find_spec("mysql.connector") is not None
mysqlclient_installed = importlib.util.find_spec("MySQLdb") is not None

print("========== 环保社区网站设置 ==========")
print(f"MySQL驱动检查:")
if mysql_connector_installed:
    print("✅ mysql-connector-python 已安装")
else:
    print("❌ mysql-connector-python 未安装")

if mysqlclient_installed:
    print("✅ mysqlclient 已安装")
else:
    print("❌ mysqlclient 未安装")

if not mysql_connector_installed and not mysqlclient_installed:
    print("\n您需要安装MySQL驱动才能连接到MySQL数据库")
    print("请运行以下命令安装驱动:")
    print("pip install mysqlclient")
    print("或")
    print("pip install mysql-connector-python")
    sys.exit(1)

# 步骤1：创建MySQL数据库
print("\n第一步：创建MySQL数据库")
print("--------------------------")
db_created = False

# 尝试不同的连接参数
connection_params = [
    {"host": "localhost", "user": "root", "password": "wanglele060603"},
    {"host": "127.0.0.1", "user": "root", "password": "wanglele060603"},
    {"host": "localhost", "user": "root", "password": ""},  # 空密码
    {"host": "localhost", "user": "root", "password": "root"},  # 常用默认密码
]

if mysql_connector_installed:
    import mysql.connector
    from mysql.connector import Error
    
    for params in connection_params:
        try:
            print(f"尝试连接到MySQL服务器 (host={params['host']}, user={params['user']})...")
            connection = mysql.connector.connect(**params)
            
            if connection.is_connected():
                print(f"✅ MySQL连接成功 (使用参数: {params})")
                cursor = connection.cursor()
                
                # 创建数据库
                print("正在创建数据库'eco_community'...")
                cursor.execute("CREATE DATABASE IF NOT EXISTS eco_community CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                
                # 检查是否创建成功
                cursor.execute("SHOW DATABASES LIKE 'eco_community'")
                result = cursor.fetchone()
                if result:
                    print("✅ 数据库'eco_community'创建成功")
                    db_created = True
                    
                    # 更新settings.py中的密码
                    with open("eco_community/settings.py", "r") as f:
                        settings = f.read()
                    
                    settings = settings.replace(
                        "'PASSWORD': 'wanglele060603'", 
                        f"'PASSWORD': '{params['password']}'"
                    )
                    
                    with open("eco_community/settings.py", "w") as f:
                        f.write(settings)
                    
                    print(f"✅ 已更新settings.py中的MySQL配置为: {params}")
                else:
                    print("❌ 创建数据库失败")
                
                cursor.close()
                connection.close()
                print("MySQL连接已关闭")
                break
        except Error as e:
            print(f"❌ 连接MySQL出错 (使用参数: {params}): {e}")
            continue

elif mysqlclient_installed:
    import MySQLdb
    
    for params in connection_params:
        try:
            print(f"尝试连接到MySQL服务器 (host={params['host']}, user={params['user']})...")
            connection = MySQLdb.connect(
                host=params['host'],
                user=params['user'],
                passwd=params['password']
            )
            
            print(f"✅ MySQL连接成功 (使用参数: {params})")
            cursor = connection.cursor()
            
            # 创建数据库
            print("正在创建数据库'eco_community'...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS eco_community CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # 检查是否创建成功
            cursor.execute("SHOW DATABASES LIKE 'eco_community'")
            result = cursor.fetchone()
            if result:
                print("✅ 数据库'eco_community'创建成功")
                db_created = True
                
                # 更新settings.py中的密码
                with open("eco_community/settings.py", "r") as f:
                    settings = f.read()
                
                settings = settings.replace(
                    "'PASSWORD': 'wanglele060603'", 
                    f"'PASSWORD': '{params['password']}'"
                )
                
                with open("eco_community/settings.py", "w") as f:
                    f.write(settings)
                
                print(f"✅ 已更新settings.py中的MySQL配置为: {params}")
            else:
                print("❌ 创建数据库失败")
            
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")
            break
        except MySQLdb.Error as e:
            print(f"❌ 连接MySQL出错 (使用参数: {params}): {e}")
            continue

if not db_created:
    print("\n❌ 无法连接MySQL或创建数据库")
    print("您可以:")
    print("1. 手动在MySQL中创建'eco_community'数据库")
    print("2. 检查MySQL是否正在运行")
    print("3. 确认用户名和密码正确")
    print("4. 尝试使用SQLite3代替MySQL")
    
    switch_to_sqlite = input("\n是否切换到SQLite3数据库？(y/n): ")
    if switch_to_sqlite.lower() == 'y':
        with open("eco_community/settings.py", "r") as f:
            settings = f.read()
        
        # 替换数据库配置
        sqlite_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}"""
        
        # 使用正则表达式查找并替换DATABASES配置
        import re
        pattern = r"DATABASES = \{.*?'default': \{.*?\}.*?\}"
        settings = re.sub(pattern, sqlite_config, settings, flags=re.DOTALL)
        
        with open("eco_community/settings.py", "w") as f:
            f.write(settings)
        
        print("✅ 已切换到SQLite3数据库")
        db_created = True
    else:
        print("❌ 操作取消，请手动配置数据库")
        sys.exit(1)

# 步骤2：应用数据库迁移
print("\n第二步：应用数据库迁移")
print("------------------------")
try:
    print("运行makemigrations...")
    subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
    
    print("运行migrate...")
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    print("✅ 数据库迁移成功应用")
except subprocess.CalledProcessError as e:
    print(f"❌ 应用迁移失败: {e}")
    print("请检查日志获取更多信息")
    sys.exit(1)

# 步骤3: 创建超级用户
print("\n第三步：创建超级用户")
print("--------------------")
try:
    print("正在创建超级用户...")
    subprocess.run([
        sys.executable, "manage.py", "shell", "-c",
        """
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('✅ 超级用户创建成功')
else:
    print('✅ 超级用户已存在，跳过创建')
        """
    ], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ 创建超级用户失败: {e}")
    print("将在启动服务器后手动创建超级用户")

# 步骤4: 启动服务器
print("\n第四步：启动Django服务器")
print("-----------------------")
print("服务器将在后台运行，您可以通过以下链接访问网站:")
print("首页: http://127.0.0.1:8000/")
print("登录: http://127.0.0.1:8000/login/ (用户名: admin, 密码: admin123456)")
print("商品列表: http://127.0.0.1:8000/products/")
print("个人资料: http://127.0.0.1:8000/profile/")
print("\n按Ctrl+C停止服务器")

# 打开浏览器
time.sleep(1)
webbrowser.open("http://127.0.0.1:8000/")

# 启动服务器
try:
    subprocess.run([sys.executable, "manage.py", "runserver"], check=True)
except KeyboardInterrupt:
    print("\n服务器已停止") 