from flask import Flask, render_template, request, redirect, session
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

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/home')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Authenticates user and creates session"""
    email = request.form['email']
    password = request.form['password']

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
    
    return id

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration"""
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if user_manager.create_account(mysql, email, password):
            return redirect('/')
        else:
            return redirect('/register')

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
    device_id = data.get("device_id")
    message = data.get("message")
    handle_publish(f"{device_id}/{session['user_id']}", message)
    return jsonify({"status": "Message published"}), 200

@app.route('/get_device_ids', methods=['POST'])
def get_device_ids():
    return device_manager.get_device_ids(mysql, session['user_id'])

@app.route('/get_device_info', methods=['POST'])
def get_device_info():
    device_id = request.json.get('device_id')
    return device_manager.get_device_info(mysql, session['user_id'])

app.run(debug=True)