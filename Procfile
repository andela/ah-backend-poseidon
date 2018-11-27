web: gunicorn authors.wsgi
release: python manage.py makemigrations authentication --noinput && python manage.py migrate authentication --noinput
