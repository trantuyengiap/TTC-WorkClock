from __future__ import annotations

from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class RoleEnum(str, Enum):
    SUPER_ADMIN = 'super_admin'
    HR_ADMIN = 'hr_admin'
    DEPARTMENT_MANAGER = 'department_manager'
    REPORT_VIEWER = 'report_viewer'


class RuleTypeEnum(str, Enum):
    CHECK_IN = 'check_in_reminder'
    CHECK_OUT = 'check_out_reminder'
    ATTENDANCE_EVENT = 'attendance_event_notice'
    ANOMALY = 'anomaly_alert'


class TargetTypeEnum(str, Enum):
    ALL = 'all'
    DEPARTMENT = 'department'
    USER = 'user'
    GROUP = 'group'


class ChannelTypeEnum(str, Enum):
    VIBER = 'viber'
    EMAIL = 'email'
    TELEGRAM = 'telegram'
    SLACK = 'slack'
    ZALO = 'zalo'


class DeliveryStatusEnum(str, Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    RETRYING = 'retrying'


class Department(BaseModel):
    __tablename__ = 'departments'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list['User']] = relationship(back_populates='department')


class Shift(BaseModel):
    __tablename__ = 'shifts'

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(64), unique=True)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    grace_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_night_shift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_special: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    users: Mapped[list['User']] = relationship(back_populates='shift')


class User(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_code: Mapped[str | None] = mapped_column(String(64), unique=True)
    attendance_code: Mapped[str | None] = mapped_column(String(64), unique=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    title: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default='active', nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum), default=RoleEnum.REPORT_VIEWER, nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey('departments.id'))
    shift_id: Mapped[int | None] = mapped_column(ForeignKey('shifts.id'))
    notification_preferences: Mapped[dict | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped[Department | None] = relationship(back_populates='users')
    shift: Mapped[Shift | None] = relationship(back_populates='users')
    notification_targets: Mapped[list['UserNotificationTarget']] = relationship(back_populates='user')


class NotificationChannel(BaseModel):
    __tablename__ = 'notification_channels'

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    channel_type: Mapped[ChannelTypeEnum] = mapped_column(SqlEnum(ChannelTypeEnum), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    retry_policy: Mapped[dict | None] = mapped_column(JSON)
    fallback_policy: Mapped[dict | None] = mapped_column(JSON)
    rate_limit: Mapped[dict | None] = mapped_column(JSON)


class UserNotificationTarget(BaseModel):
    __tablename__ = 'user_notification_targets'
    __table_args__ = (UniqueConstraint('user_id', 'channel_id', name='uq_user_channel_target'),)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey('notification_channels.id'), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship(back_populates='notification_targets')
    channel: Mapped[NotificationChannel] = relationship()


class NotificationTemplate(BaseModel):
    __tablename__ = 'notification_templates'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    template_type: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_type: Mapped[ChannelTypeEnum | None] = mapped_column(SqlEnum(ChannelTypeEnum))
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ReminderRule(BaseModel):
    __tablename__ = 'reminder_rules'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    rule_type: Mapped[RuleTypeEnum] = mapped_column(SqlEnum(RuleTypeEnum), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    schedule_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    conditions: Mapped[dict | None] = mapped_column(JSON)
    channels: Mapped[list[str] | None] = mapped_column(JSON)
    template_id: Mapped[int | None] = mapped_column(ForeignKey('notification_templates.id'))

    template: Mapped[NotificationTemplate | None] = relationship()
    targets: Mapped[list['ReminderRuleTarget']] = relationship(back_populates='rule')


class ReminderRuleTarget(BaseModel):
    __tablename__ = 'reminder_rule_targets'

    rule_id: Mapped[int] = mapped_column(ForeignKey('reminder_rules.id'), nullable=False)
    target_type: Mapped[TargetTypeEnum] = mapped_column(SqlEnum(TargetTypeEnum), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(64))

    rule: Mapped[ReminderRule] = relationship(back_populates='targets')


class AttendanceJob(BaseModel):
    __tablename__ = 'attendance_jobs'

    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending')
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict | None] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)


class NotificationLog(BaseModel):
    __tablename__ = 'notification_logs'

    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    template_name: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DeliveryStatusEnum] = mapped_column(SqlEnum(DeliveryStatusEnum), nullable=False)
    provider_response: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fallback_channel: Mapped[str | None] = mapped_column(String(50))


class SystemSetting(BaseModel):
    __tablename__ = 'system_settings'

    key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Holiday(BaseModel):
    __tablename__ = 'holidays'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    holiday_date: Mapped[str] = mapped_column(String(10), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(64))
