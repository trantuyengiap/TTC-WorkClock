# Chạy dev/test trên Windows

## Yêu cầu

- Windows 11 hoặc Windows 10 mới.
- Docker Desktop.
- Git.

## Cách chạy

1. Clone repo.
2. Mở PowerShell tại thư mục dự án.
3. Tạo file môi trường:
   ```powershell
   Copy-Item .env.example .env
   ```
4. Khởi động stack:
   ```powershell
   docker compose up --build
   ```
5. Truy cập:
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs

## Chạy test backend

```powershell
docker compose exec backend pytest
```
