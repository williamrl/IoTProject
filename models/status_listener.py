import pika
import json

def handle_status(ch, method, properties, body):
    data = json.loads(body)
    print("Received device data:", data)
    # You could also store it in the DB or return it to a user

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='reply.device.status')
channel.basic_consume(queue='reply.device.status', on_message_callback=handle_status, auto_ack=True)

print(" [*] Waiting for device replies...")
channel.start_consuming()
