from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class NotificationResult:
    success: bool
    provider: str
    response: dict[str, Any] | None = None
    error: str | None = None


class NotificationProvider(ABC):
    channel: str

    @abstractmethod
    def send(self, recipient: str, message: str, options: dict[str, Any] | None = None) -> NotificationResult:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self) -> NotificationResult:
        raise NotImplementedError
