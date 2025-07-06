from cryptography.fernet import Fernet
import os

# Generate a key for encryption/decryption
def generate_key():
    return Fernet.generate_key()

# Create directory for key if it doesn't exist
key_file = os.path.join('src', 'database', 'key.key')
os.makedirs(os.path.dirname(key_file), exist_ok=True)

# Generate and save the key if it doesn't exist
if not os.path.exists(key_file):
    with open(key_file, 'wb') as f:
        f.write(generate_key())

# Load the key
with open(key_file, 'rb') as f:
    KEY = f.read()

cipher_suite = Fernet(KEY)

# Encrypt admin credentials
def encrypt_text(text):
    return cipher_suite.encrypt(text.encode()).decode()

# Get admin credentials from user input
admin_username = input("Enter admin username: ")
admin_password = input("Enter admin password: ")

# Encrypt the credentials
encrypted_username = encrypt_text(admin_username)
encrypted_password = encrypt_text(admin_password)

print(f"Encrypted Username: {encrypted_username}")
print(f"Encrypted Password: {encrypted_password}")

print("\nAdd these to your config.py file:")
print(f"ADMIN_USERNAME = '{encrypted_username}'")
print(f"ADMIN_PASSWORD = '{encrypted_password}'")