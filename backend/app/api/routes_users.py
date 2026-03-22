from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models import RoleEnum, User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.get('', response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> list[User]:
    return db.query(User).filter(User.deleted_at.is_(None)).order_by(User.full_name.asc()).all()


@router.post('', response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> User:
    data = payload.model_dump(exclude={'password'})
    user = User(**data, hashed_password=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put('/{user_id}', response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> User:
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    data = payload.model_dump(exclude_unset=True)
    password = data.pop('password', None)
    for key, value in data.items():
        setattr(user, key, value)
    if password:
        user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(user)
    return user
