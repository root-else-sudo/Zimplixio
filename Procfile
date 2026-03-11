release: cd frontend && npm ci && npm run build && cd ../Zimplixio_site && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd Zimplixio_site && gunicorn Zimplixio_site.wsgi --bind 0.0.0.0:$PORT
