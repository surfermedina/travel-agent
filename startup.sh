#!/bin/bash

echo "===== RUNNING STARTUP.SH =====" >> /home/LogFiles/startup.log
echo "Running from $(pwd)" >> /home/LogFiles/startup.log
echo "PATH is: $PATH" >> /home/LogFiles/startup.log

# Activate virtual environment
echo "Activating venv..." >> /home/LogFiles/startup.log
source /home/site/wwwroot/antenv/bin/activate >> /home/LogFiles/startup.log 2>&1

# Log gunicorn path
echo "Which gunicorn: $(which gunicorn)" >> /home/LogFiles/startup.log

# Start gunicorn
echo "Starting Gunicorn..." >> /home/LogFiles/startup.log
exec gunicorn main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind=0.0.0.0:8000 >> /home/LogFiles/startup.log 2>&1
