# If not installed already install pycryptodome with the command "pip install pycryptodome"

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

class Security:
    def __init__(self, key=None):
        """Initialize with a 32-byte AES-256 key. Generate a new one if not provided."""
        self.key = key if key else os.urandom(32)  # Generate a secure key if not given

    def encrypt(self, data):
        """Encrypts device data using AES-256-CBC."""
        iv = os.urandom(16)  # Generate a random IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(iv + encrypted_data).decode()  # Return as Base64 string

    def decrypt(self, encrypted_data):
        """Decrypts AES-256-CBC encrypted device data."""
        encrypted_data = base64.b64decode(encrypted_data)
        iv = encrypted_data[:16]  # Extract IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted_data.decode()

# Example Usage
if __name__ == "__main__":
    # Create a Security instance
    security = Security()

    # Sample device data
    device_data = "Motion sensor triggered"

    # Encrypt data
    encrypted = security.encrypt(device_data)
    print("Encrypted Device Data:", encrypted)

    # Decrypt data
    decrypted = security.decrypt(encrypted)
    print("Decrypted Device Data:", decrypted)
