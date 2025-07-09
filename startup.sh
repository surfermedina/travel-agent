#!/bin/bash

echo "===== STARTING APP =====" >> /home/LogFiles/startup.log

# Install dependencies
pip install -r /home/site/wwwroot/requirements.txt >> /home/LogFiles/startup.log 2>&1

# Start the app with gunicorn and Uvicorn worker
exec gunicorn app.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind=0.0.0.0:8000 >> /home/LogFiles/startup.log 2>&1
