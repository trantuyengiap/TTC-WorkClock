from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import NotificationLog, User
from app.schemas.dashboard import DashboardStats
from app.services.elasticsearch.repository import AttendanceElasticRepository
from app.services.notifications.gateway import NotificationGateway

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/stats', response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> DashboardStats:
    repo = AttendanceElasticRepository()
    gateway = NotificationGateway()
    total_employees = db.query(func.count(User.id)).scalar() or 0
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    sent_today = (
        db.query(func.count(NotificationLog.id))
        .filter(NotificationLog.created_at >= today_start)
        .scalar()
        or 0
    )
    present = repo.report_summary(today_start.isoformat(), datetime.now(UTC).isoformat()).get('present_users', 0)
    return DashboardStats(
        total_employees=total_employees,
        checked_in_today=present,
        not_checked_in_today=max(total_employees - present, 0),
        notifications_sent_today=sent_today,
        elasticsearch_status=repo.health(),
        worker_status='online',
        channels_status={channel: 'configured' for channel in gateway.supported_channels()},
    )
