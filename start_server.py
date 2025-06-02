import os
import sys
import time
import subprocess
import webbrowser

print("启动Django服务器...")
print("====================")

# 创建数据库表
print("1. 创建数据库表...")
try:
    subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    print("✅ 数据库表创建成功")
except subprocess.CalledProcessError as e:
    print(f"❌ 创建数据库表失败: {e}")
    print("继续启动服务器...")

# 创建超级用户（如果需要）
try:
    from django.contrib.auth.models import User
    if not User.objects.filter(is_superuser=True).exists():
        print("\n2. 创建超级用户...")
        print("用户名: admin")
        print("邮箱: admin@example.com")
        print("密码: admin123456")
        from django.contrib.auth.hashers import make_password
        User.objects.create(
            username='admin',
            email='admin@example.com',
            password=make_password('admin123456'),
            is_staff=True,
            is_superuser=True
        )
        print("✅ 超级用户创建成功")
    else:
        print("\n2. 已存在超级用户，跳过创建")
except Exception as e:
    print(f"❌ 创建超级用户失败: {e}")

# 启动服务器
print("\n3. 启动Django服务器...")
print("服务器将在后台运行，您可以通过以下链接访问网站:")
print("首页: http://127.0.0.1:8000/")
print("登录: http://127.0.0.1:8000/login/")
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