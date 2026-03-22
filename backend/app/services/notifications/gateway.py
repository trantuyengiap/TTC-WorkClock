from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.models import DeliveryStatusEnum, NotificationLog
from app.services.notifications.base import NotificationProvider, NotificationResult
from app.services.notifications.providers.email import EmailProvider
from app.services.notifications.providers.viber import ViberProvider


class NotificationGateway:
    def __init__(self) -> None:
        self.providers: dict[str, NotificationProvider] = {
            'viber': ViberProvider(),
            'email': EmailProvider(),
        }

    def send(self, db: Session, channel: str, recipient: str, message: str, options: dict[str, Any] | None = None, *, user_id: int | None = None, template_name: str | None = None) -> NotificationResult:
        provider = self.providers.get(channel)
        if provider is None:
            result = NotificationResult(success=False, provider=channel, error=f'Unsupported channel: {channel}')
        else:
            result = provider.send(recipient, message, options)

        log = NotificationLog(
            user_id=user_id,
            channel=channel,
            recipient=recipient,
            message=message,
            template_name=template_name,
            status=DeliveryStatusEnum.SUCCESS if result.success else DeliveryStatusEnum.FAILED,
            provider_response=result.response,
            error_message=result.error,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return result

    def test_connection(self, channel: str) -> NotificationResult:
        provider = self.providers.get(channel)
        if provider is None:
            return NotificationResult(success=False, provider=channel, error='Unsupported channel')
        return provider.test_connection()

    def supported_channels(self) -> Iterable[str]:
        return self.providers.keys()
