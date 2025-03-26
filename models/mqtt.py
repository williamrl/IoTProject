import paho.mqtt.publish as publish

class Broker:
    def connect(session):
        pass

    def handle_publish(topic, message):
        pass

    def handle_disconnect(topic, message):
        pass

    def handle_subscribe(session, request, topic, message):
        pass

    def handle_heartbeet():
        pass

def publish_handler(topic, message):
    publish.single(topic, message, hostname="broker.hivemq.com", port=1883)