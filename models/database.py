from flask_mysqldb import MySQL
import MySQLdb.cursors

accounts_fields = ({'Field': 'id', 'Type': 'int', 'Null': 'NO', 'Key': 'PRI', 'Default': None, 'Extra': 'auto_increment'}, {'Field': 'email', 'Type': 'varchar(255)', 'Null': 'NO', 'Key': '', 'Default': None, 'Extra': ''}, {'Field': 'password', 'Type': 'varchar(255)', 'Null': 'NO', 'Key': '', 'Default': None, 'Extra': ''})

def migrate_accounts_table(mysql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SHOW TABLES LIKE 'accounts'")
    accounts_exists = cursor.fetchone()

    if accounts_exists:
        cursor.execute("DESCRIBE accounts")
        fields = cursor.fetchall()

        if fields != accounts_fields:
            cursor.execute("DROP TABLE IF EXISTS accounts")
            cursor.execute("""CREATE TABLE accounts(
                        id INT NOT NULL AUTO_INCREMENT,
                        email VARCHAR(255) NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        PRIMARY KEY(id))""")
    else:
        cursor.execute("""CREATE TABLE accounts(
                            id INT NOT NULL AUTO_INCREMENT,
                            email VARCHAR(255) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            PRIMARY KEY(id))""")