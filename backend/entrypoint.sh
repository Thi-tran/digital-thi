#!/bin/bash
set -e

echo "=== Running migrations ==="
python3 run_migrations.py up

echo "=== Migrations complete, starting application ==="
uvicorn main:app --host 0.0.0.0 --port 3001 --reload
