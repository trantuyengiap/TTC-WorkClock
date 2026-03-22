# Hướng dẫn migrate từ hệ thống cũ

## Mục tiêu

Chuyển từ mô hình script + file config + service rời sang hệ thống web quản trị tập trung mà vẫn giữ tương thích với dữ liệu Elasticsearch hiện tại.

## Bước migrate khuyến nghị

1. Sao lưu:
   - `/etc/user-mcc-list.conf`
   - `/etc/elastic_password.config`
   - các file `/etc/default/*` liên quan
2. Khởi động stack mới bằng Docker Compose.
3. Chạy migration database:
   ```bash
   cd backend
   alembic upgrade head
   python -m app.seed
   ```
4. Import cấu hình cũ:
   ```bash
   PYTHONPATH=backend python scripts/import_legacy_config.py \
     --user-config /etc/user-mcc-list.conf \
     --elastic-password-config /etc/elastic_password.config
   ```
5. Tạo reminder rule tương ứng với lịch cũ trong UI hoặc API.
6. Bật kênh Viber và test gửi thử.
7. Cho worker chạy song song với service cũ trong 1-3 ngày.
8. So sánh số sự kiện, số user đã chấm công, và log notification.
9. Tắt dần systemd timer cũ sau khi xác nhận.

## Mapping tương thích Elasticsearch

Repository mặc định đọc các field:

- `@timestamp`
- `hikvision.dateTime`
- `hikvision.deviceID`
- `hikvision.AccessControllerEvent.employeeNoString`
- `hikvision.AccessControllerEvent.name`
- `hikvision.AccessControllerEvent.deviceName`
- `user.id`
- `user.full_name`
- `event.outcome`

Nếu mapping thay đổi, override bằng env hoặc `system_settings` trong giai đoạn tiếp theo.
