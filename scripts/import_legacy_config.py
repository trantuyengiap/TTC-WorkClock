from __future__ import annotations

import argparse
from pathlib import Path

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import ChannelTypeEnum, Department, NotificationChannel, RoleEnum, SystemSetting, User, UserNotificationTarget


def parse_user_config(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = [item.strip() for item in line.split(',')]
        if len(parts) < 4:
            continue
        rows.append({'attendance_code': parts[0], 'full_name': parts[1], 'viber_id': parts[2], 'mcc_name': parts[3]})
    return rows


def run(user_config: Path, elastic_password_config: Path | None = None) -> None:
    db = SessionLocal()
    try:
        department = db.scalar(select(Department).where(Department.code == 'LEGACY'))
        if not department:
            department = Department(name='Imported Legacy', code='LEGACY', description='Imported from /etc/user-mcc-list.conf')
            db.add(department)
            db.commit()
            db.refresh(department)

        viber_channel = db.scalar(select(NotificationChannel).where(NotificationChannel.channel_type == ChannelTypeEnum.VIBER))
        if not viber_channel:
            viber_channel = NotificationChannel(name='Legacy Viber', channel_type=ChannelTypeEnum.VIBER, config={})
            db.add(viber_channel)
            db.commit()
            db.refresh(viber_channel)

        for row in parse_user_config(user_config):
            username = row['attendance_code'].lower()
            user = db.scalar(select(User).where(User.attendance_code == row['attendance_code']))
            if not user:
                user = User(
                    username=username,
                    hashed_password=get_password_hash('ChangeMe@123'),
                    full_name=row['full_name'],
                    attendance_code=row['attendance_code'],
                    employee_code=row['attendance_code'],
                    title=row['mcc_name'],
                    department_id=department.id,
                    role=RoleEnum.REPORT_VIEWER,
                    is_active=True,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            target = db.scalar(select(UserNotificationTarget).where(UserNotificationTarget.user_id == user.id, UserNotificationTarget.channel_id == viber_channel.id))
            if not target:
                db.add(UserNotificationTarget(user_id=user.id, channel_id=viber_channel.id, recipient=row['viber_id'], is_primary=True, is_enabled=True))
                db.commit()

        if elastic_password_config and elastic_password_config.exists():
            db_setting = db.scalar(select(SystemSetting).where(SystemSetting.key == 'legacy.elasticsearch.password'))
            value = {'password': elastic_password_config.read_text(encoding='utf-8').strip()}
            if not db_setting:
                db.add(SystemSetting(key='legacy.elasticsearch.password', value=value, description='Imported from /etc/elastic_password.config', is_secret=True))
            else:
                db_setting.value = value
            db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user-config', type=Path, required=True)
    parser.add_argument('--elastic-password-config', type=Path)
    args = parser.parse_args()
    run(args.user_config, args.elastic_password_config)
