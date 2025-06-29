# Palmr Web Application

A Python Flask web application that provides login and registration functionality for the Palmr software.

## Features

- **Login Functionality**: Redirects users to the Palmr application login page at `http://localhost:5487/login`
- **Registration System**: 
  - Collects user information (Name, Username, Email)
  - Performs email validation using regex
  - Stores user data in local SQLite database
  - Integrates with Palmr API at `http://localhost:3333` for user creation
  - Provides appropriate error handling and user feedback
- **Modern Responsive UI**: Beautiful gradient design that works on both desktop and mobile devices
- **Form Validation**: Client-side and server-side validation with user-friendly error messages

## Project Structure

```
palmr-webapp/
├── src/
│   ├── models/
│   │   └── user.py          # User database model
│   ├── routes/
│   │   └── user.py          # API routes for user management
│   ├── static/
│   │   ├── index.html       # Frontend interface
│   │   └── favicon.ico      # Application icon
│   ├── database/
│   │   └── app.db          # SQLite database (auto-created)
│   └── main.py             # Main Flask application
├── venv/                   # Python virtual environment
└── requirements.txt        # Python dependencies
```

## Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd palmr-webapp
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies (if needed):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

5. **Access the application:**
   Open your browser and go to `http://localhost:5000`

## Usage

### Login
1. Click on the "Login" tab
2. Click "Login to Palmr" button
3. You will be redirected to `http://localhost:5487/login` (ensure Palmr is running on this port)

### Registration
1. Click on the "Register" tab
2. Fill in the required information:
   - **Full Name**: Your complete name (minimum 2 characters)
   - **Username**: Unique username (minimum 3 characters)
   - **Email**: Valid email address
3. Click "Create Account"
4. The system will:
   - Validate your email format
   - Check for existing users
   - Store your information locally
   - Attempt to create your account in the Palmr API
   - Provide feedback on the registration status

## API Integration

The application integrates with the Palmr API at `http://localhost:3333/api/users` for user creation. The integration includes:

- **Endpoint**: `POST http://localhost:3333/api/users`
- **Payload**: 
  ```json
  {
    "name": "User's Full Name",
    "username": "username",
    "email": "user@example.com",
    "source": "webapp_registration"
  }
  ```
- **Error Handling**: If the Palmr API is unavailable, users are still created locally with appropriate notifications

## API Endpoints

### Registration
- **URL**: `/api/register`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "John Doe",
    "username": "johndoe123",
    "email": "john.doe@example.com"
  }
  ```

### User Management (Standard CRUD)
- `GET /api/users` - Get all users
- `POST /api/users` - Create a user
- `GET /api/users/<id>` - Get specific user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

## Configuration

### Database
- Uses SQLite database stored at `src/database/app.db`
- Database is automatically created on first run
- User model includes: id, name, username, email

### CORS
- Cross-Origin Resource Sharing (CORS) is enabled for all routes
- Allows frontend-backend communication

### Security
- Uses Flask's built-in session management
- Email validation using regex patterns
- Input sanitization and validation

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-CORS**: Cross-origin resource sharing
- **requests**: HTTP client for API integration

## Error Handling

The application includes comprehensive error handling:

- **Client-side validation**: Real-time form validation with visual feedback
- **Server-side validation**: Backend validation for all inputs
- **API integration errors**: Graceful handling when Palmr API is unavailable
- **Database errors**: Transaction rollback and error recovery
- **Network errors**: User-friendly error messages

## Responsive Design

The application features a modern, responsive design that includes:

- **Mobile-first approach**: Works seamlessly on all device sizes
- **Interactive elements**: Hover effects, smooth transitions, and animations
- **Modern UI**: Gradient backgrounds, rounded corners, and professional styling
- **Accessibility**: Proper form labels, focus states, and keyboard navigation

## Development Notes

- The application listens on `0.0.0.0:5000` to allow external access
- Debug mode is enabled for development
- All API endpoints use JSON for data exchange
- The frontend uses vanilla JavaScript for maximum compatibility

## Troubleshooting

### Common Issues

1. **Port 5000 already in use**:
   - Change the port in `src/main.py`: `app.run(host='0.0.0.0', port=5001, debug=True)`

2. **Palmr API connection failed**:
   - Ensure Palmr is running on `localhost:3333`
   - Check firewall settings
   - Users will still be created locally if API is unavailable

3. **Database errors**:
   - Delete `src/database/app.db` to reset the database
   - Restart the application to recreate tables

4. **Virtual environment issues**:
   - Deactivate and reactivate: `deactivate && source venv/bin/activate`
   - Reinstall dependencies: `pip install -r requirements.txt`

## License

This project is created for integration with the Palmr software system.

