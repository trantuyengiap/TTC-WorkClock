from pydantic import BaseModel

from app.models import DeliveryStatusEnum
from app.schemas.common import TimestampedResponse


class NotificationLogResponse(TimestampedResponse):
    user_id: int | None
    channel: str
    recipient: str
    template_name: str | None
    message: str
    status: DeliveryStatusEnum
    provider_response: dict | None
    error_message: str | None
    retry_count: int
    fallback_channel: str | None


class TestNotificationRequest(BaseModel):
    channel: str
    recipient: str
    message: str
