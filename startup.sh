#!/bin/bash

echo "===== RUNNING startup.sh ====="
echo "Running from $(pwd)"
echo "Python version: $(python --version)"
echo "Gunicorn location: $(which gunicorn)"

# Optional: Ensure __init__.py exists to treat app/ as a package
touch app/__init__.py

# Launch FastAPI app with gunicorn
exec gunicorn app.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
