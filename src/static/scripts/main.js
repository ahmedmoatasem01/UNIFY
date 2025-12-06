// Main JavaScript file for Unify

document.addEventListener('DOMContentLoaded', function() {
    initMain();
});

function initMain() {
    // Initialize progress bars
    initProgressBars();
    
    // Initialize any other global functionality
    console.log('Unify application initialized');
}

// Initialize progress bars with animation
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill[data-progress]');
    
    progressBars.forEach(bar => {
        const progress = bar.getAttribute('data-progress');
        if (progress) {
            // Animate progress bar
            setTimeout(() => {
                bar.style.width = progress + '%';
            }, 100);
        }
    });
}

// Utility function for formatting dates
function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

// Utility function for formatting time
function formatTime(date) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(date).toLocaleTimeString('en-US', options);
}

