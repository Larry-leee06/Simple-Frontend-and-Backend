"""
WSGI config for eco_community project.
"""

import os
from waitress import serve
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_community.settings')

application = get_wsgi_application()

if __name__ == "__main__":
    # 使用 waitress 启动 Django 应用
    serve(application, host="0.0.0.0", port=8000)
