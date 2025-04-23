from flask_mysqldb import MySQL
import time
from models.mqtt import *
import MySQLdb.cursors
import os

listening = False

def get_device_ids(mysql, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT device_id FROM connections WHERE account_id = {id}")
    connections = cursor.fetchall()
    return [connection['device_id'] for connection in connections]

def get_device_info(device_id):
    global listening
    if not listening:
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            recieve_messages_thread()
        listening = True

    info_message = {'msg_type': 'get_info'}
    info_message_json = json.dumps(info_message)
    publish_handler(device_id, info_message_json)
    time.sleep(1)
    messages = get_recieved_messages()
    if device_id.split('.')[1] in messages:
        device_info = messages[device_id.split('.')[1]]
        device_info = json.loads(device_info.decode())
        return device_info
    
    return dict()

def get_all_devices_info(mysql, account_id):
    devices_info = []
    device_ids = get_device_ids(mysql, account_id)
    for device in device_ids:
        devices_info.append(get_device_info(device))

    devices = dict()
    for device in devices_info:
        devices[device['device_id']] = device

    return devices

def register_device(mysql, account_id, device_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM connections WHERE device_id = '{device_id}' AND account_id = '{account_id}'")
    connections = cursor.fetchone()

    if connections:
        return
    print("Adding Device:")
    print(device_id)
    print(account_id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"INSERT INTO connections (account_id, device_id) VALUES ('{account_id}', '{device_id}')")
    mysql.connection.commit()

def unregister_device(mysql, account_id, device_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print("Removing Device:")
    print(device_id)
    print(account_id)
    cursor.execute(f"DELETE FROM connections WHERE device_id = '{device_id}' AND account_id = '{account_id}'")
    mysql.connection.commit()