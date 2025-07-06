from flask import Blueprint, jsonify, request
import requests
import re
import time
from src.models.user import User, db
from src.config import decrypt_text, ADMIN_USERNAME, ADMIN_PASSWORD, PALMR_LOGIN_URL, PALMR_REGISTER_URL

user_bp = Blueprint('user', __name__)

# Token cache with expiration
token_cache = {
    'token': None,
    'expiry': 0  # Unix timestamp when token expires
}

def validate_email(email):
    """Simple email validation using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_admin_token():
    """Get admin token with caching"""
    current_time = time.time()
    
    # If token exists and is not expired (giving 5 min buffer before actual expiry)
    if token_cache['token'] and token_cache['expiry'] > current_time + 300:
        return token_cache['token']
    
    # Otherwise, get a new token
    try:
        # Decrypt admin credentials
        admin_username = decrypt_text(ADMIN_USERNAME)
        admin_password = decrypt_text(ADMIN_PASSWORD)
        
        # Login to get token
        response = requests.post(
            PALMR_LOGIN_URL,
            json={
                'emailOrUsername': admin_username,
                'password': admin_password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            
            # Set token expiry to 1 hour from now (adjust based on actual token lifetime)
            token_cache['token'] = token
            token_cache['expiry'] = current_time + 3600  # 1 hour
            
            return token
        else:
            print(f"Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during admin login: {e}")
        return None

def create_user_in_palmr_api(user_data):
    """Create user in Palmr API using admin token"""
    try:
        # Get admin token
        token = get_admin_token()
        if not token:
            return False, None
        
        # Add authorization header with token
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            PALMR_REGISTER_URL,
            json=user_data,
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200 or response.status_code == 201, response
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Palmr API: {e}")
        return False, None

@user_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new user with email validation and Palmr API integration"""
    try:
        data = request.json
        
        # Validate required fields
        if not data or not all(key in data for key in ['name', 'username', 'email', 'password']):
            return jsonify({'message': 'Name, username, email, and password are required'}), 400
        
        name = data['name'].strip()
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        image = data.get('image', '')  # Optional image field
        
        # Validate field lengths and content
        if not name or len(name) < 2:
            return jsonify({'message': 'Name must be at least 2 characters long'}), 400
        
        if not username or len(username) < 3:
            return jsonify({'message': 'Username must be at least 3 characters long'}), 400
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Email validation
        if not validate_email(email):
            return jsonify({'message': 'Please enter a valid email address'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return jsonify({'message': 'Username already exists'}), 409
            else:
                return jsonify({'message': 'Email already registered'}), 409
        
        # Create user in local database first
        user = User(name=name, username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        # Split name into firstName and lastName for Palmr API
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Prepare data for Palmr API
        palmr_user_data = {
            'firstName': first_name,
            'lastName': last_name,
            'username': username,
            'email': email,
            'image': image,  # Optional image field
            'password': password  # Password field from user input
        }
        
        # Try to create user in Palmr API
        success, response = create_user_in_palmr_api(palmr_user_data)
        
        if success:
            return jsonify({
                'message': 'Registration successful! Your account has been created.',
                'user': user.to_dict()
            }), 201
        else:
            # If Palmr API fails, we still keep the local user but notify about the issue
            return jsonify({
                'message': 'Registration completed locally, but there was an issue connecting to the Palmr service. Please contact support if you experience any issues.',
                'user': user.to_dict(),
                'warning': 'Palmr API connection failed'
            }), 201
            
    except Exception as e:
        # Rollback database changes if something goes wrong
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'message': 'An error occurred during registration. Please try again.'}), 500

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(name=data['name'], username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.name = data.get('name', user.name)
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

