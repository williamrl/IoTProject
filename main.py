from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = % s AND password = % s', (email, password, ))
        account = cursor.fetchone()

        if account:
            session['user_id'] = account['id']
            return redirect('/home')
        else:
            return redirect('/')
        
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id')
        return redirect('/')
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect('/home')
        
        return render_template('register.html')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = % s', (email, ))
        account = cursor.fetchone()

        if account:
            return redirect('/register')
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s)',(email, password,))
            mysql.connection.commit()
            return redirect('/home')


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = % s', (session['user_id'],))
    account = cursor.fetchone()

    return render_template('home.html', username=account['email'].split('@')[0])

app.run(debug=True)