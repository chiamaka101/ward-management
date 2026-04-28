import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception as e:
    print("🔥 DJANGO STARTUP ERROR:")
    traceback.print_exc()
    raise e