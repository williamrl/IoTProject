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

with app.app_context():
    migrate_accounts_table(mysql)
    migrate_connections_table(mysql)

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    print("login")
    if 'user_id' in session:
        return redirect('/home')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    print("login")
    """Authenticates user and creates session"""
    email = request.form['email']
    print(email)
    password = request.form['password']
    print(password)

    id = user_manager.login(mysql, email, password)
    
    if id != None:
        session['user_id'] = id
        return redirect('/home')
    else:
        return redirect('/')
        

@app.route('/login_api', methods=['POST'])
def login_api():
     email = request.form['email']
     password = request.form['password']
 
     id = user_manager.login(mysql, email, password)
     
     return str(id)

@app.route('/logout', methods=['POST'])
def logout():
    print("logout")
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
@app.route('/settings', methods=['GET','POST'])
def settings():
    print("settings")
    if request.method == 'GET':
        return render_template('settings.html', message="")
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
    
@app.route('/register_device', methods=['POST'])
def register_device():
    device_id = request.form['device_id']
    user_id = request.form['user_id']

    device_manager.register_device(mysql, user_id, device_id)
    return 'added'

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("register")
    """Handles user registration"""
    if request.method == 'GET':
        return render_template('register.html', message="")
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirmpassword']
        if(not is_valid_email(email)):
            message = "Email is invalid!"
            return render_template('register.html', message=message)
        elif(password != confirm):
            message = "Passwords do not match!"
            return render_template('register.html', message=message)
        elif(len(password) <= 5):
            message = "Password must be 6 characters or longer!"
            return render_template('register.html', message=message)
        elif user_manager.create_account(mysql, email, password):
            return redirect('/')
        else:
            message = "Account already exists!"
            return render_template('register.html', message=message)

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')
    
    account = user_manager.get_account(mysql, session['user_id'])
    username = account['email'].split('@')[0]

    return render_template('home.html', username=username)

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

app.run(debug=True)