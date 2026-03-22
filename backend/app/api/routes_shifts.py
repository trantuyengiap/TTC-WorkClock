from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import RoleEnum, Shift
from app.schemas.shift import ShiftCreate, ShiftResponse, ShiftUpdate

router = APIRouter(prefix='/shifts', tags=['shifts'])


@router.get('', response_model=list[ShiftResponse])
def list_shifts(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> list[Shift]:
    return db.query(Shift).filter(Shift.deleted_at.is_(None)).order_by(Shift.name.asc()).all()


@router.post('', response_model=ShiftResponse)
def create_shift(payload: ShiftCreate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> Shift:
    shift = Shift(**payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@router.put('/{shift_id}', response_model=ShiftResponse)
def update_shift(shift_id: int, payload: ShiftUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> Shift:
    shift = db.query(Shift).filter(Shift.id == shift_id, Shift.deleted_at.is_(None)).first()
    if not shift:
        raise HTTPException(status_code=404, detail='Shift not found')
    for key, value in payload.model_dump().items():
        setattr(shift, key, value)
    db.commit()
    db.refresh(shift)
    return shift
