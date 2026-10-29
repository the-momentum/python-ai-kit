#!/bin/bash
set +x
set -e

uv run celery -A app.main:celery_app worker --loglevel=info
