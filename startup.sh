#!/bin/bash

LOGFILE=/home/LogFiles/startup.log

echo "===== RUNNING STARTUP.SH =====" >> $LOGFILE
echo "Running from $(pwd)" >> $LOGFILE
echo "PATH is: $PATH" >> $LOGFILE

# Change directory to ensure Python imports app.main properly
echo "Switching to app root..." >> $LOGFILE
cd /home/site/wwwroot >> $LOGFILE 2>&1

# Activate virtual environment
echo "Activating venv..." >> $LOGFILE
source antenv/bin/activate >> $LOGFILE 2>&1

# Log gunicorn path
echo "Which gunicorn: $(which gunicorn)" >> $LOGFILE

# Start gunicorn
echo "Starting Gunicorn..." >> $LOGFILE
exec gunicorn app.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind=0.0.0.0:8000 >> $LOGFILE 2>&1
