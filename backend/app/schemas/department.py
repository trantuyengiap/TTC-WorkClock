from pydantic import BaseModel

from app.schemas.common import TimestampedResponse


class DepartmentBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentResponse(TimestampedResponse, DepartmentBase):
    pass
