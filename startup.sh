#!/bin/bash

# Log startup steps
echo "===== RUNNING STARTUP.SH =====" >> /home/LogFiles/startup.log

# Install dependencies
echo "Installing pip and requirements..." >> /home/LogFiles/startup.log
python3 -m pip install --upgrade pip >> /home/LogFiles/startup.log 2>&1
pip install -r /home/site/wwwroot/requirements.txt >> /home/LogFiles/startup.log 2>&1

# Launch app with Gunicorn + UvicornWorker
echo "Starting Gunicorn..." >> /home/LogFiles/startup.log
exec gunicorn app.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind=0.0.0.0:8000 >> /home/LogFiles/startup.log 2>&1
