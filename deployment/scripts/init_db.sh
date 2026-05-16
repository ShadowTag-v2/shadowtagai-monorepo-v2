#!/bin/bash
# Initialize database for Release Manager

set -e

echo "Initializing Release Manager database..."

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DATABASE_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - initializing database"

# Run Alembic migrations
cd /app
alembic upgrade head

echo "Database initialization complete!"
