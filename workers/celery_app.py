"""
Celery Application Configuration
Background task processing for Solar PV LLM AI
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery app
app = Celery(
    'solar_pv_llm_ai',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
    include=['tasks.training_tasks', 'tasks.data_tasks', 'tasks.rag_tasks']
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Periodic tasks schedule
app.conf.beat_schedule = {
    'update-rag-index-daily': {
        'task': 'tasks.rag_tasks.update_rag_index',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-old-training-jobs': {
        'task': 'tasks.training_tasks.cleanup_old_jobs',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'generate-daily-report': {
        'task': 'tasks.data_tasks.generate_daily_report',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
}

if __name__ == '__main__':
    app.start()
