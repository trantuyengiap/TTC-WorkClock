from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import NotificationLog, RoleEnum
from app.schemas.notification import NotificationLogResponse, TestNotificationRequest
from app.services.notifications.gateway import NotificationGateway

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('/logs', response_model=list[NotificationLogResponse])
def list_notification_logs(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> list[NotificationLog]:
    return db.query(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(200).all()


@router.post('/test')
def test_notification(payload: TestNotificationRequest, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> dict:
    gateway = NotificationGateway()
    result = gateway.send(db, payload.channel, payload.recipient, payload.message, {'subject': 'Test notification'})
    return {'success': result.success, 'provider': result.provider, 'error': result.error, 'response': result.response}


@router.get('/channels')
def supported_channels(_: object = Depends(get_current_user)) -> dict:
    gateway = NotificationGateway()
    return {'channels': list(gateway.supported_channels())}
