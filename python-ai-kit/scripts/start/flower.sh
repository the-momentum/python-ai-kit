#!/bin/bash
set +x
set -e

worker_ready() {
    uv run celery -A app.main:celery_app inspect ping
}

until worker_ready; do
  echo 'Celery workers not available...'
  sleep 1
done
echo 'Celery workers are available, proceeding...'

uv run celery --app=app.main:celery_app flower
