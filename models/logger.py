import MySQLdb
from datetime import datetime
from flask_mysqldb import MySQL

class Logger:
    def __init__(self, mysql):
        """Initialize with a MySQL connection instance from Flask."""
        self.mysql = mysql

    def log_user_activity(self, user_id, action, status):
        """
        Logs user activity such as login/logout attempts.
        :param user_id: The user's ID.
        :param action: The action performed (e.g., "login", "logout").
        :param status: The result ("success" or "failure").
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO user_logs (user_id, action, status, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, action, status, timestamp)
        )
        self.mysql.connection.commit()
        cursor.close()

    def log_device_activity(self, device_name, event, user_id=None):
        """
        Logs device activity such as motion detection or security alerts.
        :param device_name: The name of the smart home device.
        :param event: The event description (e.g., "Motion detected in living room").
        :param user_id: (Optional) The user associated with the event.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO device_logs (device_name, event, user_id, timestamp) VALUES (%s, %s, %s, %s)",
            (device_name, event, user_id, timestamp)
        )
        self.mysql.connection.commit()
        cursor.close()
