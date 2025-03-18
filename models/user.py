import bcrypt

class User:
    def __init__(self, user_id, username, email, role="user"):
        self.user_id = user_id
        self.username = username
        self.password = None  # Initialize as None until explicitly set
        self.email = email
        self.role = role

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password):
        """Verifies the provided password against the stored hash."""
        if self.password is None:
            return False
        return bcrypt.checkpw(password.encode(), self.password.encode('utf-8'))

    def get_role(self):
        return self.role
