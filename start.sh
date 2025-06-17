#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DJANGO_DB_PASSWORD psql -h "$DJANGO_DB_HOST" -U "$DJANGO_DB_USER" -d "$DJANGO_DB_NAME" -c "\q" 2>/dev/null; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

python manage.py migrate
python manage.py loaddata fixtures/users.json fixtures/apps.json

# Run tests before starting the server
pytest || { echo "Tests failed. Not starting server."; exit 1; }

exec python manage.py runserver 0.0.0.0:8000
