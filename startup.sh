#!/bin/bash

# Extract app files if tarball exists
if [ -f /home/site/wwwroot/output.tar.gz ]; then
  echo "Extracting app files..."
  tar -xzf /home/site/wwwroot/output.tar.gz -C /home/site/wwwroot
fi

# Install dependencies
pip install -r /home/site/wwwroot/requirements.txt

# Run FastAPI app
exec gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000