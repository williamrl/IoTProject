from device import DeviceManager
from flask import Flask
from flask_mysqldb import MySQL
import paho.mqtt.client as mqtt

# Flask app to access DB
app = Flask(__name__)
app.config[...]  # same config as main.py
mysql = MySQL(app)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    with app.app_context():
        manager = DeviceManager(mysql)

        if topic == "home/livingroom/light":
            if payload == "on":
                manager.turn_on("Living Room Light")
            elif payload == "off":
                manager.turn_off("Living Room Light")
            elif payload.startswith("brightness:"):
                value = int(payload.split(":")[1])
                manager.change_setting("Living Room Light", "brightness", value)

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
client.subscribe("home/livingroom/light")
client.loop_forever()
