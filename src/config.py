import os
from cryptography.fernet import Fernet

# Generate a key for encryption/decryption
# In production, this should be stored securely and not in the code
def generate_key():
    return Fernet.generate_key()

# If key doesn't exist, generate one
key_file = os.path.join(os.path.dirname(__file__), 'database', 'key.key')
os.makedirs(os.path.dirname(key_file), exist_ok=True)

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

# Decrypt admin credentials
def decrypt_text(encrypted_text):
    return cipher_suite.decrypt(encrypted_text.encode()).decode()

# Admin credentials - these are encrypted at rest
ADMIN_USERNAME =  
ADMIN_PASSWORD =  

# Palmr API configuration
PALMR_API_BASE_URL = 'http://192.168.88.3:3333'
PALMR_LOGIN_URL = f'{PALMR_API_BASE_URL}/auth/login'
PALMR_REGISTER_URL = f'{PALMR_API_BASE_URL}/auth/register'