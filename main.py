from flask import Flask, render_template, request, redirect, session, flash
import re
from models import user_manager
from models import device_manager
from models.database import *
from models.user import User  # Import User class
from flask_mysqldb import MySQL
from flask import jsonify
from models.mqtt import *

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'ifunre8gnfm3ir94gnur2miuf3n'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'SmartHome'
app.config['MYSQL_PASSWORD'] = 'SmartHomePassword'
app.config['MYSQL_DB'] = 'SmartHomeMonitoringSystem'


dummyDeviceList = [
    {'name': "Device 1",'active': True},
    {'name': "Device 2",'active': True}
    ]
with app.app_context():
    migrate_tables(mysql)

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/home')
    return render_template('login.html',message = "",dark_mode=session.get('dark_mode', False))

@app.route('/login', methods=['POST'])
def login():
    """Authenticates user and creates session"""
    email = request.form['email']
    password = request.form['password']

    id = user_manager.login(mysql, email, password)
    if(not is_valid_email(email)):
            message = "Email is invalid!"
            return render_template('login.html',message = message,dark_mode=session.get('dark_mode', False))
    elif id != None:
        session['user_id'] = id
        return redirect('/home')
    else:
        message = "Email/Password is not correct!"
        return render_template('login.html',message = message,dark_mode=session.get('dark_mode', False))
        

@app.route('/login_api', methods=['POST'])
def login_api():
     email = request.form['email']
     password = request.form['password']
 
     id = user_manager.login(mysql, email, password)
     
     if id is not None:
         return jsonify({"user_id": id})
     else:
         return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
@app.route('/settings', methods=['GET','POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html', message="",dark_mode=session.get('dark_mode', False))
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    if request.method == 'POST':
        session['dark_mode'] = not session.get('dark_mode', False)
        return render_template('settings.html', message="",dark_mode=session.get('dark_mode', False))
@app.route('/register_device', methods=['POST'])
def register_device():
    device_id = request.form['device_id']
    user_id = request.form['user_id']

    device_manager.register_device(mysql, user_id, device_id)
    return 'added'

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration"""
    if request.method == 'GET':
        return render_template('register.html', message="",dark_mode=session.get('dark_mode', False))
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirmpassword']
        if(not is_valid_email(email)):
            message = "Email is invalid!"
            return render_template('register.html', message=message, dark_mode=session.get('dark_mode', False))
        elif(password != confirm):
            message = "Passwords do not match!"
            return render_template('register.html', message=message, dark_mode=session.get('dark_mode', False))
        elif(len(password) <= 5):
            message = "Password must be 6 characters or longer!"
            return render_template('register.html', message=message, dark_mode=session.get('dark_mode', False))
        elif user_manager.create_account(mysql, email, password):
            return redirect('/')
        else:
            message = "Account already exists!"
            return render_template('register.html', message=message, dark_mode=session.get('dark_mode', False))

@app.route('/button_pressed', methods = ['POST'])
def button_pressed():  # Get the unique ID sent by the button
    light_id = int(request.form.get('id'))
    dummyDeviceList[light_id]['active'] = not dummyDeviceList[light_id]['active']
    print(f"Button {light_id} pressed!")
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/remove_button', methods = ['POST'])
def remove_button():  # Get the unique ID sent by the button
    itemid = int(request.form.get('id'))
    dummyDeviceList.pop(itemid)
    print(f"Button {itemid} pressed!")
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/add_button', methods = ['POST'])
def add_button():  # Get the unique ID sent by the button
    itemid = (request.form.get('id'))
    dummyDeviceList.append({'name':itemid,'active':False})
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/rename_button', methods = ['POST'])
def rename_button():  # Get the unique ID sent by the button
    print("Hello!!!!")
    itemid = int(request.form.get('id'))
    name = (request.form.get('name'))
    dummyDeviceList[itemid]['name'] = name
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')
    account = user_manager.get_account(mysql, session['user_id'])
    username = account['email'].split('@')[0]
    return render_template('home.html', username=username, dark_mode=session.get('dark_mode', False),items = dummyDeviceList)

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    topic = data.get("topic")
    message = data.get("message")
    publish_handler(topic, message)
    return jsonify({"status": "Message published"}), 200

@app.route('/get_device_ids', methods=['POST'])
def get_device_ids():
    return device_manager.get_device_ids(mysql, session['user_id'])

@app.route('/get_device_info', methods=['POST'])
def get_device_info():
    device_id = request.json.get('device_id')
    return device_manager.get_device_info(mysql, session['user_id'])

@app.route('/list_devices', methods=['GET', 'POST'])
def list_devices():
    device_ids = device_manager.get_device_ids(mysql, session['user_id'])
    account = user_manager.get_account(mysql, session['user_id'])
    username = account['email'].split('@')[0]
    message_str = username + ' has the following devices registered...<br>'
    for device in device_ids:
        message_str += device['device_id'] + '<br>'
    return message_str
    #return render_template('settings.html', message=message_str)

@app.route('/get_all_devices_info', methods=['GET', 'POST'])
def get_all_devices_info():
    return json.dumps(device_manager.get_all_devices_info(mysql, session['user_id']))
    
@app.route("/change-settings", methods=["POST"])
def change_settings():
    data = request.get_json()
    device_id = data.get("device_id")
    settings = data.get("settings")

    if not device_id or not settings:
        return jsonify({"error": "Missing device_id or settings"}), 400

    queue = f"device.{device_id}"
    message = {
        "type": "update",
        "settings": settings
    }

    try:
        publish_handler(queue, message)
        return jsonify({"status": "Settings update sent", "device": device_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.run(debug=True)
