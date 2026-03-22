from fastapi import APIRouter

from app.api import routes_attendance, routes_auth, routes_dashboard, routes_departments, routes_notifications, routes_rules, routes_settings, routes_shifts, routes_users

api_router = APIRouter()
api_router.include_router(routes_auth.router)
api_router.include_router(routes_dashboard.router)
api_router.include_router(routes_departments.router)
api_router.include_router(routes_shifts.router)
api_router.include_router(routes_users.router)
api_router.include_router(routes_rules.router)
api_router.include_router(routes_attendance.router)
api_router.include_router(routes_notifications.router)
api_router.include_router(routes_settings.router)
