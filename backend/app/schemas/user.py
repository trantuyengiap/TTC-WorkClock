from pydantic import BaseModel, EmailStr

from app.models import RoleEnum
from app.schemas.common import TimestampedResponse


class UserBase(BaseModel):
    username: str
    full_name: str
    employee_code: str | None = None
    attendance_code: str | None = None
    email: EmailStr | None = None
    title: str | None = None
    status: str = 'active'
    role: RoleEnum = RoleEnum.REPORT_VIEWER
    department_id: int | None = None
    shift_id: int | None = None
    notification_preferences: dict | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    employee_code: str | None = None
    attendance_code: str | None = None
    email: EmailStr | None = None
    title: str | None = None
    status: str | None = None
    role: RoleEnum | None = None
    department_id: int | None = None
    shift_id: int | None = None
    notification_preferences: dict | None = None
    is_active: bool | None = None
    password: str | None = None


class UserResponse(TimestampedResponse, UserBase):
    pass
