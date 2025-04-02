from flask_mysqldb import MySQL
import MySQLdb.cursors

def get_device_ids(mysql, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT device_id FROM connections WHERE account_id = {id}")
    connections = cursor.fetchall()
    return connections

def get_device_info(mysql, device_id):
    pass

def register_device(mysql, account_id, device_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM connections WHERE device_id = '{device_id}' AND account_id = '{account_id}'")
    connections = cursor.fetchone()

    if connections:
        return

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"INSERT INTO connections (account_id, device_id) VALUES ('{account_id}', '{device_id}')")
    mysql.connection.commit()
