// Settings page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initSettingsNavigation();
    initToggleSwitches();
    initFormSubmissions();
    initThemeSelector();
});

function initSettingsNavigation() {
    const navLinks = document.querySelectorAll('.settings-nav-link');
    const panels = document.querySelectorAll('.settings-panel');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and panels
            navLinks.forEach(l => l.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            // Add active class to clicked link
            this.classList.add('active');

            // Show corresponding panel
            const section = this.getAttribute('data-section');
            const targetPanel = document.getElementById(`${section}-panel`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// Toggle switches
function initToggleSwitches() {
    const toggles = document.querySelectorAll('.toggle-switch input');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const setting = this.closest('.setting-item');
            const settingName = setting.querySelector('h3').textContent;
            
            // Save setting (would make API call in production)
            saveSetting(settingName, this.checked);
        });
    });
}

// Form submissions
function initFormSubmissions() {
    const forms = document.querySelectorAll('.panel-body');
    
    forms.forEach(form => {
        const saveButton = form.querySelector('.btn-primary');
        if (saveButton) {
            saveButton.addEventListener('click', function(e) {
                e.preventDefault();
                const panel = this.closest('.settings-panel');
                const panelId = panel.id;
                
                // Collect form data
                const formData = collectFormData(panel);
                
                // Save settings
                saveSettings(panelId, formData);
            });
        }
    });
}

// Collect form data from a panel
function collectFormData(panel) {
    const formData = {};
    
    // Get all form controls
    const inputs = panel.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            formData[input.name || input.id] = input.checked;
        } else if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else {
            formData[input.name || input.id] = input.value;
        }
    });
    
    return formData;
}

// Save settings via API
async function saveSettings(panelId, formData) {
    try {
        const response = await fetch('/api/settings/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                panel: panelId,
                data: formData
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showNotification('Settings saved successfully!', 'success');
        } else {
            showNotification('Failed to save settings. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('An error occurred. Please try again.', 'error');
    }
}

async function saveSetting(name, value) {
    try {
        await fetch('/api/settings/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                setting: name,
                value: value
            })
        });
    } catch (error) {
        console.error('Error saving setting:', error);
    }
}

function initThemeSelector() {
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    
    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const theme = this.value;
            applyTheme(theme);
            localStorage.setItem('theme', theme);
            saveSetting('theme', theme);
        });
    });
    
    // Color blind mode toggle
    const colorblindToggle = document.getElementById('colorblind-mode') || 
                             document.querySelector('input[name="colorblind_mode"]');
    if (colorblindToggle) {
        colorblindToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('colorblind-mode');
                localStorage.setItem('colorblind-mode', 'true');
            } else {
                document.body.classList.remove('colorblind-mode');
                localStorage.setItem('colorblind-mode', 'false');
            }
            saveSetting('colorblind-mode', this.checked);
        });
    }
    
    // Dyslexia font toggle
    const dyslexiaToggle = document.getElementById('dyslexia-font') || 
                           document.querySelector('input[name="dyslexia_font"]');
    if (dyslexiaToggle) {
        dyslexiaToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dyslexia-font');
                localStorage.setItem('dyslexia-font', 'true');
            } else {
                document.body.classList.remove('dyslexia-font');
                localStorage.setItem('dyslexia-font', 'false');
            }
            saveSetting('dyslexia-font', this.checked);
        });
    }
}

// Apply theme - uses CSS variables from style.css
function applyTheme(theme) {
    const body = document.body;
    const root = document.documentElement;
    
    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark', 'theme-auto');

    if (theme === 'dark') {
        body.classList.add('theme-dark');
        root.setAttribute('data-theme', 'dark');
    } else if (theme === 'light') {
        body.classList.add('theme-light');
        root.setAttribute('data-theme', 'light');
    } else {
        body.classList.add('theme-auto');

        // Current time logic
        const now = new Date();
        const hour = now.getHours();  // 0–23

        let autoTheme;

        if (hour >= 17) {
            // After 5pm → force dark theme
            autoTheme = 'dark';
        } else {
            // Before 5pm → use system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            autoTheme = prefersDark ? 'dark' : 'light';
        }

        root.setAttribute('data-theme', autoTheme);
    }
}

// Show notification
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#43e97b' : '#ef4444'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

