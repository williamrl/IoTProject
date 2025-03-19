import MySQLdb
import bcrypt

# Database connection
db = MySQLdb.connect(
    host="localhost",
    user="SmartHome",
    password="SmartHomePassword",
    database="SmartHomeMonitoringSystem"
)
cursor = db.cursor()

# Fetch all users with plaintext passwords
cursor.execute("SELECT id, password FROM accounts")
users = cursor.fetchall()

for user in users:
    user_id, plain_password = user
    if not plain_password.startswith("$2b$"):  # Check if it's already hashed
        hashed_password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("UPDATE accounts SET password = %s WHERE id = %s", (hashed_password, user_id))

db.commit()
cursor.close()
db.close()

print("Passwords updated successfully!")
