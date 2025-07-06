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
    """Get admin token with caching and detailed debugging"""
    current_time = time.time()
    
    print(f"[DEBUG] Checking admin token cache...")
    print(f"[DEBUG] Current time: {current_time}")
    print(f"[DEBUG] Token expiry: {token_cache['expiry']}")
    print(f"[DEBUG] Token exists: {token_cache['token'] is not None}")
    
    # If token exists and is not expired (giving 5 min buffer before actual expiry)
    if token_cache['token'] and token_cache['expiry'] > current_time + 300:
        print("[DEBUG] Using cached admin token")
        return token_cache['token']
    
    print("[DEBUG] Getting new admin token...")
    
    # Otherwise, get a new token
    try:
        # Decrypt admin credentials
        print("[DEBUG] Decrypting admin credentials...")
        admin_username = decrypt_text(ADMIN_USERNAME)
        admin_password = decrypt_text(ADMIN_PASSWORD)
        
        print(f"[DEBUG] Admin username: {admin_username}")
        print(f"[DEBUG] Admin password: {'*' * len(admin_password) if admin_password else 'None'}")
        print(f"[DEBUG] Login URL: {PALMR_LOGIN_URL}")
        
        # Prepare login payload
        login_payload = {
            'emailOrUsername': admin_username,
            'password': admin_password
        }
        print(f"[DEBUG] Login payload prepared (password hidden)")
        
        # Login to get token
        print("[DEBUG] Sending login request...")
        response = requests.post(
            PALMR_LOGIN_URL,
            json=login_payload,
            timeout=10
        )
        
        print(f"[DEBUG] Login response status: {response.status_code}")
        print(f"[DEBUG] Login response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("[DEBUG] Login successful, parsing response...")
            data = response.json()
            print(f"[DEBUG] Login response keys: {list(data.keys()) if data else 'No data'}")
            
            # Check for token in JSON response first
            token = data.get('token')
            
            # If not in JSON, extract from set-cookie header
            if not token:
                print("[DEBUG] Token not in JSON response, checking cookies...")
                set_cookie_header = response.headers.get('set-cookie', '')
                print(f"[DEBUG] Set-Cookie header: {set_cookie_header}")
                
                # Parse the cookie to extract token
                if 'token=' in set_cookie_header:
                    # Extract token value from cookie string
                    # Format: token=JWT_TOKEN_HERE; Path=/; HttpOnly; SameSite=Strict
                    cookie_parts = set_cookie_header.split(';')
                    for part in cookie_parts:
                        if part.strip().startswith('token='):
                            token = part.strip().split('=', 1)[1]
                            break
                    
                    if token:
                        print(f"[DEBUG] Token extracted from cookie: {token[:20]}...")
                    else:
                        print("[ERROR] Failed to extract token from cookie")
            
            if token:
                print(f"[DEBUG] Token received: {token[:20]}...")
                # Set token expiry to 1 hour from now
                token_cache['token'] = token
                token_cache['expiry'] = current_time + 3600  # 1 hour
                print(f"[DEBUG] Token cached with expiry: {token_cache['expiry']}")
                return token
            else:
                print("[ERROR] No token found in login response or cookies")
                print(f"[DEBUG] Full response: {data}")
                return None
        else:
            print(f"[ERROR] Admin login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"[ERROR] Login error response: {error_data}")
            except:
                print(f"[ERROR] Login error text: {response.text}")
            return None
            
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Login request timeout: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Login connection error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Error during admin login: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        return None

def create_user_in_palmr_api(user_data):
    """Create user in Palmr API using admin token with detailed debugging"""
    try:
        print(f"[DEBUG] Starting Palmr API user creation for: {user_data.get('username', 'Unknown')}")
        
        # Get admin token
        print("[DEBUG] Attempting to get admin token...")
        token = get_admin_token()
        if not token:
            print("[ERROR] Failed to obtain admin token")
            return False, None
        
        print(f"[DEBUG] Admin token obtained successfully: {token[:20]}...")
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        print(f"[DEBUG] Request headers prepared: {headers}")
        
        # Log the request data (excluding sensitive info)
        safe_user_data = user_data.copy()
        if 'password' in safe_user_data:
            safe_user_data['password'] = '***HIDDEN***'
        print(f"[DEBUG] Request payload: {safe_user_data}")
        print(f"[DEBUG] Target URL: {PALMR_REGISTER_URL}")
        
        # Make the API request
        print("[DEBUG] Sending POST request to Palmr API...")
        response = requests.post(
            PALMR_REGISTER_URL,
            json=user_data,
            headers=headers,
            timeout=10
        )
        
        # Log response details
        print(f"[DEBUG] Response status code: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")
        
        # Log response content
        try:
            response_json = response.json()
            print(f"[DEBUG] Response JSON: {response_json}")
        except Exception as json_error:
            print(f"[DEBUG] Response text (not JSON): {response.text}")
            print(f"[DEBUG] JSON parsing error: {json_error}")
        
        # Check for success status codes
        if response.status_code in [200, 201]:
            print("[SUCCESS] User created successfully in Palmr API")
            return True, response
        else:
            print(f"[ERROR] Palmr API returned error status: {response.status_code}")
            print(f"[ERROR] Error response: {response.text}")
            
            # Check for specific error types
            if response.status_code == 400:
                print("[ERROR] Bad Request - Check request payload format")
            elif response.status_code == 401:
                print("[ERROR] Unauthorized - Token might be invalid or expired")
            elif response.status_code == 403:
                print("[ERROR] Forbidden - Admin account might not have permission")
            elif response.status_code == 409:
                print("[ERROR] Conflict - User might already exist in Palmr")
            elif response.status_code == 422:
                print("[ERROR] Unprocessable Entity - Validation errors")
            elif response.status_code >= 500:
                print("[ERROR] Server Error - Palmr API internal error")
            
            return False, response
            
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Request timeout: {e}")
        return False, None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error: {e}")
        print("[DEBUG] Check if Palmr API URL is correct and accessible")
        return False, None
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}")
        return False, None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request exception: {e}")
        return False, None
    except Exception as e:
        print(f"[ERROR] Unexpected error in create_user_in_palmr_api: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
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

