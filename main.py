from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from models.user import User  # Import User class
from models.device import LightingDevice  # Import Device classes
import bcrypt # pip insall bcrypt
from flask import jsonify

app = Flask(__name__)

app.secret_key = 'ifunre8gnfm3ir94gnur2miuf3n'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'SmartHome'
app.config['MYSQL_PASSWORD'] = 'SmartHomePassword'
app.config['MYSQL_DB'] = 'SmartHomeMonitoringSystem'
 
mysql = MySQL(app)

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

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    account = cursor.fetchone()

    if account and bcrypt.checkpw(password.encode(), account['password'].encode()):
        session['user_id'] = account['id']
        return redirect('/home')
    else:
        return redirect('/')
        
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
        
@app.route('/register', methods=['POST'])
def register():
    """Handles user registration"""
    email = request.form['email']
    password = request.form['password']
    
    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    account = cursor.fetchone()

    if account:
        return redirect('/register')
    else:
        # Store the hashed password, NOT plaintext
        cursor.execute('INSERT INTO accounts (email, password) VALUES (%s, %s)', (email, hashed_password))
        mysql.connection.commit()
        return redirect('/')


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = % s', (session['user_id'],))
    account = cursor.fetchone()

    return render_template('home.html', username=account['email'].split('@')[0])

8

app.run(debug=True)