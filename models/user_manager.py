import bcrypt # pip insall bcrypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
    
def login(mysql, email, password):
    """Authenticates user and returns id"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    account = cursor.fetchone()

    if account and bcrypt.checkpw(password.encode(), account['password'].encode()):
        return account['id']
    
    return None

def create_account(mysql, email, password, nickname='Temp_Nickname'):
    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    account = cursor.fetchone()

    if account == None:
        # Store the hashed password, NOT plaintext
        cursor.execute('INSERT INTO accounts (email, password, nickname) VALUES (%s, %s, %s)', (email, hashed_password, nickname))
        mysql.connection.commit()

    return account == None

def get_account(mysql, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = % s', (id,))
    account = cursor.fetchone()

    return account