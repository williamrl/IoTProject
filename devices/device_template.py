import pika
import sys
import os
import requests

device_type = ''
topic = ''
owner_id = ''
device_id = ''
server = '127.0.0.1:5000'

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=topic)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def login():
    print(f"To use your {device_type} please login to your account")
    print("Email: ")
    email = input()
    print("Password: ")
    password = input()
    response = requests.post(server + '/login_api', {'email':email, 'password':password})
    if response:
        owner_id = response
        return True
    print("Login failed. Please try again")
    return False

if __name__ == '__main__':
    if topic == '':
        while not login():
            continue
        topic = f"{owner_id}/{device_id}"
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)