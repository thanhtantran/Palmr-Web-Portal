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
ADMIN_USERNAME = 'gAAAAABoapZ8lm-jHfL-rFchp8qkwhaAyXfliKnp5oQbY6Cr42Wbv5s7KAaCF4BKQ8XWZML3RdisvKkbLJuSYwxw7NaSVbW2Bw=='
ADMIN_PASSWORD = 'gAAAAABoapZ8_GTEYbhL-LoZva8GDaY1uFtcucQDphQ-YGtT6uS8BkU4F0llrsQNxURlOzPMqdR93hGwGTZIKx3-VxIiw7mcmQ=='

# Palmr API configuration
PALMR_API_BASE_URL = 'http://192.168.88.3:3333'
PALMR_LOGIN_URL = f'{PALMR_API_BASE_URL}/auth/login'
PALMR_REGISTER_URL = f'{PALMR_API_BASE_URL}/auth/register'

# reCAPTCHA configuration
RECAPTCHA_SITE_KEY = '6Lf3DXorAAAAAGF9FdJ60Se6lIVT9uyg72BgANn9'  # Should match your frontend
RECAPTCHA_SECRET_KEY = '6Lf3DXorAAAAAJYu9IDKUSvncag1kU_pT9L37qdY'  # Get from Google reCAPTCHA admin

# SMTP configuration
SMTP_SERVER = 'smtp.postmarkapp.com'
SMTP_PASSWORD = '23eef7c7-1986-446b-af8c-e203939e6b31'
SMTP_USERNAME = '23eef7c7-1986-446b-af8c-e203939e6b31'
SMTP_PORT = 587
