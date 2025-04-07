import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickle_business.settings')

# Vercel expects 'handler' as the WSGI application
handler = get_wsgi_application()