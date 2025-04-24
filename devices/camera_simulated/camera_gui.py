import tkinter as tk
import requests
import json
import os
from datetime import datetime

PATH = os.path.dirname(os.path.abspath(__file__))

SESSION_FILE = os.path.join(PATH, "user.session.json")
CONFIG_PATH = os.getenv("CONFIG_PATH", "camera001_config.json")
QUEUE_NAME = os.getenv("QUEUE_NAME", "device.camera001")

def update_device_status():
    enabled = camera_config['settings'].get('enabled', True)


def get_logged_in_user():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get("user_id")
    return None

def load_camera_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {
        "device_id": "camera001",
        "settings": {"enabled": True},
        "alerts": []
    }

def save_camera_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def trigger_alert():
    global camera_config
    print(camera_config['settings']['enabled'])
    if not camera_config['settings'].get('enabled', True):
        status_label.config(text="Camera is disabled. Cannot send alert.")
        return
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_id = get_logged_in_user()
    requests.post('http://127.0.0.1:5000/camera_alert', {'user_id':user_id, 'device_id':QUEUE_NAME})
    status_label.config(text=f"Alert sent at {timestamp}")
    update_device_status()

def toggle_camera():
    global camera_config
    enabled = camera_config['settings'].get('enabled', True)
    camera_config['settings']['enabled'] = not enabled
    save_camera_config(camera_config)

    new_state = "Enabled" if not enabled else "Disabled"
    toggle_button.config(text=f"{'Disable' if not enabled else 'Enable'} Camera")
    status_label.config(text=f"Camera {new_state}")
    update_device_status()
def sync_settings_from_file():
    global camera_config
    try:
        new_config = load_camera_config()
        if new_config['settings'].get('enabled') != camera_config['settings'].get('enabled'):
            camera_config['settings']['enabled'] = new_config['settings'].get('enabled')
            update_device_status()
            toggle_button.config(
                text="Disable Camera" if camera_config['settings'].get('enabled', True) else "Enable Camera"
            )
    except Exception as e:
        print(f"Error syncing settings: {e}")
    
    root.after(1000, sync_settings_from_file)
# Load configuration
camera_config = load_camera_config()
update_device_status()
# GUI setup
root = tk.Tk()
root.geometry("400x300")
root.title("Camera Control")
root.resizable(False, False)

main_frame = tk.Frame(root)
main_frame.pack(expand=True)

toggle_button = tk.Button(main_frame, text='Disable Camera', width=20, height=3, command=toggle_camera)
toggle_button.pack(pady=20)

alert_button = tk.Button(main_frame, text='Trigger Alert', width=20, height=3, command=trigger_alert)
alert_button.pack(pady=20)

user_id = get_logged_in_user()
user_label = tk.Label(main_frame, text=f"User: {user_id}", font=("Arial", 10, "italic"))
user_label.pack(pady=10)

status_label = tk.Label(main_frame, text="Ready", font=("Arial", 10))
status_label.pack()
sync_settings_from_file()


# Uncomment to show window:
# root.mainloop()