#!/usr/bin/env bash
set -e

# wait-for utility (simple)
wait_for_postgres() {
  host=$(python - <<PY
import os
print(os.getenv('DATABASE_URL','').split('://')[-1].split('@')[-1].split('/')[0].split(':')[0] if os.getenv('DATABASE_URL') else 'postgres')
PY)
  # simple sleep to wait for postgres startup
  sleep 3
}

case "$1" in
  web|"")
    # run DB migrations/creation
    python - <<PY
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
print('DB init done')
PY
    # run gunicorn
    exec gunicorn -c gunicorn.conf.py app:app
    ;;
  worker)
    exec celery -A tasks.celery worker --loglevel=info -Q default
    ;;
  beat)
    exec celery -A tasks.celery beat --loglevel=info
    ;;
  *)
    exec "$@"
    ;;
esac
