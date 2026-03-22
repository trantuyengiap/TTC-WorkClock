from pydantic import BaseModel

from app.models import RuleTypeEnum, TargetTypeEnum
from app.schemas.common import TimestampedResponse


class RuleTarget(BaseModel):
    target_type: TargetTypeEnum
    target_id: str | None = None


class ReminderRuleBase(BaseModel):
    name: str
    rule_type: RuleTypeEnum
    description: str | None = None
    is_active: bool = True
    schedule_config: dict
    conditions: dict | None = None
    channels: list[str] | None = None
    template_id: int | None = None
    targets: list[RuleTarget] = []


class ReminderRuleCreate(ReminderRuleBase):
    pass


class ReminderRuleUpdate(ReminderRuleBase):
    pass


class ReminderRuleResponse(TimestampedResponse, ReminderRuleBase):
    pass
