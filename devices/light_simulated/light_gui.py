import tkinter as tk
import json
import os

SESSION_FILE = "user.session.json"
CONFIG_PATH = os.getenv("CONFIG_PATH", "light001_config.json")

def get_logged_in_user():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get("user_id")
    return None

def load_light_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"device_id": "light001", "settings": {}}

def save_light_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        # Load light001 configuration
        self.light_config = load_light_config()

         # Display the logged-in user
        user_id = get_logged_in_user()
        self.user_label = tk.Label(self, text=f"User: {user_id}", font=("Arial", 10, "italic"))
        self.user_label.pack(pady=10)

        # Display light001 settings
        self.light_label = tk.Label(self, text=f"Light ID: {self.light_config['device_id']}", font=("Arial", 12, "bold"))
        self.light_label.pack(pady=5)

        self.brightness_label = tk.Label(self, text=f"Brightness: {self.light_config['settings'].get('brightness', 'N/A')}")
        self.brightness_label.pack()

        self.color_label = tk.Label(self, text=f"Color: {self.light_config['settings'].get('color', 'N/A')}")
        self.color_label.pack()

        self.status_label = tk.Label(self, text=f"Status: {self.light_config['settings'].get('status', 'N/A')}")
        self.status_label.pack()

        # Add controls to update brightness
        self.brightness_slider = tk.Scale(self, from_=0, to=100, orient="horizontal", label="Brightness")
        self.brightness_slider.set(self.light_config['settings'].get('brightness', 0))
        self.brightness_slider.pack()

        self.update_button = tk.Button(self, text="Update Settings", command=self.update_settings)
        self.update_button.pack(pady=10)

    def update_settings(self):
        # Update brightness in the configuration
        self.light_config['settings']['brightness'] = self.brightness_slider.get()
        save_light_config(self.light_config)

        # Update the displayed brightness
        self.brightness_label.config(text=f"Brightness: {self.light_config['settings']['brightness']}")
        print(f"Updated light001 settings: {self.light_config['settings']}")

def start_gui():
    root = tk.Tk()
    root.title("Light001 Control Panel")
    myapp = App(root)
    myapp.mainloop()