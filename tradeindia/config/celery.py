"""
Celery configuration for TradeIndia
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('tradeindia')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

# Celery beat schedule
app.conf.beat_schedule = {
    # Verify new listings every 10 minutes
    'verify-new-listings': {
        'task': 'apps.ai_verification.tasks.batch_verify_listings',
        'schedule': crontab(minute='*/10'),
    },
    
    # Update user trust scores daily
    'update-trust-scores': {
        'task': 'apps.ai_verification.tasks.update_user_trust_scores',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    
    # Send saved search alerts
    'send-search-alerts': {
        'task': 'apps.search.tasks.send_saved_search_alerts',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    
    # Clean up expired listings
    'cleanup-expired-listings': {
        'task': 'apps.listings.tasks.cleanup_expired_listings',
        'schedule': crontab(hour=0, minute=0),  # Midnight daily
    },
    
    # Update listing statistics
    'update-listing-stats': {
        'task': 'apps.listings.tasks.update_listing_statistics',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    
    # Send notification digests
    'send-daily-digests': {
        'task': 'apps.notifications.tasks.send_daily_digests',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
    
    # Clean up old data
    'cleanup-old-data': {
        'task': 'apps.core.tasks.cleanup_old_data',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # 3 AM Sunday
    },
    
    # Update search analytics
    'update-search-analytics': {
        'task': 'apps.search.tasks.update_search_analytics',
        'schedule': crontab(hour=1, minute=0),  # 1 AM daily
    },
}

# Celery configuration
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Task routing
    task_routes={
        'apps.ai_verification.tasks.*': {'queue': 'ai_verification'},
        'apps.notifications.tasks.*': {'queue': 'notifications'},
        'apps.payments.tasks.*': {'queue': 'payments'},
        'apps.search.tasks.*': {'queue': 'search'},
    },
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')