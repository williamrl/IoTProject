from flask import Flask, render_template, request, redirect, session, flash, url_for
import re
import os
from models import user_manager
from models import device_manager
from models.logger import Logger
from devices.light_simulated import light_gui
from models.database import *
from models.user import User  # Import User class
from flask_mysqldb import MySQL
from flask import jsonify
from models.mqtt import *
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
logger = Logger()
mysql = MySQL(app)

app.secret_key = 'ifunre8gnfm3ir94gnur2miuf3n'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'SmartHome'
app.config['MYSQL_PASSWORD'] = 'SmartHomePassword'
app.config['MYSQL_DB'] = 'SmartHomeMonitoringSystem'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'IoTSmartHomePSU@gmail.com'
app.config['MAIL_PASSWORD'] = 'wtma fcze dtiu gbki'
app.config['MAIL_DEFAULT_SENDER'] = 'IoTSmartHomePSU@gmail.com'

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['MAIL_PASSWORD'])


dummyDeviceList = {}
addedDevices = {}
with app.app_context():
    migrate_tables(mysql)

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    logger.log_user_activity(user_id=session.get('user_id', 'guest'), action="visit index", status="viewed")
    if 'user_id' in session:
        return redirect('/home')
    return render_template('login.html',message = "",dark_mode=session.get('dark_mode', False))

@app.route('/login', methods=['POST'])
def login():
    """Authenticates user and creates session"""
    email = request.form['email']
    password = request.form['password']

    if not is_valid_email(email):
        message = "Email is invalid!"
        return render_template('login.html',message = message,dark_mode=session.get('dark_mode', False))

    # Check if account exists and is confirmed
    if not user_manager.is_confirmed(mysql, email):
        message = "Please confirm your email before logging in."
        return render_template('login.html',message = message,dark_mode=session.get('dark_mode', False))

    # Continue login if confirmed
    id = user_manager.login(mysql, email, password)
    if id is not None:
        session['user_id'] = id
        logger.log_user_activity(user_id=id, action="login", status="success")
        return redirect('/home')
    else:
        message = "Email/Password is not correct!"
        logger.log_user_activity(user_id=email, action="login", status="failure")
        return render_template('login.html',message = message,dark_mode=session.get('dark_mode', False))
        

@app.route('/login_api', methods=['POST'])
def login_api():
     email = request.form['email']
     password = request.form['password']
 
     id = user_manager.login(mysql, email, password)
     
     if id is not None:
         logger.log_user_activity(user_id=id, action="API login", status="success")
         return jsonify({"user_id": id})
     else:
         logger.log_user_activity(user_id=email, action="API login", status="failure")
         return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        user_id = session.get('user_id', 'unknown')
        logger.log_user_activity(user_id=user_id, action="logout", status="success")
        session.pop('user_id')
        return redirect('/')

@app.route('/logs', methods=['GET'])
def logs():
    if request.method == 'GET':
        user_id = session.get('user_id', 'guest')
        logger.log_user_activity(user_id=user_id, action="view logs", status="success")
        return render_template('logs.html', message="",dark_mode=session.get('dark_mode', False), items = [])

@app.route('/settings', methods=['GET','POST'])
def settings():
    if request.method == 'GET':
        logger.log_user_activity(user_id = session['user_id'], action="view settings", status="success")
        return render_template('settings.html', message="",dark_mode=session.get('dark_mode', False))
    if request.method == 'POST':
        session.pop('user_id')
        logger.log_user_activity(user_id = session['user_id'], action="logout via settings", status="success")
        return redirect('/')
    
@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    if request.method == 'POST':
        user_id = session.get('user_id', 'unknown')
        session['dark_mode'] = not session.get('dark_mode', False)
        logger.log_user_activity(user_id=user_id, action="toggle dark mode", status="success")
        return render_template('settings.html', message="",dark_mode=session.get('dark_mode', False))
    
@app.route('/register_device', methods=['POST'])
def register_device():
    device_id = request.form['device_id']
    user_id = request.form['user_id']

    device_manager.register_device(mysql, user_id, device_id)
    logger.log_device_activity(device_name=device_id, event="Device registered", user_id=user_id)
    return 'added'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', message="", dark_mode=session.get('dark_mode', False))
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirmpassword']

        if not is_valid_email(email):
            return render_template('register.html', message="Email is invalid!", dark_mode=session.get('dark_mode', False))
        elif password != confirm:
            return render_template('register.html', message="Passwords do not match!", dark_mode=session.get('dark_mode', False))
        elif len(password) <= 5:
            return render_template('register.html', message="Password must be 6 characters or longer!", dark_mode=session.get('dark_mode', False))

        # Attempt to create user but with is_confirmed = False
        if user_manager.create_account(mysql, email, password, is_confirmed=False):
            # Generate token
            token = serializer.dumps(email, salt='email-confirm')
            confirm_url = url_for('confirm_email', token=token, _external=True)

            # Send confirmation email
            msg = Message('Confirm your SmartHome Account', recipients=[email])
            msg.body = f'Thank you for registering!\n\nClick this link to activate your account:\n{confirm_url}'
            mail.send(msg)
            logger.log_user_activity(user_id=email, action="register", status="unconfirmed")

            return render_template('message.html', message="Account created! Please check your email to confirm your account.")
        else:
            if not user_manager.is_confirmed(mysql, email):
                message = "This account exists but is unverified! Please verify through your email."
                token = serializer.dumps(email, salt='email-confirm')
                confirm_url = url_for('confirm_email', token=token, _external=True)
                logger.log_user_activity(user_id=email, action="resent confirmation", status="pending")

                # Send confirmation email
                msg = Message('Confirm your SmartHome Account', recipients=[email])
                msg.body = f'Thank you for registering!\n\nClick this link to activate your account:\n{confirm_url}'
                mail.send(msg)
                return render_template('login.html',message = message,dark_mode=session.get('dark_mode', False))
            else:
                return render_template('register.html', message="Account already exists!", dark_mode=session.get('dark_mode', False))
        
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        return render_template('message.html', message="Confirmation link is invalid or expired.")

    user_manager.confirm_account(mysql, email)  # ➕ Set `is_confirmed=True` in DB
    logger.log_user_activity(user_id=email, action="email confirmed", status="success")
    return render_template('message.html', message="Your account has been confirmed! You can now log in.")


@app.route('/button_pressed', methods = ['POST'])
def button_pressed():  # Get the unique ID sent by the button
    id = session['user_id']

    print("Updating...")
    light_id = int(request.form.get('id'))
    itemtype = request.form.get('type')
    dummyDeviceList[id][light_id]['active'] = not dummyDeviceList[id][light_id]['active']
    isActive = dummyDeviceList[id][light_id]['active']
    print(itemtype)
    if(itemtype != "dummy"):
        deviceid = request.form.get('deviceid')
        deviceid = deviceid.split(".")[1]
        filename = f"{deviceid}_config.json"
        config_path = filename
        print()
        print(config_path)
        if not os.path.exists(config_path):
            return jsonify(success=False, error="Config file not found"), 404

        with open(config_path, 'r') as f:
            config = json.load(f)

        logger.log_device_activity(device_name=deviceid, event="Toggled device state", user_id=id)
        config.setdefault("settings", {})["enabled"] = isActive
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

    return jsonify(success=True)

    print(f"Button {light_id} pressed!")
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/remove_button', methods = ['POST'])
def remove_button():  # Get the unique ID sent by the button
    id = session['user_id']
    itemid = int(request.form.get('id'))
    dummy = bool(request.form.get('dummy'))
    if(dummy != "dummy"):
        deviceid = request.form.get('deviceid')
        print(id)
        print(deviceid)
        device_manager.unregister_device(mysql,id,deviceid)
        logger.log_device_activity(device_name=deviceid, event="Device unregistered", user_id=id)
    dummyDeviceList[id].pop(itemid)
    print(f"Button {itemid} pressed!")
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/add_button', methods = ['POST'])
def add_button():  # Get the unique ID sent by the button
    id = session['user_id']
    itemid = (request.form.get('id'))
    dummyDeviceList[id].append({'name':itemid,'active':False,'type':'dummy'} )
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/rename_button', methods = ['POST'])
def rename_button():  # Get the unique ID sent by the button
    print("Hello!!!!")
    id = session['user_id']
    itemid = int(request.form.get('id'))
    name = (request.form.get('name'))
    dummyDeviceList[id][itemid]['name'] = name
    logger.log_device_activity(device_name=dummyDeviceList[id][itemid]['name'], event=f"Renamed to {name}", user_id=id)
    return jsonify(message=f"Button {1} pressed successfully!")

@app.route('/home')
def home():

    if 'user_id' not in session:
        return redirect('/')
    id = session['user_id']
    logger.log_user_activity(user_id=id, action="viewed home", status="success")
    if(not id in dummyDeviceList):
            dummyDeviceList[id] = []
            addedDevices[id] = []
    account = user_manager.get_account(mysql, session['user_id'])
    username = account['email'].split('@')[0]
    device_ids = device_manager.get_device_ids(mysql, session['user_id'])
    realDeviceList = []
    for device in device_ids:
        print(device)
        if(device not in addedDevices[id]):
            deviceid = device.split(".")[1]
            filename = f"{deviceid}_config.json"
            print(filename)
            config_path = filename
            print(config_path)
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                brightness = config.get("settings", {}).get("brightness", 50)
            else:
                brightness = 50  # Default value if file doesn't exist
            

            print(brightness)
            realDeviceList.insert(0,{'name':device,'active': True,'type':"light",'deviceid': device,'value':brightness})
            addedDevices[id].append(device)
    dummyDeviceList[id].extend(realDeviceList)
    for device in dummyDeviceList[id]:
        if(device['type'] == "light"):
            deviceid = device['deviceid'].split(".")[1]
            filename = f"{deviceid}_config.json"
            print(filename)
            config_path = filename
            print(config_path)
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                brightness = config.get("settings", {}).get("brightness", 50)
            else:
                brightness = 50  # Default value if file doesn't exist
            device['value'] = brightness

    return render_template('home.html', username=username, dark_mode=session.get('dark_mode', False),items = dummyDeviceList[id])

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    topic = data.get("topic")
    message = data.get("message")
    publish_handler(topic, message)
    logger.log_device_activity(
        device_name=topic,
        event=f"MQTT message published: {message}",
        user_id=session.get('user_id', 'unknown')
    )

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
        logger.log_device_activity(
            device_name=device_id,
            event=f"Settings update sent: {settings}",
            user_id=session.get('user_id', 'unknown')
        )
        return jsonify({"status": "Settings update sent", "device": device_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/update_slider_config', methods=['POST'])
def update_slider_config():
    print("Updating...")
    data = request.get_json()
    deviceid = data['deviceid']
    print(deviceid)
    deviceid = deviceid.split(".")[1]
    value = int(data['value'])

    logger.log_device_activity(
        device_name=deviceid,
        event=f"Brightness set to {value}",
        user_id=session['user_id']
    )

    filename = f"{deviceid}_config.json"
    config_path = filename
    print(config_path)
    if not os.path.exists(config_path):
        return jsonify(success=False, error="Config file not found"), 404

    with open(config_path, 'r') as f:
        config = json.load(f)

    config.setdefault("settings", {})["brightness"] = value
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    return jsonify(success=True)





app.run(debug=True)
