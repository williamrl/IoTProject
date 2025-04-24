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
def getid(mysql,email):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    account = cursor.fetchone()
    return account['id']
def create_account(mysql, email, password, nickname='Temp_Nickname', is_confirmed=False):
    """Creates a new account with hashed password and confirmation status"""
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    account = cursor.fetchone()

    if account is None:
        cursor.execute(
            'INSERT INTO accounts (email, password, nickname, is_confirmed) VALUES (%s, %s, %s, %s)',
            (email, hashed_password, nickname, is_confirmed)
        )
        mysql.connection.commit()

    return account is None

def confirm_account(mysql, email):
    """Marks the account as confirmed"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE accounts SET is_confirmed = TRUE WHERE email = %s', (email,))
    mysql.connection.commit()

def is_confirmed(mysql, email):
    """Checks if the account is confirmed"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT is_confirmed FROM accounts WHERE email = %s', (email,))
    result = cursor.fetchone()
    return result and result['is_confirmed'] == 1

def get_account(mysql, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = % s', (id,))
    account = cursor.fetchone()

    return account