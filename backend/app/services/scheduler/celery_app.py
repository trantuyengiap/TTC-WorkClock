from celery import Celery

from app.core.config import settings

celery_app = Celery('workclock', broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.update(
    timezone=settings.app_timezone,
    task_track_started=True,
    beat_schedule={
        'scan-recent-attendance-events': {
            'task': 'app.services.scheduler.tasks.scan_recent_attendance_events',
            'schedule': 15.0,
        },
        'evaluate-reminder-rules': {
            'task': 'app.services.scheduler.tasks.evaluate_reminder_rules',
            'schedule': 60.0,
        },
    },
)
