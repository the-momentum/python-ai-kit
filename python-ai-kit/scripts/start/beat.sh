#!/bin/bash
set +x
set -e

rm -f './celerybeat.pid'
uv run celery -A app.main:celery_app beat -l info
