release: cd frontend && npm ci && npm run build && cd ../Zimplixio_site && DJANGO_SETTINGS_MODULE=Zimplixio_site.settings.prod python manage.py migrate --noinput && DJANGO_SETTINGS_MODULE=Zimplixio_site.settings.prod python manage.py collectstatic --noinput
web: cd Zimplixio_site && DJANGO_SETTINGS_MODULE=Zimplixio_site.settings.prod gunicorn Zimplixio_site.wsgi --bind 0.0.0.0:$PORT
