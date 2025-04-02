import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def handle_publish(topic, message):
    channel.queue_declare(queue=topic)
    channel.basic_publish(exchange='', routing_key=topic, body=message)