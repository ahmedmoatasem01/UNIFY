// Accessibility features JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initAccessibility();
    loadSavedPreferences();
});

function initAccessibility() {
    // Color-blind mode toggle - works on all pages
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
        });
    }

    // Dyslexia font toggle - works on all pages
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
        });
    }

    // Theme switching - works on all pages
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            applyTheme(this.value);
            localStorage.setItem('theme', this.value);
        });
    });

    // Listen for system theme changes when in auto mode
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', function() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'auto') {
            applyTheme('auto');
        }
    });
}

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
        // Auto - use system preference
        body.classList.add('theme-auto');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
}

function loadSavedPreferences() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // Update radio button if on settings page
    const themeRadio = document.querySelector(`input[name="theme"][value="${savedTheme}"]`);
    if (themeRadio) {
        themeRadio.checked = true;
    }
    
    // Load color blind mode
    const colorblindMode = localStorage.getItem('colorblind-mode') === 'true';
    if (colorblindMode) {
        document.body.classList.add('colorblind-mode');
        const colorblindCheckbox = document.getElementById('colorblind-mode') || 
                                   document.querySelector('input[name="colorblind_mode"]');
        if (colorblindCheckbox) {
            colorblindCheckbox.checked = true;
        }
    }
    
    // Load dyslexia font
    const dyslexiaFont = localStorage.getItem('dyslexia-font') === 'true';
    if (dyslexiaFont) {
        document.body.classList.add('dyslexia-font');
        const dyslexiaCheckbox = document.getElementById('dyslexia-font') || 
                                  document.querySelector('input[name="dyslexia_font"]');
        if (dyslexiaCheckbox) {
            dyslexiaCheckbox.checked = true;
        }
    }
}

