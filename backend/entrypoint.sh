#!/bin/bash
set -e

echo "=== Running init.sql to setup database ==="
PGPASSWORD=digitalthi_password psql -h postgres -U digitalthi -d digitalthi_db -f /app/init.sql

echo "=== Database initialized, starting application ==="
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
