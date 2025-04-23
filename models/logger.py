import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

class Logger:
    def __init__(self, log_file='logs/system_log.log'):
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.logger = logging.getLogger('SmartHomeLogger')
        self.logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers if logger is reused
        if not self.logger.handlers:
            handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_user_activity(self, user_id, action, status):
       
        message = f"USER | ID: {user_id} | ACTION: {action} | STATUS: {status}"
        self.logger.info(message)

    def log_device_activity(self, device_name, event, user_id=None):
       
        message = f"DEVICE | Name: {device_name} | Event: {event}"
        if user_id:
            message += f" | User ID: {user_id}"
        self.logger.info(message)
