release: cd Zimplixio_site && python manage.py migrate --noinput
web: cd Zimplixio_site && gunicorn Zimplixio_site.wsgi --bind 0.0.0.0:$PORT
