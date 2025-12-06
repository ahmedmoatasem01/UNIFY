
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
