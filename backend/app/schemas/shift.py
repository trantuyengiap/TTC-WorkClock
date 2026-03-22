from pydantic import BaseModel

from app.schemas.common import TimestampedResponse


class ShiftBase(BaseModel):
    name: str
    code: str | None = None
    start_time: str
    end_time: str
    grace_minutes: int = 0
    is_night_shift: bool = False
    is_special: bool = False
    notes: str | None = None


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(ShiftBase):
    pass


class ShiftResponse(TimestampedResponse, ShiftBase):
    pass
