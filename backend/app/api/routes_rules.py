from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import ReminderRule, ReminderRuleTarget, RoleEnum
from app.schemas.rule import ReminderRuleCreate, ReminderRuleResponse, ReminderRuleUpdate

router = APIRouter(prefix='/reminder-rules', tags=['reminder-rules'])


@router.get('', response_model=list[ReminderRuleResponse])
def list_rules(db: Session = Depends(get_db), _: object = Depends(get_current_user)) -> list[ReminderRule]:
    return db.query(ReminderRule).filter(ReminderRule.deleted_at.is_(None)).all()


@router.post('', response_model=ReminderRuleResponse)
def create_rule(payload: ReminderRuleCreate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> ReminderRule:
    targets = payload.targets
    rule = ReminderRule(**payload.model_dump(exclude={'targets'}))
    db.add(rule)
    db.flush()
    for target in targets:
        db.add(ReminderRuleTarget(rule_id=rule.id, **target.model_dump()))
    db.commit()
    db.refresh(rule)
    return rule


@router.put('/{rule_id}', response_model=ReminderRuleResponse)
def update_rule(rule_id: int, payload: ReminderRuleUpdate, db: Session = Depends(get_db), _: object = Depends(require_roles(RoleEnum.SUPER_ADMIN, RoleEnum.HR_ADMIN))) -> ReminderRule:
    rule = db.query(ReminderRule).filter(ReminderRule.id == rule_id, ReminderRule.deleted_at.is_(None)).first()
    if not rule:
        raise HTTPException(status_code=404, detail='Rule not found')
    for key, value in payload.model_dump(exclude={'targets'}).items():
        setattr(rule, key, value)
    db.query(ReminderRuleTarget).filter(ReminderRuleTarget.rule_id == rule.id).delete()
    for target in payload.targets:
        db.add(ReminderRuleTarget(rule_id=rule.id, **target.model_dump()))
    db.commit()
    db.refresh(rule)
    return rule
