from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_employees: int
    checked_in_today: int
    not_checked_in_today: int
    notifications_sent_today: int
    elasticsearch_status: str
    worker_status: str
    channels_status: dict[str, str]
