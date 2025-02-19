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

# Start Django's development server for auto-reloading
exec python manage.py runserver 0.0.0.0:${PORT}