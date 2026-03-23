# TTC WorkClock Admin

Hệ thống web quản trị tập trung cho chấm công, nhắc chấm công và gửi thông báo đa kênh, tương thích dữ liệu Elasticsearch `hikvision-*` hiện có.

## Phase 1 đã có

- FastAPI backend với JWT auth, RBAC, REST API.
- React + Ant Design frontend cho dashboard admin.
- PostgreSQL cho cấu hình và dữ liệu quản trị.
- Redis + Celery worker/beat cho background jobs.
- Elasticsearch repository tập trung, tương thích trường Hikvision hiện tại.
- Notification gateway theo provider cho Viber và Email, sẵn sàng mở rộng Telegram/Slack/Zalo.
- Docker Compose cho local/dev trên Debian 12 và Windows Docker Desktop.
- Script import cấu hình cũ từ `/etc/user-mcc-list.conf` và `/etc/elastic_password.config`.
- Tài liệu kiến trúc, vận hành, migration, deploy.

## Cấu trúc thư mục

```text
backend/   FastAPI, models, migrations, services, tests
frontend/  React admin UI
scripts/   seed dữ liệu, import legacy config
docs/      kiến trúc, migration, vận hành, checklist
deploy/    hướng dẫn deploy Debian 12
nginx/     reverse proxy config
```

## Khởi động nhanh bằng Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Service mặc định:

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- Swagger: <http://localhost:8000/docs>
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Tài khoản seed mặc định

- Username: `admin`
- Password: `Admin@123`

> Đổi mật khẩu ngay sau khi triển khai thực tế.

## Chạy backend local không Docker

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

## Chạy frontend local không Docker

```bash
cd frontend
npm install
npm run dev
```

## Chạy test

```bash
cd backend
pytest
```

## Tài liệu

- Kiến trúc và API: `docs/architecture.md`
- Migration từ hệ thống cũ: `docs/migration-guide.md`
- Vận hành: `docs/operations.md`
- Checklist test: `docs/test-checklist.md`
- Deploy Debian 12: `deploy/debian12.md`
- Script cài Debian 12 không Docker: `install-ttc-workclok.sh`
- Dev trên Windows: `docs/windows-dev.md`

