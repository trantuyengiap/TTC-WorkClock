# Tài liệu vận hành

## Luồng vận hành hằng ngày

- Theo dõi Dashboard để kiểm tra Elasticsearch, worker và số cảnh báo.
- Kiểm tra trang Realtime events nếu nghi ngờ máy chấm công chưa đẩy dữ liệu.
- Kiểm tra Notification logs để xem lỗi provider, retry hoặc fallback.

## Các lệnh thường dùng

### Khởi động
```bash
docker compose up -d
```

### Xem log backend
```bash
docker compose logs -f backend
```

### Xem log worker
```bash
docker compose logs -f worker beat
```

### Seed lại dữ liệu mặc định
```bash
docker compose exec backend python -m app.seed
```

### Chạy import legacy config
```bash
docker compose exec backend python /app/../scripts/import_legacy_config.py --user-config /path/to/user-mcc-list.conf
```

## Vận hành an toàn

- Đổi password admin seed ngay sau khi cài đặt.
- Đặt `APP_SECRET_KEY` mạnh cho production.
- Không để plaintext secret trong git.
- Tách `.env` production và giới hạn quyền truy cập.
