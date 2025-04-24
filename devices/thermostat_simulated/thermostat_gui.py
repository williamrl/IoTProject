import tkinter as tk
import json
import os

PATH = os.path.dirname(os.path.abspath(__file__))

SESSION_FILE = os.path.join(PATH, "user.session.json")
CONFIG_PATH = os.getenv("CONFIG_PATH", "thermostat001_config.json")

def get_logged_in_user():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get("user_id")
    return None

def load_thermostat_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"device_id": "thermostat001", "settings": {"temperature": 0, "mode": "off", "enabled": True}}

def save_thermostat_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def update_settings(value=None):
    global thermostat_config
    temperature = temperature_slider.get()
    enabled = thermostat_config['settings'].get('enabled', True) == True
    print(f"Slider temperature: {temperature}, Enabled: {enabled}")

    if not enabled:
        temperature = 0

    thermostat_config['settings']['temperature'] = temperature
    save_thermostat_config(thermostat_config)
    update_gui()
    print(f"Updated thermostat settings: {thermostat_config}")

def sync_settings_from_file():
    global thermostat_config
    print("Syncing settings from file...")
    thermostat_config = load_thermostat_config()
    temperature = thermostat_config['settings'].get('temperature', 0)
    mode = thermostat_config['settings'].get('mode', 'off')
    enabled = thermostat_config['settings'].get('enabled', True)
    if not enabled:
        temperature = 0
    # Update GUI elements
    temperature_slider.set(temperature)
    temperature_label.config(text=f"Temperature: {temperature}")
    print(f"Synced settings: Mode={mode}, Temperature={temperature}, Enabled={enabled}")

def loop_update_settings():
    sync_settings_from_file()
    root.after(1000, loop_update_settings)

# Button functionality
def cool_mode():
    global thermostat_config
    thermostat_config['settings']['mode'] = 'cool'
    thermostat_config['settings'][enabled] = True
    save_thermostat_config(thermostat_config)
    update_gui()
    print(f"Thermostat set to Cool mode: {thermostat_config}")

def off_mode():
    global thermostat_config
    thermostat_config['settings']['mode'] = 'off'
    thermostat_config['settings']['enabled'] = False
    thermostat_config['settings']['temperature'] = 0
    save_thermostat_config(thermostat_config)
    update_gui()
    print(f"Thermostat turned Off: {thermostat_config}")

def heat_mode():
    global thermostat_config
    thermostat_config['settings']['mode'] = 'heat'
    thermostat_config['settings']['enabled'] = True
    save_thermostat_config(thermostat_config)
    update_gui()
    print(f"Thermostat set to Heat mode: {thermostat_config}")

def update_gui():
    mode = thermostat_config['settings'].get('mode', 'off')
    temperature = thermostat_config['settings'].get('temperature', 'N/A')
    temperature_label.config(text=f"Temperature: {temperature}")
    thermostat_canvas.itemconfig(temperature_text, text=str(temperature) + '°')
    print(f"Updated GUI with mode: {mode}, temperature: {temperature}")

# Load thermostat001 configuration
thermostat_config = load_thermostat_config()

root = tk.Tk()
root.geometry("500x500")
root.title("Simulated Thermostat Device")
root.resizable(False, False)

main_frame = tk.Frame(root)
main_frame.pack()

thermostat_canvas = tk.Canvas(main_frame, width=300, height=500)
temperature_text = thermostat_canvas.create_text(175, 200, text='0°', font=('', 50))
thermostat_canvas.pack(side=tk.LEFT)

# Buttons for Cool, Off, and Heat modes
cool_button = tk.Button(main_frame, text='Cool', width=8, height=4, command=cool_mode)
cool_button.place(x=70, y=300)
off_button = tk.Button(main_frame, text='Off', width=8, height=4, command=off_mode)
off_button.place(x=135, y=300)
heat_button = tk.Button(main_frame, text='Heat', width=8, height=4, command=heat_mode)
heat_button.place(x=200, y=300)

slider_frame = tk.Frame(main_frame)

# Add controls to update temperature
temperature_slider = tk.Scale(slider_frame, from_=100, to=0, orient="vertical", length=300, showvalue=0, command=update_settings)
temperature_slider.set(thermostat_config['settings'].get('temperature', 0))
temperature_slider.pack(side=tk.TOP, padx=80)

# Display the logged-in user
user_id = get_logged_in_user()
user_label = tk.Label(slider_frame, text=f"User: {user_id}", font=("Arial", 10, "italic"))
user_label.pack(side=tk.BOTTOM, pady=10)

# Display thermostat001 settings
thermostat_label = tk.Label(slider_frame, text=f"Thermostat ID: {thermostat_config['device_id']}", font=("Arial", 8, "bold"))
thermostat_label.pack(side=tk.BOTTOM, pady=5)

slider_frame.pack(side=tk.RIGHT)

temperature_label = tk.Label(slider_frame, text=f"Temperature: {thermostat_config['settings'].get('temperature', 'N/A')}")
temperature_label.pack()

loop_update_settings()
root.withdraw()
# root.mainloop()