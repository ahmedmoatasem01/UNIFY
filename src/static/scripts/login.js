
document.addEventListener('DOMContentLoaded', () => {
    // ===== Tabs (Login / Register) =====
    const tabButtons = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));

            btn.classList.add('active');
            const target = document.getElementById(btn.dataset.tab);
            if (target) target.classList.add('active');
        });
    });

    // ===== Cartoon characters & eyes =====
    const characters = document.querySelector('.characters');
    const eyes = document.querySelectorAll('.eye');
    const loginPasswordInput = document.getElementById('login-password');

    // Move pupils towards mouse position anywhere on screen
    function updateEyeDirection(event) {
        if (!characters || eyes.length === 0) return;

        const rect = characters.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        const dx = event.clientX - centerX;
        const dy = event.clientY - centerY;

        // Normalize to [-1, 1]
        const nx = Math.max(-1, Math.min(1, dx / (rect.width / 2)));
        const ny = Math.max(-1, Math.min(1, dy / (rect.height / 2)));

        // Scale to pixel offsets
        const offsetX = nx * 8;   // max ±8px
        const offsetY = ny * 4;   // max ±4px

        eyes.forEach(eye => {
            eye.style.setProperty('--pupil-x', offsetX + 'px');
            eye.style.setProperty('--pupil-y', offsetY + 'px');
        });
    }

    // Bounce when password field gets focus
    if (loginPasswordInput) {
        loginPasswordInput.addEventListener('focus', () => {
            if (characters) characters.classList.add('characters-active');
        });

        loginPasswordInput.addEventListener('blur', () => {
            if (characters) characters.classList.remove('characters-active');
            eyes.forEach(eye => {
                eye.style.setProperty('--pupil-x', '0px');
                eye.style.setProperty('--pupil-y', '0px');
            });
        });
    }

    // Global mousemove – track cursor everywhere
    document.addEventListener('mousemove', updateEyeDirection);

    // ===== Show / hide password (Login + Register) =====
    const toggles = document.querySelectorAll('.password-toggle');

    toggles.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input = document.getElementById(targetId);
            if (!input) return;

            const icon = btn.querySelector('i');

            if (input.type === 'password') {
                // Show password
                input.type = 'text';
                if (icon) {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                }
                btn.setAttribute('aria-label', 'Hide password');

                // Close eyes only when showing LOGIN password
                if (characters && targetId === 'login-password') {
                    characters.classList.add('eyes-closed');
                }
            } else {
                // Hide password
                input.type = 'password';
                if (icon) {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
                btn.setAttribute('aria-label', 'Show password');

                if (characters && targetId === 'login-password') {
                    characters.classList.remove('eyes-closed');
                }
            }
        });
    });
});

// ===== Login Form Handler =====
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    const loginBtn = document.getElementById('login-btn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoading = loginBtn.querySelector('.btn-loading');
    
    // Hide error message
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
    
    // Show loading state
    loginBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Login successful - redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Show error message
            errorDiv.textContent = data.error || 'Login failed. Please try again.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'Network error. Please check your connection and try again.';
        errorDiv.style.display = 'block';
    } finally {
        // Reset button state
        loginBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// ===== Register Form Handler =====
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    const errorDiv = document.getElementById('register-error');
    const successDiv = document.getElementById('register-success');
    const registerBtn = document.getElementById('register-btn');
    const btnText = registerBtn.querySelector('.btn-text');
    const btnLoading = registerBtn.querySelector('.btn-loading');
    
    // Hide messages
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';
    errorDiv.textContent = '';
    successDiv.textContent = '';
    
    // Validate password length
    if (password.length < 8) {
        errorDiv.textContent = 'Password must be at least 8 characters long.';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Validate role
    if (!role) {
        errorDiv.textContent = 'Please select a role.';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Show loading state
    registerBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                role: role
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Registration successful
            successDiv.textContent = 'Account created successfully! Redirecting to login...';
            successDiv.style.display = 'block';
            
            // Clear form
            document.getElementById('register-tab').reset();
            
            // Switch to login tab after 2 seconds
            setTimeout(() => {
                document.querySelector('[data-tab="login-tab"]').click();
                successDiv.style.display = 'none';
            }, 2000);
        } else {
            // Show error message
            errorDiv.textContent = data.error || 'Registration failed. Please try again.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Registration error:', error);
        errorDiv.textContent = 'Network error. Please check your connection and try again.';
        errorDiv.style.display = 'block';
    } finally {
        // Reset button state
        registerBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}