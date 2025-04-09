from flask_mysqldb import MySQL
import MySQLdb.cursors

accounts_sql = """CREATE TABLE accounts(
                id INT NOT NULL AUTO_INCREMENT,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                nickname VARCHAR(255) NOT NULL,
                PRIMARY KEY(id))"""

connections_sql = """CREATE TABLE connections(
                id INT NOT NULL AUTO_INCREMENT,
                account_id INT NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                PRIMARY KEY(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id))"""

user_logs_sql = """CREATE TABLE user_logs(
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                action VARCHAR(50),
                status VARCHAR(50),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts(id))"""

device_logs_sql = """CREATE TABLE device_logs(
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  device_name VARCHAR(255),
                  event TEXT,
                  user_id INT DEFAULT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES accounts(id))"""

def describeSQL(mysql, sql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DROP TABLE IF EXISTS temp")
    table_name = sql.split('(')[0].split(' ')[-1]
    sql = sql.replace(table_name, 'temp')
    cursor.execute(sql)
    cursor.execute("DESCRIBE temp")
    described_sql = cursor.fetchall()
    cursor.execute("DROP TABLE IF EXISTS temp")
    return described_sql

def migrate_table(mysql, sql, fks=[]):
    table_name = sql.split('(')[0].split(' ')[-1]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute(f"DESCRIBE {table_name}")
        fields = cursor.fetchall()

        if fields != describeSQL(mysql, sql):
            for fk in fks:
                fk_table_name = fk.split('(')[0].split(' ')[-1]
                cursor.execute(f"DROP TABLE IF EXISTS {fk_table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(sql)
            for fk in fks:
                cursor.execute(fk)
    else:
        cursor.execute(sql)

def migrate_tables(mysql):
    migrate_table(mysql, accounts_sql, [connections_sql, user_logs_sql, device_logs_sql])
    migrate_table(mysql, connections_sql)
    migrate_table(mysql, user_logs_sql)
    migrate_table(mysql, device_logs_sql)
