"""initial schema

Revision ID: 20260319_0001
Revises:
Create Date: 2026-03-19 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '20260319_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    role_enum = sa.Enum(
        'SUPER_ADMIN', 'HR_ADMIN', 'DEPARTMENT_MANAGER', 'REPORT_VIEWER',
        name='roleenum', create_type=False
    )
    rule_type_enum = sa.Enum(
        'CHECK_IN', 'CHECK_OUT', 'ATTENDANCE_EVENT', 'ANOMALY',
        name='ruletypeenum', create_type=False
    )
    target_type_enum = sa.Enum(
        'ALL', 'DEPARTMENT', 'USER', 'GROUP',
        name='targettypeenum', create_type=False
    )
    channel_type_enum = sa.Enum(
        'VIBER', 'EMAIL', 'TELEGRAM', 'SLACK', 'ZALO',
        name='channeltypeenum', create_type=False
    )
    delivery_status_enum = sa.Enum(
        'PENDING', 'SUCCESS', 'FAILED', 'RETRYING',
        name='deliverystatusenum', create_type=False
    )

    bind = op.get_bind()
    sa.Enum(
        'SUPER_ADMIN', 'HR_ADMIN', 'DEPARTMENT_MANAGER', 'REPORT_VIEWER',
        name='roleenum'
    ).create(bind, checkfirst=True)
    sa.Enum(
        'CHECK_IN', 'CHECK_OUT', 'ATTENDANCE_EVENT', 'ANOMALY',
        name='ruletypeenum'
    ).create(bind, checkfirst=True)
    sa.Enum(
        'ALL', 'DEPARTMENT', 'USER', 'GROUP',
        name='targettypeenum'
    ).create(bind, checkfirst=True)
    sa.Enum(
        'VIBER', 'EMAIL', 'TELEGRAM', 'SLACK', 'ZALO',
        name='channeltypeenum'
    ).create(bind, checkfirst=True)
    sa.Enum(
        'PENDING', 'SUCCESS', 'FAILED', 'RETRYING',
        name='deliverystatusenum'
    ).create(bind, checkfirst=True)

    op.create_table(
        'departments',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)

    op.create_table(
        'shifts',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=True),
        sa.Column('start_time', sa.String(length=5), nullable=False),
        sa.Column('end_time', sa.String(length=5), nullable=False),
        sa.Column('grace_minutes', sa.Integer(), nullable=False),
        sa.Column('is_night_shift', sa.Boolean(), nullable=False),
        sa.Column('is_special', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_shifts_id'), 'shifts', ['id'], unique=False)

    op.create_table(
        'notification_channels',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('channel_type', channel_type_enum, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('retry_policy', sa.JSON(), nullable=True),
        sa.Column('fallback_policy', sa.JSON(), nullable=True),
        sa.Column('rate_limit', sa.JSON(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_notification_channels_id'), 'notification_channels', ['id'], unique=False)

    op.create_table(
        'notification_templates',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('template_type', sa.String(length=100), nullable=False),
        sa.Column('channel_type', channel_type_enum, nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_notification_templates_id'), 'notification_templates', ['id'], unique=False)

    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(length=120), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_secret', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
    )
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)

    op.create_table(
        'holidays',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('holiday_date', sa.String(length=10), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_holidays_id'), 'holidays', ['id'], unique=False)

    op.create_table(
        'users',
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('employee_code', sa.String(length=64), nullable=True),
        sa.Column('attendance_code', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('shift_id', sa.Integer(), nullable=True),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.ForeignKeyConstraint(['shift_id'], ['shifts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('attendance_code'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('employee_code'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table(
        'user_notification_targets',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['notification_channels.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'channel_id', name='uq_user_channel_target'),
    )
    op.create_index(op.f('ix_user_notification_targets_id'), 'user_notification_targets', ['id'], unique=False)

    op.create_table(
        'reminder_rules',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', rule_type_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('schedule_config', sa.JSON(), nullable=False),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('channels', sa.JSON(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_reminder_rules_id'), 'reminder_rules', ['id'], unique=False)

    op.create_table(
        'reminder_rule_targets',
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('target_type', target_type_enum, nullable=False),
        sa.Column('target_id', sa.String(length=64), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['reminder_rules.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reminder_rule_targets_id'), 'reminder_rule_targets', ['id'], unique=False)

    op.create_table(
        'attendance_jobs',
        sa.Column('job_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attendance_jobs_id'), 'attendance_jobs', ['id'], unique=False)

    op.create_table(
        'notification_logs',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('template_name', sa.String(length=255), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', delivery_status_enum, nullable=False),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('fallback_channel', sa.String(length=50), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notification_logs_id'), 'notification_logs', ['id'], unique=False)

    op.create_table(
        'audit_logs',
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)


def downgrade() -> None:
    for table in [
        'audit_logs', 'notification_logs', 'attendance_jobs', 'reminder_rule_targets',
        'reminder_rules', 'user_notification_targets', 'users', 'holidays',
        'system_settings', 'notification_templates', 'notification_channels',
        'shifts', 'departments'
    ]:
        op.drop_table(table)

    bind = op.get_bind()
    sa.Enum(name='deliverystatusenum').drop(bind, checkfirst=True)
    sa.Enum(name='channeltypeenum').drop(bind, checkfirst=True)
    sa.Enum(name='targettypeenum').drop(bind, checkfirst=True)
    sa.Enum(name='ruletypeenum').drop(bind, checkfirst=True)
    sa.Enum(name='roleenum').drop(bind, checkfirst=True)
