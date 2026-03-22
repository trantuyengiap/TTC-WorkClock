from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.services.notifications.base import NotificationProvider, NotificationResult


class ViberProvider(NotificationProvider):
    channel = 'viber'

    def send(self, recipient: str, message: str, options: dict[str, Any] | None = None) -> NotificationResult:
        payload = {'receiverId': recipient, 'message': message}
        try:
            response = httpx.post(
                f"{settings.viber_base_url.rstrip('/')}{settings.viber_send_endpoint}",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return NotificationResult(success=True, provider=self.channel, response=response.json())
        except Exception as exc:
            return NotificationResult(success=False, provider=self.channel, error=str(exc))

    def test_connection(self) -> NotificationResult:
        return NotificationResult(success=True, provider=self.channel, response={'base_url': settings.viber_base_url})
