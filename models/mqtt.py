import pika
import threading
import json
import queue

recieved_messages = dict()

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def publish_handler(topic, message):
    channel.queue_declare(queue=topic)
    channel.basic_publish(exchange='', routing_key=topic, body=message)

def get_recieved_messages():
    return recieved_messages

def recieve_messages():
    global recieved_messages
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    queue_name = 'reply.device.status'
    result = channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        body_json = (json.loads(body.decode()))
        recieved_messages[body_json['device_id']] = body

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def recieve_messages_thread():
    consume_thread = threading.Thread(target=recieve_messages, daemon=True)
    consume_thread.start()