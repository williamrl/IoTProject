import pika, json, os, signal, sys, logging, requests, threading
from tkinter import messagebox
from thermostat_gui import *
import login_form

PATH = os.path.dirname(os.path.abspath(__file__))

SESSION_FILE = os.path.join(PATH, "user.session.json")
# Path to the configuration file, defaults to "thermostat001_config.json" if not set in environment variables
CONFIG_PATH = os.getenv("CONFIG_PATH", "thermostat001_config.json")
# Name of the RabbitMQ queue, defaults to "device.thermostat001" if not set in environment variables
QUEUE_NAME = os.getenv("QUEUE_NAME", "device.thermostat001")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to load the device configuration from a JSON file
def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading config: {e}")
        # Return a default configuration if loading fails
        return {"device_id": "unknown", "settings": {}}

# Function to save the device configuration to a JSON file
def save_config(config):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def is_logged_in():
    return os.path.exists(SESSION_FILE)

def get_stored_user_id():
    if is_logged_in():
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get("user_id")
    return None

def save_user_session(user_id):
    with open(SESSION_FILE, 'w') as f:
        json.dump({"user_id": user_id}, f)

def register_device(account_id):
    requests.post('http://127.0.0.1:5000/register_device', {'user_id':account_id, 'device_id':QUEUE_NAME})

# Callback function to handle incoming messages from the RabbitMQ queue
def handle_message(ch, method, properties, body):
    # Load the current configuration
    config = load_config()
    # Parse the incoming message
    message = json.loads(body.decode())
    msg_type = message.get("msg_type")

    # Handle "get_info" message type
    if msg_type == "get_info":
        send_response(config)
        logger.info(f"Device Info: {json.dumps(config, indent=2)}")

    # Handle "update" message type
    elif msg_type == "update":
        # Update the configuration settings
        settings = message.get("settings", {})
        config["settings"].update(settings)
        save_config(config)
        logger.info(f"[{config['device_id']}] Settings updated: {settings}")

    # Acknowledge the message to RabbitMQ
    ch.basic_ack(delivery_tag=method.delivery_tag)

def send_response(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='reply.device.status')
    channel.basic_publish(
        exchange='',
        routing_key='reply.device.status',
        body=json.dumps(data)
    )
    connection.close()
    
# Function to handle graceful shutdown on SIGINT (Ctrl+C)
def graceful_shutdown(signal, frame):
    logger.info("Shutting down...")
    # Stop consuming messages and close the connection
    channel.stop_consuming()
    connection.close()
    sys.exit(0)

def start_listening():
    logger.info(f"[{QUEUE_NAME}] Listening for messages...")
    channel.start_consuming()

try:
    # Register the graceful shutdown function for SIGINT
    signal.signal(signal.SIGINT, graceful_shutdown)

    # Establish a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # Declare the queue to ensure it exists
    channel.queue_declare(queue=QUEUE_NAME)
    # Set QoS to process one message at a time
    channel.basic_qos(prefetch_count=1)
    # Set up the consumer with the message handling callback
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)

    if is_logged_in():
        user_id = get_stored_user_id()
        register_device(user_id)
    else:
        requests.get('http://localhost:5000', timeout=2)
        login_form.login_gui(SESSION_FILE, QUEUE_NAME)
    offline = False
except Exception:
    messagebox.showerror("Unable to connect to Smart Home", "Please check your connection, for now we will continue in offline mode.")
    offline = True

if not offline:
    listening_thread = threading.Thread(target=start_listening, daemon=True)
    listening_thread.start()

root.deiconify()
root.mainloop()