from flask_mysqldb import MySQL
import MySQLdb.cursors

def get_device_ids(mysql, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT device_id FROM connections WHERE account_id = {id}")
    connections = cursor.fetchall()
    return connections

def get_device_info(mysql, device_id):
    pass