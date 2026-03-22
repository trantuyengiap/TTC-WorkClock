from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import settings
from app.db.session import get_db
from app.models import RoleEnum, SystemSetting

router = APIRouter(prefix='/settings', tags=['settings'])


@router.get('/system')
def get_system_settings(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> dict:
    rows = db.query(SystemSetting).all()
    return {
        'database': settings.database_url,
        'elasticsearch_index_pattern': settings.elasticsearch_index_pattern,
        'timezone': settings.app_timezone,
        'field_mapping': {
            'timestamp': settings.es_field_timestamp,
            'event_time': settings.es_field_event_time,
            'user_id': settings.es_field_user_id,
            'user_name': settings.es_field_user_name,
            'device_name': settings.es_field_device_name,
            'device_id': settings.es_field_device_id,
        },
        'overrides': {row.key: row.value for row in rows},
    }


@router.post('/resync-rules')
def resync_rules(_: object = Depends(require_roles(RoleEnum.SUPER_ADMIN))) -> dict:
    return {'message': 'Celery Beat schedule uses dynamic DB evaluation task. Extend here for runtime sync if needed.'}
