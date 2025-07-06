function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update form sections
    document.querySelectorAll('.form-section').forEach(section => section.classList.remove('active'));
    document.getElementById(tab + '-form').classList.add('active');
    
    // Clear any previous messages
    clearMessages();
}

function clearMessages() {
    document.getElementById('result-message').style.display = 'none';
    document.querySelectorAll('.error-message').forEach(msg => {
        msg.style.display = 'none';
        msg.textContent = '';
    });
    document.querySelectorAll('input').forEach(input => input.classList.remove('error'));
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    document.querySelectorAll('.submit-btn').forEach(btn => btn.disabled = show);
}

function showResult(message, isSuccess) {
    const resultDiv = document.getElementById('result-message');
    resultDiv.textContent = message;
    resultDiv.className = 'result-message ' + (isSuccess ? 'success' : 'error');
    resultDiv.style.display = 'block';
}

function showFieldError(fieldId, message) {
    const errorDiv = document.getElementById(fieldId + '-error');
    const input = document.getElementById('register-' + fieldId);
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    input.classList.add('error');
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function handleLogin(event) {
    event.preventDefault();
    clearMessages();
    
    // Open Palmr login in a popup window without address bar
    const palmrUrl = 'https://app.saveyourfile.online/login';
    
    // Popup window configuration
    const popupWidth = 1000;
    const popupHeight = 800;
    const left = (screen.width - popupWidth) / 2;
    const top = (screen.height - popupHeight) / 2;
    
    const popupFeatures = [
        `width=${popupWidth}`,
        `height=${popupHeight}`,
        `left=${left}`,
        `top=${top}`,
        'toolbar=no',
        'location=no',
        'directories=no',
        'status=no',
        'menubar=no',
        'scrollbars=yes',
        'resizable=yes',
        'copyhistory=no'
    ].join(',');
    
    // Open popup window
    const popup = window.open(palmrUrl, 'PalmrLogin', popupFeatures);
    
    // Focus on the popup window
    if (popup) {
        popup.focus();
    } else {
        // Fallback if popup is blocked
        showResult('Popup blocked. Please allow popups for this site and try again.', false);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    clearMessages();
    
    const firstName = document.getElementById('register-firstName').value.trim();
    const lastName = document.getElementById('register-lastName').value.trim();
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    // Basic validation
    let hasErrors = false;
    
    if (!firstName) {
        showFieldError('firstName', 'firstName is required');
        hasErrors = true;
    }

    if (!lastName) {
        showFieldError('lastName', 'lastName is required');
        hasErrors = true;
    }    
    
    if (!username) {
        showFieldError('username', 'Username is required');
        hasErrors = true;
    }
    
    if (!email) {
        showFieldError('email', 'Email is required');
        hasErrors = true;
    } else if (!validateEmail(email)) {
        showFieldError('email', 'Please enter a valid email address');
        hasErrors = true;
    }
    
    if (!password) {
        showFieldError('password', 'Password is required');
        hasErrors = true;
    } else if (password.length < 6) {
        showFieldError('password', 'Password must be at least 6 characters long');
        hasErrors = true;
    }
    
    if (!confirmPassword) {
        showFieldError('confirm-password', 'Please confirm your password');
        hasErrors = true;
    } else if (password !== confirmPassword) {
        showFieldError('confirm-password', 'Passwords do not match');
        hasErrors = true;
    }
    
    if (hasErrors) {
        return;
    }
    
    showLoading(true);
    
    try {
        // Call our registration API
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lastName: lastName,
                firstName: firstName,
                username: username,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResult('Registration successful! Your account has been created.', true);
            // Clear form
            document.getElementById('register-lastName').value = '';
            document.getElementById('register-firstName').value = '';
            document.getElementById('register-username').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-confirm-password').value = '';
        } else {
            showResult(data.message || 'Registration failed. Please try again.', false);
        }
    } catch (error) {
        console.error('Registration error:', error);
        showResult('Network error. Please check your connection and try again.', false);
    } finally {
        showLoading(false);
    }
}

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
    // Add focus effects to inputs
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.remove('error');
            const errorMsg = document.getElementById(this.name + '-error');
            if (errorMsg) {
                errorMsg.style.display = 'none';
            }
        });
    });
});