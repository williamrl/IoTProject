import tkinter as tk
import json
import os

PATH = os.path.dirname(os.path.abspath(__file__))

SESSION_FILE = os.path.join(PATH, "user.session.json")
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

def rgb_to_color(rgb):
    return '#%02x%02x%02x' % rgb

def update_settings(value=None):
    global oval_id, rect_id
    brightness = brightness_slider.get()
    enabled = bool(light_config['settings'].get('enabled', True))
    print(brightness)
    if enabled == False:
        brightness = 0
    light_config['settings']['brightness'] = brightness
    save_light_config(light_config)

    light_canvas.itemconfig(oval_id, fill=rgb_to_color((int(brightness/100 * 160)+95,int(brightness/100 * 160)+95,0)))
    light_canvas.itemconfig(rect_id, fill="silver")
    brightness_label.config(text=f"Brightness: {light_config['settings']['brightness']}")
    print(CONFIG_PATH)
    print(f"Updated light001 settings: {light_config['settings']}")

def sync_settings_from_file():
    print("Updating...")
    global light_config, oval_id, rect_id
    new_config = load_light_config()
    brightness = new_config['settings'].get('brightness', 0)
    enabled = bool(new_config['settings'].get('enabled', True))
    print(brightness)
    # Only update if brightness actually changed
    if enabled == False:
        brightness = 0
    light_config = new_config

    light_canvas.itemconfig(
        oval_id,
        fill=rgb_to_color((int(brightness/100 * 160)+95, int(brightness/100 * 160)+95, 0))
    )
    brightness_label.config(text=f"Brightness: {brightness}")
        
        
def loop_update_settings():
    print(CONFIG_PATH)
    sync_settings_from_file()
    root.after(1000, loop_update_settings)
# Load light001 configuration
light_config = load_light_config()

root = tk.Tk()
root.geometry("500x500")
root.title("Simulated Light Device")
root.resizable(False, False)

main_frame = tk.Frame(root)
main_frame.pack()

light_canvas = tk.Canvas(main_frame, width=300, height=500)

oval_id = light_canvas.create_oval(50, 100, 250, 320, fill=rgb_to_color((95,95,0)))
rect_id = light_canvas.create_rectangle(100, 300, 200, 500, fill="silver")
light_canvas.pack(side=tk.LEFT)

slider_frame = tk.Frame(main_frame)

# Add controls to update brightness
brightness_slider = tk.Scale(slider_frame, from_=100, to=0, orient="vertical", length=300, showvalue=0, command=update_settings)
brightness_slider.set(light_config['settings'].get('brightness', 0))
brightness_slider.pack(side=tk.TOP, padx=80)

# Display the logged-in user
user_id = get_logged_in_user()
user_label = tk.Label(slider_frame, text=f"User: {user_id}", font=("Arial", 10, "italic"))
user_label.pack(side=tk.BOTTOM, pady=10)

# Display light001 settings
light_label = tk.Label(slider_frame, text=f"Light ID: {light_config['device_id']}", font=("Arial", 12, "bold"))
light_label.pack(side=tk.BOTTOM, pady=5)

slider_frame.pack(side=tk.RIGHT)

brightness_label = tk.Label(slider_frame, text=f"Brightness: {light_config['settings'].get('brightness', 'N/A')}")
brightness_label.pack()

loop_update_settings() 
# root.withdraw()
root.mainloop()