from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import AttendanceJob, ReminderRule, RuleTypeEnum, User
from app.services.elasticsearch.repository import AttendanceElasticRepository
from app.services.notifications.gateway import NotificationGateway
from app.services.scheduler.celery_app import celery_app
from app.utils.template import render_template


@celery_app.task(name='app.services.scheduler.tasks.scan_recent_attendance_events')
def scan_recent_attendance_events() -> dict:
    db = SessionLocal()
    repo = AttendanceElasticRepository()
    job = AttendanceJob(job_type='scan_recent_attendance_events', status='running', started_at=datetime.now(UTC))
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        events = repo.recent_events(minutes=10, size=100, sort_order='desc')
        job.status = 'success'
        job.finished_at = datetime.now(UTC)
        job.result = {'count': len(events)}
        db.commit()
        return {'count': len(events)}
    except Exception as exc:
        job.status = 'failed'
        job.finished_at = datetime.now(UTC)
        job.error_message = str(exc)
        db.commit()
        return {'error': str(exc)}
    finally:
        db.close()


@celery_app.task(name='app.services.scheduler.tasks.evaluate_reminder_rules')
def evaluate_reminder_rules() -> dict:
    db = SessionLocal()
    gateway = NotificationGateway()
    repo = AttendanceElasticRepository()
    now = datetime.now(UTC)
    summary: list[dict] = []
    try:
        rules = db.scalars(select(ReminderRule).where(ReminderRule.is_active.is_(True))).all()
        users = db.scalars(select(User).where(User.is_active.is_(True))).all()
        for rule in rules:
            if rule.rule_type not in {RuleTypeEnum.CHECK_IN, RuleTypeEnum.CHECK_OUT}:
                continue
            attendance_codes = [user.attendance_code for user in users if user.attendance_code]
            checked_in = repo.checked_in_users((now - timedelta(hours=8)).isoformat(), now.isoformat(), attendance_codes)
            for user in users:
                if not user.attendance_code or user.attendance_code in checked_in:
                    continue
                target = next((item for item in user.notification_targets if item.is_enabled), None)
                if not target:
                    continue
                message = render_template(
                    'Xin chào {name}, bạn chưa chấm công cho ca {shift_name}.',
                    {'name': user.full_name, 'shift_name': user.shift.name if user.shift else 'mặc định'},
                )
                result = gateway.send(db, target.channel.channel_type.value, target.recipient, message, user_id=user.id, template_name=rule.name)
                summary.append({'user': user.username, 'channel': target.channel.channel_type.value, 'success': result.success})
        return {'sent': summary}
    finally:
        db.close()
