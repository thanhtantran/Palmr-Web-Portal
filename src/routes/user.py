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

def create_palmr_user(user_data):
    """Create user in Palmr API with detailed debugging"""
    print(f"[DEBUG] Starting Palmr API user creation for: {user_data.get('username', 'Unknown')}")
    
    # Get admin token
    print("[DEBUG] Attempting to get admin token...")
    admin_token = get_admin_token()
    if not admin_token:
        print("[ERROR] Failed to obtain admin token")
        return False
    
    print(f"[DEBUG] Admin token obtained successfully: {admin_token[:20]}...")
    
    try:
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {admin_token}',
            'Content-Type': 'application/json'
        }
        print(f"[DEBUG] Request headers prepared: {headers}")
        
        # Prepare payload with separate firstName and lastName
        payload = {
            'firstName': user_data.get('firstName', '').strip(),
            'lastName': user_data.get('lastName', '').strip(),
            'username': user_data['username'].strip(),
            'email': user_data['email'].strip(),
            'password': user_data['password']
        }
        
        # Add image field if provided
        if 'image' in user_data and user_data['image']:
            payload['image'] = user_data['image']
        
        # Hide password in debug output
        debug_payload = payload.copy()
        debug_payload['password'] = '***HIDDEN***'
        print(f"[DEBUG] Request payload: {debug_payload}")
        print(f"[DEBUG] Target URL: {PALMR_REGISTER_URL}")
        print(f"[DEBUG] Sending POST request to Palmr API...")
        
        response = requests.post(
            PALMR_REGISTER_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"[DEBUG] Response status code: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("[DEBUG] User creation successful!")
            try:
                response_data = response.json()
                print(f"[DEBUG] Success response: {response_data}")
            except:
                print(f"[DEBUG] Success response (text): {response.text}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"[DEBUG] Error response JSON: {error_data}")
            except:
                print(f"[DEBUG] Error response text: {response.text}")
            
            print(f"[ERROR] Palmr API returned error status: {response.status_code}")
            if response.status_code == 400:
                print("[ERROR] Bad Request - Check request payload format")
            elif response.status_code == 409:
                print("[ERROR] Conflict - User might already exist")
            elif response.status_code == 422:
                print("[ERROR] Unprocessable Entity - Validation error")
            
            return False
        
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Request timeout: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error creating Palmr user: {e}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        return False

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate reCAPTCHA
        recaptcha_token = data.get('recaptchaToken')
        if not recaptcha_token:
            return jsonify({'error': 'Vui lòng xác nhận reCAPTCHA'}), 400
            
        # Verify with Google reCAPTCHA API
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': current_app.config['RECAPTCHA_SECRET_KEY'],
            'response': recaptcha_token
        }
        response = requests.post(verify_url, data=payload)
        result = response.json()
        
        if not result.get('success'):
            return jsonify({'error': 'Xác thực reCAPTCHA thất bại'}), 400

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                print(f"[ERROR] Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract user data
        firstName = data['firstName'].strip()
        lastName = data['lastName'].strip()
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        
        print(f"[DEBUG] Extracted data - firstName: {firstName}, lastName: {lastName}, username: {username}, email: {email}")
        
        # Validate data
        if len(firstName) < 1:
            return jsonify({'error': 'Tên phải có ít nhất 1 ký tự'}), 400
            
        if len(lastName) < 1:
            return jsonify({'error': 'Họ phải có ít nhất 1 ký tự'}), 400
            
        if len(username) < 3:
            return jsonify({'error': 'Tên đăng nhập phải có ít nhất 3 ký tự'}), 400
            
        if len(password) < 6:
            return jsonify({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Email không hợp lệ'}), 400
        
        print("[DEBUG] All validations passed")
        
        # Prepare user data for Palmr API
        user_data = {
            'firstName': firstName,
            'lastName': lastName,
            'username': username,
            'email': email,
            'password': password
        }
        
        # Create user in Palmr API
        print("[DEBUG] Creating user in Palmr API...")
        if create_palmr_user(user_data):
            print("[DEBUG] User created successfully in Palmr API")
            return jsonify({
                'message': 'Tài khoản đã được tạo thành công! Vui lòng kiểm tra email để xác minh tài khoản.',
                'success': True
            }), 201
        else:
            print("[ERROR] Failed to create user in Palmr API")
            return jsonify({'error': 'Không thể tạo tài khoản. Vui lòng thử lại sau.'}), 500
            
    except Exception as e:
        print(f"[ERROR] Registration error: {e}")
        import traceback
        print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Lỗi server. Vui lòng thử lại sau.'}), 500

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

