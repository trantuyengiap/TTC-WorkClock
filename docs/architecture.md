# Kiến trúc TTC WorkClock Admin

## 1. Phân tích ngắn hệ thống cũ và vấn đề hiện tại

Hệ thống cũ hoạt động tốt ở mức tác vụ đơn lẻ nhưng gặp các điểm nghẽn chính:

- Cấu hình phân tán trong file text, khó phân quyền và khó audit.
- Timer và lịch nhắc hard-code trong service, khó mở rộng thêm nhiều rule và nhiều ca.
- Logic truy vấn Elasticsearch và logic gửi Viber nằm rải rác, khó tái sử dụng.
- Không có web UI quản trị tập trung, khó vận hành và bàn giao.
- Khó mở rộng đa kênh thông báo vì logic provider đang viết cứng cho Viber.

## 2. Kiến trúc đề xuất

### Thành phần chính

1. **FastAPI Backend**
   - Auth + RBAC.
   - CRUD users, departments, shifts, reminder rules.
   - REST API cho frontend và tích hợp ngoài.
   - Repository truy vấn Elasticsearch tương thích `hikvision-*`.
   - Notification gateway theo adapter/provider.
   - Audit log, notification log, system settings.

2. **React Admin Frontend**
   - Dashboard tổng quan.
   - Các màn hình CRUD quản trị.
   - Trang realtime attendance và notification history.
   - Trang hướng dẫn sử dụng trực tiếp trong website.

3. **PostgreSQL**
   - Lưu toàn bộ cấu hình, người dùng, rule nhắc, log gửi, audit.

4. **Redis + Celery Worker/Beat**
   - Quét event mới 15 giây/lần.
   - Đánh giá rule nhắc theo cấu hình động từ DB.
   - Retry task và mở rộng báo cáo định kỳ.

5. **Elasticsearch Adapter Layer**
   - Chỉ một nơi quản lý query `hikvision-*`.
   - Hỗ trợ field mapping động qua settings/env.
   - Có fallback query khi aggregation lỗi.

6. **Notification Gateway**
   - `send(channel, recipient, message, options)`.
   - Provider độc lập cho Viber, Email; mở rộng Telegram/Slack/Zalo sau.
   - Ghi log, retry/fallback mở rộng theo policy.

### Luồng dữ liệu giữ tương thích

`Hikvision -> Logstash -> Elasticsearch(hikvision-*) -> FastAPI/Celery -> Notification Gateway -> Viber/Email/...`

Logstash hiện tại **không cần thay đổi ngay**.

## 3. Cây thư mục dự án

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── elasticsearch/
│   │   │   ├── notifications/
│   │   │   └── scheduler/
│   │   ├── utils/
│   │   ├── main.py
│   │   └── seed.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── router/
│   │   └── types/
│   └── Dockerfile
├── scripts/
├── docs/
├── deploy/
├── nginx/
├── docker-compose.yml
└── README.md
```

## 4. Thiết kế database

### Bảng chính

- `users`: tài khoản đăng nhập + thông tin nhân sự + mapping attendance code.
- `departments`: phòng ban.
- `shifts`: ca làm việc.
- `notification_channels`: cấu hình channel/provider.
- `user_notification_targets`: đích nhận thông báo của từng user.
- `notification_templates`: mẫu tin nhắn.
- `reminder_rules`: rule nhắc chấm công.
- `reminder_rule_targets`: đối tượng áp dụng rule.
- `attendance_jobs`: log các background job.
- `notification_logs`: lịch sử gửi.
- `system_settings`: cấu hình hệ thống và field mapping.
- `holidays`: ngày nghỉ/lễ.
- `audit_logs`: nhật ký thay đổi cấu hình.

### Ghi chú schema

- Tất cả bảng có `id`, `created_at`, `updated_at`, `deleted_at`.
- Soft delete áp dụng cho dữ liệu quản trị.
- `attendance_code` dùng để map với `hikvision.AccessControllerEvent.employeeNoString`.
- `notification_channels.config` lưu token/webhook hoặc config riêng từng provider.
- `reminder_rules.schedule_config` lưu JSON động để thay thế timer hard-code.

## 5. Danh sách API backend

### Auth
- `POST /api/v1/auth/login`

### Dashboard
- `GET /api/v1/dashboard/stats`

### Departments
- `GET /api/v1/departments`
- `POST /api/v1/departments`
- `PUT /api/v1/departments/{id}`

### Shifts
- `GET /api/v1/shifts`
- `POST /api/v1/shifts`
- `PUT /api/v1/shifts/{id}`

### Users
- `GET /api/v1/users`
- `POST /api/v1/users`
- `PUT /api/v1/users/{id}`

### Reminder rules
- `GET /api/v1/reminder-rules`
- `POST /api/v1/reminder-rules`
- `PUT /api/v1/reminder-rules/{id}`

### Attendance / Elasticsearch
- `GET /api/v1/attendance/events`

### Notifications
- `GET /api/v1/notifications/logs`
- `GET /api/v1/notifications/channels`
- `POST /api/v1/notifications/test`

### System settings
- `GET /api/v1/settings/system`
- `POST /api/v1/settings/resync-rules`

## 6. Luồng nghiệp vụ chính

### 6.1. Realtime event notice
1. Worker quét Elasticsearch 15 giây/lần.
2. Event được chuẩn hóa bởi repository adapter.
3. Áp rule loại `attendance_event_notice`.
4. Render template theo user + device + time.
5. Gửi qua notification gateway.
6. Ghi `notification_logs` và `attendance_jobs`.

### 6.2. Reminder chưa chấm công
1. Beat kích hoạt task đánh giá rule.
2. Rule đọc `schedule_config`, `conditions`, `targets` từ PostgreSQL.
3. Repository truy vấn user đã chấm công trong time window.
4. User chưa chấm công được chọn theo phòng ban / user / toàn bộ.
5. Gateway gửi theo ưu tiên kênh.
6. Log kết quả, retry/fallback ở worker.

### 6.3. Quản trị cấu hình
1. Admin đăng nhập qua JWT.
2. Thay đổi user/shift/rule/channel trên website.
3. Backend lưu DB.
4. Audit log ghi nhận tác nhân và payload thay đổi.
5. Worker đọc cấu hình mới mà không cần sửa file text.

## 7. Kế hoạch migration từ hệ thống cũ

1. **Giữ nguyên Logstash và Elasticsearch** để không đụng luồng ingest Hikvision.
2. Import `/etc/user-mcc-list.conf` vào `users` + `user_notification_targets` bằng script `scripts/import_legacy_config.py`.
3. Import `/etc/elastic_password.config` vào `system_settings` hoặc chuyển thành env secret.
4. Tạo rule Phase 1 tương đương timer cũ:
   - sáng 07:50, 07:54
   - chiều 17:10, 17:20, 17:30, 17:40
5. Chạy song song hệ cũ và hệ mới một giai đoạn ngắn.
6. Đối chiếu notification logs giữa 2 hệ thống.
7. Khi xác nhận đúng, tắt systemd timer cũ.

## 8. Docker/dev/prod setup

### Local / Windows dev
- Dùng Docker Desktop + `docker compose up --build`.
- Frontend chạy trên Vite, backend trên Uvicorn.
- PostgreSQL/Redis/Mailhog chạy container.

### Production Debian 12
- Dùng Docker Compose hoặc systemd + Nginx.
- Reverse proxy bằng `nginx/workclock.conf`.
- Nên cấu hình `.env` riêng cho production và secret manager nếu có.

## 9. Bắt đầu sinh code cho Phase 1

Phase 1 trong repo hiện đã scaffold các phần ưu tiên:

- Auth + RBAC.
- User management.
- Shift management.
- Reminder rules.
- Elasticsearch query module.
- Viber + Email gateway.
- Dashboard cơ bản.
- Notification logs.
- Realtime attendance page.
- Website có trang hướng dẫn sử dụng.

