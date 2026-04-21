#!/bin/bash
set -e
echo "=== Zimplixio: running migrate ==="
/app/.venv/bin/python /app/Zimplixio_site/manage.py migrate --noinput
echo "=== Zimplixio: starting gunicorn ==="
exec /app/.venv/bin/gunicorn --chdir /app/Zimplixio_site Zimplixio_site.wsgi:application --bind 0.0.0.0:$PORT --workers 2
