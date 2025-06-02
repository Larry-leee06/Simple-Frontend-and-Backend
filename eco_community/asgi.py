"""
ASGI config for eco_community project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_community.settings')

application = get_asgi_application() 