#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Migrate the database, collect static files
python manage.py migrate
python manage.py collectstatic --noinput

# Run Gunicorn to start the Django web server
exec gunicorn config.wsgi:application --bind 0.0.0.0:8009 --workers 10