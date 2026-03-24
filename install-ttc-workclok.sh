#!/usr/bin/env bash
set -Eeuo pipefail

APP_USER="${APP_USER:-ttc-workclock}"
APP_GROUP="${APP_GROUP:-$APP_USER}"
APP_DIR="${APP_DIR:-/opt/ttc-workclock}"
WEB_ROOT="${WEB_ROOT:-/var/www/ttc-workclock}"
DOMAIN="${DOMAIN:-_}"
NODE_MAJOR="${NODE_MAJOR:-22}"
POSTGRES_DB="${POSTGRES_DB:-workclock}"
POSTGRES_USER="${POSTGRES_USER:-workclock}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-workclock}"
APP_SECRET_KEY="${APP_SECRET_KEY:-}"
DEFAULT_ADMIN_USERNAME="${DEFAULT_ADMIN_USERNAME:-admin}"
DEFAULT_ADMIN_PASSWORD="${DEFAULT_ADMIN_PASSWORD:-}"
DEFAULT_ADMIN_EMAIL="${DEFAULT_ADMIN_EMAIL:-admin@example.com}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
ELASTICSEARCH_URL="${ELASTICSEARCH_URL:-http://localhost:9200}"
SMTP_HOST="${SMTP_HOST:-localhost}"
SMTP_PORT="${SMTP_PORT:-25}"
SMTP_USERNAME="${SMTP_USERNAME:-}"
SMTP_PASSWORD="${SMTP_PASSWORD:-}"
SMTP_FROM="${SMTP_FROM:-info@ttcdanghuynh.vn}"
VIBER_BASE_URL="${VIBER_BASE_URL:-http://127.0.0.1:8080}"
VIBER_SEND_ENDPOINT="${VIBER_SEND_ENDPOINT:-/viber/send}"
VIBER_TOKEN="${VIBER_TOKEN:-}"
BACKEND_CORS_ORIGINS="${BACKEND_CORS_ORIGINS:-http://localhost,http://127.0.0.1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR"

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

fail() {
  printf '\n[ERROR] %s\n' "$*" >&2
  exit 1
}

need_root() {
  if [ "${EUID}" -ne 0 ]; then
    fail "Vui lòng chạy script bằng root hoặc sudo."
  fi
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

version_ge() {
  dpkg --compare-versions "$1" ge "$2"
}

ensure_source_tree() {
  [ -d "$SOURCE_DIR/backend" ] || fail "Không tìm thấy thư mục backend trong $SOURCE_DIR"
  [ -d "$SOURCE_DIR/frontend" ] || fail "Không tìm thấy thư mục frontend trong $SOURCE_DIR"
}

install_base_packages() {
  log "Cài các gói nền tảng"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y \
    ca-certificates curl gnupg rsync unzip git build-essential pkg-config \
    python3 python3-venv python3-pip libpq-dev \
    postgresql redis-server nginx
}

install_node_if_needed() {
  local install_node=0
  if ! command_exists node; then
    install_node=1
  else
    local current
    current="$(node -v | sed 's/^v//')"
    if ! version_ge "$current" "20.19.0"; then
      install_node=1
    fi
  fi

  if [ "$install_node" -eq 1 ]; then
    log "Cài Node.js ${NODE_MAJOR}.x vì frontend dùng Vite 7 yêu cầu Node >= 20.19"
    curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash -
    apt-get install -y nodejs
  else
    log "Node.js hiện tại đã đạt yêu cầu: $(node -v)"
  fi
}

create_app_user() {
  if ! getent group "$APP_GROUP" >/dev/null 2>&1; then
    groupadd --system "$APP_GROUP"
  fi
  if ! id -u "$APP_USER" >/dev/null 2>&1; then
    useradd --system --gid "$APP_GROUP" --home-dir "$APP_DIR" --create-home --shell /usr/sbin/nologin "$APP_USER"
  fi
}

sync_source() {
  log "Đồng bộ source vào $APP_DIR"
  mkdir -p "$APP_DIR"
  rsync -a --delete \
    --exclude '.git' \
    --exclude '.github' \
    --exclude 'node_modules' \
    --exclude 'dist' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    "$SOURCE_DIR/" "$APP_DIR/"
  chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"
}

generate_secret_if_needed() {
  if [ -z "$APP_SECRET_KEY" ]; then
    APP_SECRET_KEY="$(openssl rand -hex 32)"
  fi
  if [ -z "$DEFAULT_ADMIN_PASSWORD" ]; then
    DEFAULT_ADMIN_PASSWORD="$(openssl rand -base64 18 | tr -d '=+/\n' | cut -c1-16)"
  fi
}

write_env_file() {
  local env_file="$APP_DIR/.env"
  if [ ! -f "$env_file" ]; then
    log "Tạo file môi trường $env_file"
    cp "$APP_DIR/.env.debian12.example" "$env_file"
  else
    log "Giữ nguyên file môi trường hiện có: $env_file"
  fi

  python3 - "$env_file" <<PY
from pathlib import Path
import sys

path = Path(sys.argv[1])
updates = {
    'APP_ENV': 'production',
    'APP_SECRET_KEY': '''$APP_SECRET_KEY''',
    'BACKEND_CORS_ORIGINS': '''$BACKEND_CORS_ORIGINS''',
    'DATABASE_URL': 'postgresql+psycopg://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB',
    'REDIS_URL': 'redis://localhost:6379/0',
    'CELERY_BROKER_URL': 'redis://localhost:6379/1',
    'CELERY_RESULT_BACKEND': 'redis://localhost:6379/2',
    'ELASTICSEARCH_URL': '''$ELASTICSEARCH_URL''',
    'SMTP_HOST': '''$SMTP_HOST''',
    'SMTP_PORT': '''$SMTP_PORT''',
    'SMTP_USERNAME': '''$SMTP_USERNAME''',
    'SMTP_PASSWORD': '''$SMTP_PASSWORD''',
    'SMTP_FROM': '''$SMTP_FROM''',
    'VIBER_BASE_URL': '''$VIBER_BASE_URL''',
    'VIBER_SEND_ENDPOINT': '''$VIBER_SEND_ENDPOINT''',
    'VIBER_TOKEN': '''$VIBER_TOKEN''',
    'DEFAULT_ADMIN_USERNAME': '''$DEFAULT_ADMIN_USERNAME''',
    'DEFAULT_ADMIN_PASSWORD': '''$DEFAULT_ADMIN_PASSWORD''',
    'DEFAULT_ADMIN_EMAIL': '''$DEFAULT_ADMIN_EMAIL''',
}
lines = []
existing = {}
for raw in path.read_text(encoding='utf-8').splitlines():
    if '=' in raw and not raw.lstrip().startswith('#'):
        k, v = raw.split('=', 1)
        existing[k] = v
for k, v in updates.items():
    existing[k] = v
for raw in path.read_text(encoding='utf-8').splitlines():
    if '=' in raw and not raw.lstrip().startswith('#'):
        k, _ = raw.split('=', 1)
        if k in existing:
            lines.append(f'{k}={existing.pop(k)}')
        else:
            lines.append(raw)
    else:
        lines.append(raw)
for k, v in existing.items():
    if not any(line.startswith(f'{k}=') for line in lines):
        lines.append(f'{k}={v}')
path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY

  ln -sf ../.env "$APP_DIR/backend/.env"
  chown -h "$APP_USER:$APP_GROUP" "$APP_DIR/backend/.env"
  chmod 640 "$env_file"
}

setup_postgres() {
  log "Khởi động PostgreSQL và Redis"
  systemctl enable --now postgresql redis-server

  local db_exists role_exists
  role_exists="$(runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'")"
  if [ "$role_exists" != "1" ]; then
    runuser -u postgres -- psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
  fi

  db_exists="$(runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'")"
  if [ "$db_exists" != "1" ]; then
    runuser -u postgres -- psql -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};"
  fi

  runuser -u postgres -- psql -c "ALTER USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';" >/dev/null
  runuser -u postgres -- psql -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};" >/dev/null
}

run_as_app_user() {
  runuser -u "$APP_USER" -- bash -lc "$*"
}

install_backend() {
  log "Cài backend Python"
  run_as_app_user "cd '$APP_DIR/backend' && python3 -m venv .venv"
  run_as_app_user "cd '$APP_DIR/backend' && .venv/bin/pip install --upgrade pip setuptools wheel"
  run_as_app_user "cd '$APP_DIR/backend' && . ../.env && export \
    APP_NAME APP_ENV APP_SECRET_KEY APP_ACCESS_TOKEN_EXPIRE_MINUTES APP_TIMEZONE API_V1_PREFIX BACKEND_CORS_ORIGINS \
    DATABASE_URL REDIS_URL CELERY_BROKER_URL CELERY_RESULT_BACKEND ELASTICSEARCH_URL ELASTICSEARCH_USERNAME ELASTICSEARCH_PASSWORD \
    ELASTICSEARCH_INDEX_PATTERN ELASTICSEARCH_VERIFY_CERTS ELASTICSEARCH_REQUEST_TIMEOUT ES_FIELD_TIMESTAMP ES_FIELD_EVENT_TIME \
    ES_FIELD_USER_ID ES_FIELD_USER_NAME ES_FIELD_DEVICE_NAME ES_FIELD_DEVICE_ID SMTP_HOST SMTP_PORT SMTP_USERNAME SMTP_PASSWORD SMTP_FROM \
    VIBER_BASE_URL VIBER_SEND_ENDPOINT VIBER_TOKEN DEFAULT_ADMIN_USERNAME DEFAULT_ADMIN_PASSWORD DEFAULT_ADMIN_EMAIL && \
    .venv/bin/pip install -r requirements.txt && \
    .venv/bin/alembic upgrade head && \
    .venv/bin/python -m app.seed"
}

build_frontend() {
  log "Build frontend React"
  mkdir -p "$WEB_ROOT"
  run_as_app_user "cd '$APP_DIR/frontend' && npm install && VITE_API_BASE_URL='/api/v1' npm run build"
  rsync -a --delete "$APP_DIR/frontend/dist/" "$WEB_ROOT/"
  chown -R www-data:www-data "$WEB_ROOT"
}

write_systemd_units() {
  log "Cài systemd service"
  cp "$APP_DIR/deploy/systemd/ttc-workclock-api.service" /etc/systemd/system/ttc-workclock-api.service
  cp "$APP_DIR/deploy/systemd/ttc-workclock-worker.service" /etc/systemd/system/ttc-workclock-worker.service
  cp "$APP_DIR/deploy/systemd/ttc-workclock-beat.service" /etc/systemd/system/ttc-workclock-beat.service
  sed -i "s#/opt/ttc-workclock#$APP_DIR#g; s#User=ttc-workclock#User=$APP_USER#g; s#Group=ttc-workclock#Group=$APP_GROUP#g" /etc/systemd/system/ttc-workclock-*.service
  sed -i "s#--port 8000#--port $BACKEND_PORT#g" /etc/systemd/system/ttc-workclock-api.service
  systemctl daemon-reload
  systemctl enable --now ttc-workclock-api.service ttc-workclock-worker.service ttc-workclock-beat.service
}

configure_nginx() {
  log "Cấu hình Nginx"
  local conf=/etc/nginx/sites-available/ttc-workclock.conf
  cp "$APP_DIR/nginx/workclock.debian12.conf" "$conf"
  sed -i "s#server_name _;#server_name $DOMAIN;#g" "$conf"
  sed -i "s#root /var/www/ttc-workclock;#root $WEB_ROOT;#g" "$conf"
  sed -i "s#127.0.0.1:8000#127.0.0.1:$BACKEND_PORT#g" "$conf"
  ln -sf "$conf" /etc/nginx/sites-enabled/ttc-workclock.conf
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable --now nginx
  systemctl reload nginx
}

print_summary() {
  log "Hoàn tất cài đặt"
  printf 'APP_DIR=%s\n' "$APP_DIR"
  printf 'WEB_ROOT=%s\n' "$WEB_ROOT"
  printf 'Domain=%s\n' "$DOMAIN"
  printf 'Backend health: http://127.0.0.1:%s/health\n' "$BACKEND_PORT"
  printf 'Admin username: %s\n' "$DEFAULT_ADMIN_USERNAME"
  printf 'Admin password: %s\n' "$DEFAULT_ADMIN_PASSWORD"
  printf 'Lưu ý: hãy chỉnh ELASTICSEARCH_URL/SMTP/VIBER trong %s nếu đang dùng dịch vụ ngoài máy cục bộ.\n' "$APP_DIR/.env"
}

main() {
  need_root
  ensure_source_tree
  generate_secret_if_needed
  install_base_packages
  install_node_if_needed
  create_app_user
  sync_source
  write_env_file
  setup_postgres
  install_backend
  build_frontend
  write_systemd_units
  configure_nginx
  print_summary
}

main "$@"
