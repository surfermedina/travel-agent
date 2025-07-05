"""
logger.py

Provides a reusable logger for the banking agent system.
Logs to both console and a file named per session in the /logs directory.
"""

import logging
import os
from datetime import datetime

def get_logger(name: str = "banking_agent") -> logging.Logger:
    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Format the log filename using current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{log_dir}/session_{timestamp}.log"

    # Create logger instance
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers during reloads
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

        # Add both handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
