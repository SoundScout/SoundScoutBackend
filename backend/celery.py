# backend/celery.py
import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# 2. Read broker & backend URLs from Django settings (using decouple in settings.py).
app.config_from_object('django.conf:settings', namespace='CELERY')

# 3. Discover and load task modules in all INSTALLED_APPS
app.autodiscover_tasks()

# Optional: define a debug task
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')