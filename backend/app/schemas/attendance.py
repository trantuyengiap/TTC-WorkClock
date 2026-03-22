from pydantic import BaseModel


class AttendanceEvent(BaseModel):
    timestamp: str | None = None
    event_time: str | None = None
    user_id: str | None = None
    user_name: str | None = None
    device_name: str | None = None
    device_id: str | None = None
    outcome: str | None = None
    raw: dict
