from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import Department, RoleEnum
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate

router = APIRouter(prefix='/departments', tags=['departments'])


@router.get('', response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> list[Department]:
    return db.query(Department).filter(Department.deleted_at.is_(None)).order_by(Department.name.asc()).all()


@router.post('', response_model=DepartmentResponse)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> Department:
    department = Department(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.put('/{department_id}', response_model=DepartmentResponse)
def update_department(department_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> Department:
    department = db.query(Department).filter(Department.id == department_id, Department.deleted_at.is_(None)).first()
    if not department:
        raise HTTPException(status_code=404, detail='Department not found')
    for key, value in payload.model_dump().items():
        setattr(department, key, value)
    db.commit()
    db.refresh(department)
    return department
