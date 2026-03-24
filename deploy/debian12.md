# Deploy Debian 12 không dùng Docker

## Mục tiêu

Triển khai TTC WorkClock trực tiếp trên Debian 12 bằng:

- PostgreSQL local
- Redis local
- FastAPI + Uvicorn qua systemd
- Celery worker + beat qua systemd
- Frontend React build tĩnh và phục vụ bằng Nginx

> Lưu ý: frontend đang dùng Vite 7, vì vậy Node.js cần từ `20.19+` hoặc `22.12+`. Debian 12 mặc định đang đóng gói Node.js 18.20.4 nên cần cài Node mới hơn khi build frontend.

## File mới dùng cho Debian 12

- `install-ttc-workclok.sh`
- `.env.debian12.example`
- `nginx/workclock.debian12.conf`
- `deploy/systemd/ttc-workclock-api.service`
- `deploy/systemd/ttc-workclock-worker.service`
- `deploy/systemd/ttc-workclock-beat.service`

## Cài nhanh

Giải nén source rồi chạy:

```bash
chmod +x install-ttc-workclok.sh
sudo ./install-ttc-workclok.sh
```

## Có thể truyền biến môi trường trước khi chạy

```bash
sudo APP_DIR=/opt/ttc-workclock \
DOMAIN=workclock.example.com \
POSTGRES_PASSWORD='MatKhauRieng' \
APP_SECRET_KEY='secret-random' \
DEFAULT_ADMIN_PASSWORD='AdminMoi@123' \
ELASTICSEARCH_URL='http://127.0.0.1:9200' \
SMTP_HOST='127.0.0.1' \
SMTP_PORT='25' \
./install-ttc-workclok.sh
```

## Script sẽ làm gì

1. Cài gói hệ thống cần thiết.
2. Cài Node.js 22 nếu Node hiện tại chưa đạt yêu cầu cho Vite 7.
3. Tạo user hệ thống `ttc-workclock`.
4. Đồng bộ source vào `/opt/ttc-workclock`.
5. Tạo `.env` production từ `.env.debian12.example`.
6. Tạo database PostgreSQL và user ứng dụng.
7. Tạo virtualenv, cài Python dependencies, chạy Alembic và seed dữ liệu.
8. Build frontend React ra thư mục tĩnh `/var/www/ttc-workclock`.
9. Cài 3 service systemd: API, worker, beat.
10. Cài Nginx reverse proxy + phục vụ frontend.

## Service sau khi cài

```bash
systemctl status ttc-workclock-api
systemctl status ttc-workclock-worker
systemctl status ttc-workclock-beat
systemctl status nginx
```

## Log thường dùng

```bash
journalctl -u ttc-workclock-api -f
journalctl -u ttc-workclock-worker -f
journalctl -u ttc-workclock-beat -f
```

## Kiểm tra nhanh

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1/api/v1/auth/login
```

## Các điểm tôi đã chỉnh để phù hợp non-Docker

- Tách file env riêng `.env.debian12.example` dùng `localhost` thay cho hostname container.
- Thêm cấu hình Nginx mới để phục vụ frontend build tĩnh thay vì proxy sang Vite dev server.
- Thêm unit systemd cho backend, worker và beat.
- Thêm script `install-ttc-workclok.sh` để cài trực tiếp trên Debian 12.

## Việc bạn cần rà lại sau cài đặt

- `ELASTICSEARCH_URL`, tài khoản và chứng thư nếu Elasticsearch không nằm cùng máy.
- SMTP/Viber nếu dùng dịch vụ ngoài.
- `BACKEND_CORS_ORIGINS` nếu frontend chạy khác domain.
- Đổi mật khẩu admin seed ngay sau khi đăng nhập lần đầu.
