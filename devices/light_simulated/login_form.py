import tkinter as tk
from tkinter import messagebox
import requests, json, sys

SESSION_FILE = ''
QUEUE_NAME = ''
root = None
emailField = None
passwordField = None

def save_user_session(user_id, SESSION_FILE):
    with open(SESSION_FILE, 'w') as f:
        json.dump({"user_id": user_id}, f)

def register_device(account_id, QUEUE_NAME):
    requests.post('http://127.0.0.1:5000/register_device', {'user_id':account_id, 'device_id':QUEUE_NAME})

def login(email, password):
    global root
    response = requests.post('http://127.0.0.1:5000/login_api', {'email': email, 'password': password})

    if response.status_code == 200:
        data = response.json()
        user_id = data.get("user_id")
        if user_id:
            register_device(user_id, QUEUE_NAME)
            save_user_session(user_id, SESSION_FILE)
            global root
            root.destroy()
            root.quit()
            return
    messagebox.showerror("Unable to login", "Incorrect email or password")


def check_login():
    global emailField
    global passwordField
    global SESSION_FILE
    global QUEUE_NAME

    email = emailField.get()
    password = passwordField.get()

    login(email, password)

def offline():
    global root
    root.destroy()
    root.quit()

def on_close():
    sys.exit()

def login_gui(file, name):
    global SESSION_FILE
    global QUEUE_NAME
    global root
    global emailField
    global passwordField
    SESSION_FILE = file
    QUEUE_NAME = name

    root = tk.Tk()
    root.geometry("300x300")
    root.title("Login")
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.resizable(False, False)
    emailLabel = tk.Label(root, text='Email')
    emailField = tk.Entry(root)
    passwordLabel = tk.Label(root, text='Password')
    passwordField = tk.Entry(root)
    loginButton = tk.Button(root, text="Login", command=check_login)
    offlineButton = tk.Button(root, text="Offline Mode", command=offline)

    emailLabel.pack(pady=(60,0))
    emailField.pack()
    passwordLabel.pack()
    passwordField.pack()
    loginButton.pack(pady=10)
    offlineButton.pack()

    root.mainloop()