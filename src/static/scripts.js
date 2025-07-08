let loginCaptchaSuccess = false;
let registerCaptchaSuccess = false;

function onLoginCaptchaSuccess(token) {
    loginCaptchaSuccess = true;
}

function onRegisterCaptchaSuccess(token) {
    registerCaptchaSuccess = true;
}

function resetCaptcha() {
    loginCaptchaSuccess = false;
    registerCaptchaSuccess = false;
    grecaptcha.reset();
}

function switchTab(tab) {
  // Update tab buttons
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
  
  // Find the clicked button and make it active
  const clickedButton = Array.from(document.querySelectorAll('.tab-button')).find(btn => 
      (tab === 'login' && btn.textContent.includes('Đăng nhập')) ||
      (tab === 'register' && btn.textContent.includes('Đăng ký'))
  );
  if (clickedButton) {
      clickedButton.classList.add('active');
  }
  
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
  resetCaptcha();
}

function clearErrors() {
  clearMessages();
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
  
  if (errorDiv && input) {
      errorDiv.textContent = message;
      errorDiv.style.display = 'block';
      input.classList.add('error');
  }
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
  
  // Client-side validation
  let hasErrors = false;
  
  if (!firstName) {
      showFieldError('firstName', 'Tên là bắt buộc');
      hasErrors = true;
  }

  if (!lastName) {
      showFieldError('lastName', 'Họ là bắt buộc');
      hasErrors = true;
  }    
  
  if (!username) {
      showFieldError('username', 'Tên đăng nhập là bắt buộc');
      hasErrors = true;
  } else if (username.length < 3) {
      showFieldError('username', 'Tên đăng nhập phải có ít nhất 3 ký tự');
      hasErrors = true;
  }
  
  if (!email) {
      showFieldError('email', 'Email là bắt buộc');
      hasErrors = true;
  } else if (!validateEmail(email)) {
      showFieldError('email', 'Email không hợp lệ');
      hasErrors = true;
  }
  
  if (!password) {
      showFieldError('password', 'Mật khẩu là bắt buộc');
      hasErrors = true;
  } else if (password.length < 6) {
      showFieldError('password', 'Mật khẩu phải có ít nhất 6 ký tự');
      hasErrors = true;
  }
  
  if (!confirmPassword) {
      showFieldError('confirm-password', 'Vui lòng xác nhận mật khẩu');
      hasErrors = true;
  } else if (password !== confirmPassword) {
      showFieldError('confirm-password', 'Mật khẩu không khớp');
      hasErrors = true;
  }
  
  if (hasErrors) {
      return;
  }
  
  if (!registerCaptchaSuccess) {
      showResult('Vui lòng xác nhận reCAPTCHA', false);
      return;
  }
  
  // Get the reCAPTCHA token
  const recaptchaToken = grecaptcha.getResponse();
  
  showLoading(true);
  
  try {
      const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              firstName: firstName,
              lastName: lastName,
              username: username,
              email: email,
              password: password,
              recaptchaToken: recaptchaToken  // Add this line
          })
      });
      
      const data = await response.json();
      
      if (response.ok) {
          // Success - show the message from your Python backend
          showResult(data.message || 'Đăng ký thành công!', true);
          // Clear form
          document.getElementById('register-firstName').value = '';
          document.getElementById('register-lastName').value = '';
          document.getElementById('register-username').value = '';
          document.getElementById('register-email').value = '';
          document.getElementById('register-password').value = '';
          document.getElementById('register-confirm-password').value = '';
      } else {
          // Error - show the error message from your Python backend
          showResult(data.error || 'Đăng ký thất bại. Vui lòng thử lại.', false);
      }
  } catch (error) {
      console.error('Registration error:', error);
      showResult('Lỗi mạng. Vui lòng kiểm tra kết nối và thử lại.', false);
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