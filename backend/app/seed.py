from __future__ import annotations

from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import ChannelTypeEnum, Department, NotificationChannel, RoleEnum, Shift, User


def run() -> None:
    db = SessionLocal()
    try:
        if not db.scalar(select(Department).where(Department.code == 'OPS')):
            db.add(Department(name='Vận hành', code='OPS', description='Phòng vận hành'))
        if not db.scalar(select(Shift).where(Shift.code == 'HC')):
            db.add(Shift(name='Hành chính', code='HC', start_time='08:00', end_time='17:00', grace_minutes=10))
        db.commit()

        if not db.scalar(select(NotificationChannel).where(NotificationChannel.name == 'Viber Default')):
            db.add(NotificationChannel(name='Viber Default', channel_type=ChannelTypeEnum.VIBER, config={}))
        if not db.scalar(select(NotificationChannel).where(NotificationChannel.name == 'Email Default')):
            db.add(NotificationChannel(name='Email Default', channel_type=ChannelTypeEnum.EMAIL, config={}))
        db.commit()

        existing_admin = db.scalar(select(User).where(User.username == settings.default_admin_username))
        if not existing_admin:
            department = db.scalar(select(Department).where(Department.code == 'OPS'))
            shift = db.scalar(select(Shift).where(Shift.code == 'HC'))
            admin = User(
                username=settings.default_admin_username,
                hashed_password=get_password_hash(settings.default_admin_password),
                full_name='System Administrator',
                employee_code='ADMIN001',
                attendance_code='ADMIN001',
                email=str(settings.default_admin_email),
                role=RoleEnum.SUPER_ADMIN,
                department_id=department.id if department else None,
                shift_id=shift.id if shift else None,
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    run()
