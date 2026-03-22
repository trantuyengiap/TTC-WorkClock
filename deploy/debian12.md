# Deploy Debian 12

## Kiến nghị

- Debian 12
- Docker Engine + Docker Compose plugin
- Nginx
- SSL qua Let's Encrypt hoặc reverse proxy nội bộ

## Các bước

1. Cài Docker và Compose plugin.
2. Clone source vào `/opt/ttc-workclock`.
3. Tạo `.env` production từ `.env.example`.
4. Chỉnh `DATABASE_URL`, `REDIS_URL`, `ELASTICSEARCH_URL`, SMTP, `APP_SECRET_KEY`.
5. Chạy:
   ```bash
   docker compose up -d --build
   ```
6. Cấu hình Nginx dùng `nginx/workclock.conf`.
7. Bật firewall cho 80/443 nếu cần.
8. Kiểm tra:
   - `curl http://127.0.0.1:8000/health`
   - truy cập web UI
   - thử gửi test notification

## Gợi ý hardening

- Đặt Postgres/Redis không expose public nếu không cần.
- Giới hạn quyền file `.env`.
- Cấu hình backup cho volume Postgres.
