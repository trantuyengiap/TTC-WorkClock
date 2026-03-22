from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.schemas.attendance import AttendanceEvent
from app.services.elasticsearch.repository import AttendanceElasticRepository

router = APIRouter(prefix='/attendance', tags=['attendance'])


@router.get('/events', response_model=list[AttendanceEvent])
def recent_attendance_events(
    minutes: int = Query(default=10, ge=1, le=1440),
    size: int = Query(default=100, ge=1, le=500),
    _: object = Depends(get_current_user),
) -> list[AttendanceEvent]:
    repo = AttendanceElasticRepository()
    events = repo.recent_events(minutes=minutes, size=size, sort_order='desc')
    return [
        AttendanceEvent(
            timestamp=event.get('@timestamp'),
            event_time=(event.get('hikvision') or {}).get('dateTime'),
            user_id=((event.get('hikvision') or {}).get('AccessControllerEvent') or {}).get('employeeNoString') or (event.get('user') or {}).get('id'),
            user_name=((event.get('hikvision') or {}).get('AccessControllerEvent') or {}).get('name') or (event.get('user') or {}).get('full_name'),
            device_name=((event.get('hikvision') or {}).get('AccessControllerEvent') or {}).get('deviceName'),
            device_id=(event.get('hikvision') or {}).get('deviceID'),
            outcome=(event.get('event') or {}).get('outcome'),
            raw=event,
        )
        for event in events
    ]
