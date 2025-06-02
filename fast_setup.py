import os
import django
from pathlib import Path
import sys
import subprocess
import time
import webbrowser

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_community.settings')
django.setup()

print("========== 环保社区网站快速初始化 ==========")

# 确保使用SQLite
from django.conf import settings
if 'sqlite3' not in settings.DATABASES['default']['ENGINE']:
    print("当前不是SQLite数据库，正在切换...")
    
    # 获取settings.py文件路径
    settings_path = Path(__file__).resolve().parent / 'eco_community' / 'settings.py'
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings_content = f.read()
    
    # 创建新的数据库配置
    sqlite_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}"""
    
    # 替换数据库配置
    import re
    pattern = r"DATABASES = \{.*?'default': \{.*?\}.*?\}"
    settings_content = re.sub(pattern, sqlite_config, settings_content, flags=re.DOTALL)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(settings_content)
    
    print("✅ 已切换到SQLite数据库")
    
    # 重新加载设置
    from importlib import reload
    reload(settings)

# 运行迁移
print("\n步骤1: 应用数据库迁移")
print("------------------")

# 删除旧的数据库文件（如果存在）
db_path = Path(__file__).resolve().parent / 'db.sqlite3'
if db_path.exists():
    os.remove(db_path)
    print("已删除旧的数据库文件")

# 应用迁移
print("应用数据库迁移...")
subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
print("✅ 数据库迁移成功")

# 创建超级用户
print("\n步骤2: 创建超级用户")
print("---------------")

from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✅ 已创建超级用户: admin (密码: admin123456)")
else:
    print("✅ 超级用户已存在")

# 创建用户资料
print("\n步骤3: 创建用户资料")
print("---------------")

from django.apps import apps
UserProfile = apps.get_model('main', 'UserProfile')

for user in User.objects.all():
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"用户 {user.username} 的资料已存在")
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            user=user,
            is_public=True,
            theme_preference='light'
        )
        print(f"✅ 已为用户 {user.username} 创建资料")

# 启动服务器
print("\n步骤4: 启动服务器")
print("-------------")
print("服务器将在后台运行，您可以通过以下链接访问网站:")
print("首页: http://127.0.0.1:8000/")
print("登录: http://127.0.0.1:8000/login/ (用户名: admin, 密码: admin123456)")
print("商品列表: http://127.0.0.1:8000/products/")
print("个人资料: http://127.0.0.1:8000/profile/")

# 打开浏览器
time.sleep(1)
webbrowser.open("http://127.0.0.1:8000/")

# 启动服务器
try:
    subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
except KeyboardInterrupt:
    print("\n服务器已停止") 