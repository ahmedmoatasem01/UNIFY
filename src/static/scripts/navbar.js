/**
 * Navbar Dropdown Functionality
 * Handles AI Assistant dropdown menu interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // AI Assistant Dropdown
    const aiDropdownToggle = document.getElementById('aiDropdownToggle');
    const aiDropdownMenu = document.getElementById('aiDropdownMenu');
    const aiDropdownParent = aiDropdownToggle?.closest('.nav-dropdown');
    
    if (aiDropdownToggle && aiDropdownMenu) {
        // Toggle dropdown on click
        aiDropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle active class
            aiDropdownParent.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!aiDropdownParent.contains(e.target)) {
                aiDropdownParent.classList.remove('active');
            }
        });
        
        // Close dropdown when clicking a link inside
        const dropdownLinks = aiDropdownMenu.querySelectorAll('a:not(#clearHistoryNav)');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', function() {
                aiDropdownParent.classList.remove('active');
            });
        });
    }
    
    // Clear History from navbar
    const clearHistoryNav = document.getElementById('clearHistoryNav');
    if (clearHistoryNav) {
        clearHistoryNav.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!confirm('Are you sure you want to clear your conversation history? This cannot be undone.')) {
                return;
            }
            
            try {
                const response = await fetch('/ai-assistant/clear-history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification('Chat history cleared successfully!', 'success');
                    
                    // If on AI Assistant page, reload
                    if (window.location.pathname.includes('ai-assistant')) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    showNotification(data.error || 'Failed to clear history', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Failed to clear history', 'error');
            }
            
            // Close dropdown
            if (aiDropdownParent) {
                aiDropdownParent.classList.remove('active');
            }
        });
    }
});

// Notification helper
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `navbar-notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#22c55e' : '#ef4444'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slideInRight 0.3s ease;
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
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
