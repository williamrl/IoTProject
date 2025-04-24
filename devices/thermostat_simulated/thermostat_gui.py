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
    return {"device_id": "thermostat001", "settings": {}}

def save_thermostat_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def rgb_to_color(rgb):
    return '#%02x%02x%02x' % rgb

def update_settings(value=None):
    global oval_id, rect_id
    temperature = temperature_slider.get()
    enabled = bool(thermostat_config['settings'].get('enabled', True))
    print(temperature)
    if enabled == False:
        temperature = 0
    thermostat_config['settings']['temperature'] = temperature
    save_thermostat_config(thermostat_config)

    # thermostat_canvas.itemconfig(oval_id, fill=rgb_to_color((int(temperature/100 * 160)+95,int(temperature/100 * 160)+95,0)))
    # thermostat_canvas.itemconfig(rect_id, fill="silver")
    thermostat_canvas.itemconfig(temperature_text, text=str(temperature) + '°')
    temperature_label.config(text=f"Temperature: {thermostat_config['settings']['temperature']}")
    print(CONFIG_PATH)
    print(f"Updated thermostat001 settings: {thermostat_config['settings']}")

def sync_settings_from_file():
    print("Updating...")
    global thermostat_config, oval_id, rect_id
    new_config = load_thermostat_config()
    temperature = new_config['settings'].get('temperature', 0)
    enabled = bool(new_config['settings'].get('enabled', True))
    print(temperature)
    # Only update if temperature actually changed
    if enabled == False:
        temperature = 0
    thermostat_config = new_config

    # thermostat_canvas.itemconfig(
    #     oval_id,
    #     fill=rgb_to_color((int(temperature/100 * 160)+95, int(temperature/100 * 160)+95, 0))
    # )
    temperature_label.config(text=f"Temperature: {temperature}")
        
        
def loop_update_settings():
    print(CONFIG_PATH)
    sync_settings_from_file()
    root.after(1000, loop_update_settings)
# Load thermostat001 configuration
thermostat_config = load_thermostat_config()

root = tk.Tk()
root.geometry("500x500")
root.title("Simulated Thermostat Device")
root.resizable(False, False)

main_frame = tk.Frame(root)
main_frame.pack()

thermostat_canvas = tk.Canvas(main_frame, width=300, height=500)

# oval_id = thermostat_canvas.create_oval(50, 100, 250, 320, fill=rgb_to_color((95,95,0)))
# rect_id = thermostat_canvas.create_rectangle(100, 300, 200, 500, fill="silver")
temperature_text = thermostat_canvas.create_text(175, 200, text='0°', font=('',50))
thermostat_canvas.pack(side=tk.LEFT)

cool_button = tk.Button(main_frame, text='Cool', width=8, height=4)
cool_button.place(x=70, y=300)
off_button = tk.Button(main_frame, text='Off', width=8, height=4)
off_button.place(x=135, y=300)
heat_button = tk.Button(main_frame, text='Heat', width=8, height=4)
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