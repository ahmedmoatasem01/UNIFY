/**
 * Global Theme Toggle Script
 * Works across all pages in the Unify application
 */

(function() {
    'use strict';

    // Theme toggle functionality
    function initThemeToggle() {
        const themeToggle = document.getElementById('cr-theme-toggle');
        if (!themeToggle) return;

        // Apply saved theme on page load
        function applySavedTheme() {
            const saved = localStorage.getItem('unify_theme') || 'dark';
            const isLight = saved === 'light';
            
            if (isLight) {
                document.body.classList.add('cr-light-mode');
                document.documentElement.setAttribute('data-theme', 'light');
                themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
            } else {
                document.body.classList.remove('cr-light-mode');
                document.documentElement.setAttribute('data-theme', 'dark');
                themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
            }
        }

        // Toggle theme on click
        themeToggle.addEventListener('click', () => {
            const isLight = document.body.classList.contains('cr-light-mode');
            
            if (isLight) {
                document.body.classList.remove('cr-light-mode');
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('unify_theme', 'dark');
                themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
            } else {
                document.body.classList.add('cr-light-mode');
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('unify_theme', 'light');
                themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
            }
        });

        // Apply theme on page load
        applySavedTheme();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeToggle);
    } else {
        initThemeToggle();
    }
})();

