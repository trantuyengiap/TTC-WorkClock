from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Any

from app.core.config import settings
from app.services.notifications.base import NotificationProvider, NotificationResult


class EmailProvider(NotificationProvider):
    channel = 'email'

    def send(self, recipient: str, message: str, options: dict[str, Any] | None = None) -> NotificationResult:
        try:
            email = EmailMessage()
            email['From'] = settings.smtp_from
            email['To'] = recipient
            email['Subject'] = (options or {}).get('subject', 'Attendance Notification')
            email.set_content(message)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(email)
            return NotificationResult(success=True, provider=self.channel, response={'recipient': recipient})
        except Exception as exc:
            return NotificationResult(success=False, provider=self.channel, error=str(exc))

    def test_connection(self) -> NotificationResult:
        return NotificationResult(success=True, provider=self.channel, response={'host': settings.smtp_host, 'port': settings.smtp_port})
