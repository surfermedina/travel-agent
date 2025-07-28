"""
logger.py

Provides a reusable logger for the banking agent system.
Logs to both console and a file named per session.
Writes to /logs locally or /home/LogFiles/app_logs on Azure.
"""

import logging
import os
from datetime import datetime

def determine_log_dir() -> str:
    azure_log_dir = "/home/LogFiles/app_logs"
    local_log_dir = "logs"

    # More reliable check for Azure App Service
    if os.environ.get("WEBSITE_SITE_NAME"):
        os.makedirs(azure_log_dir, exist_ok=True)
        return azure_log_dir
    else:
        os.makedirs(local_log_dir, exist_ok=True)
        return local_log_dir

def get_logger(name: str = "banking_agent") -> logging.Logger:
    log_dir = determine_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(log_dir, f"session_{timestamp}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_format)

        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
