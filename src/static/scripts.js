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
    
    // Clear previous errors
    clearErrors();
    
    // Get form data
    const firstName = document.getElementById('register-firstName').value.trim();
    const lastName = document.getElementById('register-lastName').value.trim();
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    // Validate form
    let hasError = false;
    
    if (!firstName) {
        showError('firstName-error', 'Vui lòng nhập tên');
        hasError = true;
    }
    
    if (!lastName) {
        showError('lastName-error', 'Vui lòng nhập họ');
        hasError = true;
    }
    
    if (!username) {
        showError('username-error', 'Vui lòng nhập tên đăng nhập');
        hasError = true;
    } else if (username.length < 3) {
        showError('username-error', 'Tên đăng nhập phải có ít nhất 3 ký tự');
        hasError = true;
    }
    
    if (!email) {
        showError('email-error', 'Vui lòng nhập email');
        hasError = true;
    } else if (!isValidEmail(email)) {
        showError('email-error', 'Email không hợp lệ');
        hasError = true;
    }
    
    if (!password) {
        showError('password-error', 'Vui lòng nhập mật khẩu');
        hasError = true;
    } else if (password.length < 6) {
        showError('password-error', 'Mật khẩu phải có ít nhất 6 ký tự');
        hasError = true;
    }
    
    if (!confirmPassword) {
        showError('confirm-password-error', 'Vui lòng xác nhận mật khẩu');
        hasError = true;
    } else if (password !== confirmPassword) {
        showError('confirm-password-error', 'Mật khẩu không khớp');
        hasError = true;
    }
    
    if (hasError) {
        return;
    }
    
    // Show loading
    showLoading();
    
    // Send registration request
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            firstName: firstName,
            lastName: lastName,
            username: username,
            email: email,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showResult(data.message, 'success');
            // Clear form
            document.getElementById('register-form').querySelector('form').reset();
        } else {
            showResult(data.error || 'Có lỗi xảy ra', 'error');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showResult('Có lỗi xảy ra. Vui lòng thử lại sau.', 'error');
    });
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