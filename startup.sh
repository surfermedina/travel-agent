#!/bin/bash

echo "===== RUNNING STARTUP.SH =====" >> /home/LogFiles/startup.log

# Extract app files if tarball exists
if [ -f /home/site/wwwroot/output.tar.gz ]; then
  echo "Extracting app files..." >> /home/LogFiles/startup.log
  tar -xzf /home/site/wwwroot/output.tar.gz -C /home/site/wwwroot
else
  echo "No output.tar.gz found." >> /home/LogFiles/startup.log
fi

# Install dependencies
echo "Installing dependencies..." >> /home/LogFiles/startup.log
pip install -r /home/site/wwwroot/requirements.txt >> /home/LogFiles/startup.log 2>&1

# Start the app
echo "Starting gunicorn..." >> /home/LogFiles/startup.log
exec gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000