#!/bin/bash

echo "===== RUNNING STARTUP.SH =====" >> /home/LogFiles/startup.log
echo "Running from $(pwd)" >> /home/LogFiles/startup.log

# Extract tarball if it exists
if [ -f /home/site/wwwroot/output.tar.gz ]; then
  echo "Extracting output.tar.gz..." >> /home/LogFiles/startup.log
  tar -xzf /home/site/wwwroot/output.tar.gz -C /home/site/wwwroot >> /home/LogFiles/startup.log 2>&1
  echo "Removing tarball..." >> /home/LogFiles/startup.log
  rm /home/site/wwwroot/output.tar.gz
else
  echo "No output.tar.gz found." >> /home/LogFiles/startup.log
fi

# Attempt to use system-wide pip3 and python3
echo "Installing packages from requirements.txt..." >> /home/LogFiles/startup.log
python3 -m pip install --upgrade pip >> /home/LogFiles/startup.log 2>&1
python3 -m pip install -r /home/site/wwwroot/requirements.txt >> /home/LogFiles/startup.log 2>&1

# Launch Gunicorn
echo "Starting Gunicorn..." >> /home/LogFiles/startup.log
exec gunicorn app.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind=0.0.0.0:8000 >> /home/LogFiles/startup.log 2>&1