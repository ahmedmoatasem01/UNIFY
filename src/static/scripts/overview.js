/**
 * Overview Page JavaScript
 * Handles interactivity, animations, and dynamic content updates
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all overview page features
    initializeStatistics();
    initializeScheduleInteraction();
    initializeNotifications();
    initializeQuickActions();
    initializeProgressAnimation();
    initializePageObservers();
});

// ===== STATISTICS =====
function initializeStatistics() {
    const statCards = document.querySelectorAll('.stat-card');
    
    // Add hover ripple effect
    statCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.animation = 'none';
            setTimeout(() => {
                card.style.animation = '';
            }, 10);
        });
    });

    // Animate stat numbers on page load
    animateStatNumbers();
}

function animateStatNumbers() {
    const statNumbers = document.querySelectorAll('.stat-content h3');
    
    statNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent) || 0;
        const duration = 1500; // ms
        const start = 0;
        const increment = finalValue / (duration / 16); // 60fps
        let current = start;

        const counter = setInterval(() => {
            current += increment;
            if (current >= finalValue) {
                element.textContent = finalValue;
                clearInterval(counter);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    });
}

// ===== SCHEDULE =====
function initializeScheduleInteraction() {
    const scheduleItems = document.querySelectorAll('.schedule-item');
    
    scheduleItems.forEach((item, index) => {
        // Stagger animation
        item.style.animationDelay = `${index * 0.1}s`;
        
        // Add click to expand/collapse
        item.addEventListener('click', (e) => {
            if (!e.target.closest('a')) {
                item.classList.toggle('expanded');
            }
        });

        // Add tooltip on hover for truncated text
        const details = item.querySelector('.schedule-details');
        if (details) {
            item.addEventListener('mouseenter', () => {
                if (details.scrollHeight > details.offsetHeight) {
                    addTooltip(details);
                }
            });
        }
    });

    // Handle schedule refresh
    const dateInputs = document.querySelectorAll('[data-schedule-date]');
    dateInputs.forEach(input => {
        input.addEventListener('change', () => {
            refreshScheduleData();
        });
    });
}

function refreshScheduleData() {
    // Placeholder for future API call to refresh schedule
    console.log('Schedule refresh triggered');
}

// ===== NOTIFICATIONS =====
function initializeNotifications() {
    const notificationItems = document.querySelectorAll('.notification-item');
    const notificationBadge = document.querySelector('.notification-badge');
    
    // Mark notification as read on click
    notificationItems.forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('a')) {
                markNotificationAsRead(item);
            }
        });

        // Add swipe-to-dismiss on mobile
        let startX = 0;
        item.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });

        item.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            if (startX - endX > 100) {
                dismissNotification(item);
            }
        });
    });

    // Handle "View all notifications" link
    const viewAllLink = document.querySelector('.view-all-link');
    if (viewAllLink) {
        viewAllLink.addEventListener('click', (e) => {
            e.preventDefault();
            navigateToNotifications();
        });
    }

    // Auto-refresh notifications
    setInterval(refreshNotifications, 30000); // Every 30 seconds
}

function markNotificationAsRead(notificationElement) {
    // Remove unread class
    notificationElement.classList.remove('unread');
    
    // Hide the notification dot
    const dot = notificationElement.querySelector('.notification-dot');
    if (dot) {
        dot.style.opacity = '0';
        setTimeout(() => dot.remove(), 300);
    }

    // Update badge count
    updateNotificationBadge();

    // Send to server (placeholder)
    const notificationId = notificationElement.getAttribute('data-notification-id');
    if (notificationId) {
        fetch(`/api/notifications/${notificationId}/read`, { method: 'PUT' })
            .catch(err => console.error('Error marking notification as read:', err));
    }
}

function dismissNotification(notificationElement) {
    notificationElement.style.animation = 'slideOut 0.3s ease-out forwards';
    setTimeout(() => {
        notificationElement.remove();
        updateNotificationBadge();
    }, 300);

    // Send to server (placeholder)
    const notificationId = notificationElement.getAttribute('data-notification-id');
    if (notificationId) {
        fetch(`/api/notifications/${notificationId}/dismiss`, { method: 'DELETE' })
            .catch(err => console.error('Error dismissing notification:', err));
    }
}

function updateNotificationBadge() {
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    const badge = document.querySelector('.notification-badge');
    
    if (badge) {
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = 'inline-flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

function refreshNotifications() {
    // Placeholder for future API call to refresh notifications
    console.log('Notifications refresh triggered');
}

function navigateToNotifications() {
    window.location.href = '/notifications';
}

// ===== QUICK ACTIONS =====
function initializeQuickActions() {
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach((btn, index) => {
        // Add stagger animation
        btn.style.animationDelay = `${index * 0.05}s`;

        // Add click handlers
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            handleQuickAction(btn);
        });

        // Add ripple effect on click
        btn.addEventListener('click', (e) => {
            createRipple(e, btn);
        });
    });
}

function handleQuickAction(button) {
    const actionText = button.querySelector('span').textContent.toLowerCase();
    
    const actions = {
        'add course': () => window.location.href = '/courses/add',
        'new event': () => window.location.href = '/calendar/new-event',
        'create note': () => openNoteModal(),
        'ai assistant': () => openAIAssistant(),
        'new task': () => window.location.href = '/tasks/new',
        'view courses': () => window.location.href = '/courses'
    };

    const action = actions[actionText] || (() => console.log('Action:', actionText));
    action();
}

function openNoteModal() {
    // Placeholder for note creation modal
    console.log('Note modal should open');
    // In a real app, this would open a modal component
}

function openAIAssistant() {
    // Placeholder for AI assistant
    console.log('AI Assistant should open');
    // In a real app, this would open an AI chat interface
}

function createRipple(e, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// ===== PROGRESS ANIMATION =====
function initializeProgressAnimation() {
    const progressBars = document.querySelectorAll('.progress-fill');
    const gpaDisplay = document.querySelector('.gpa-value');

    // Animate progress bars
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
            bar.style.width = targetWidth;
        }, 100);
    });

    // Animate GPA number
    if (gpaDisplay) {
        const finalGPA = parseFloat(gpaDisplay.textContent);
        animateValue(gpaDisplay, 0, finalGPA, 1500, 2);
    }
}

function animateValue(element, start, end, duration, decimals) {
    const increment = (end - start) / (duration / 16);
    let current = start;

    const counter = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            element.textContent = end.toFixed(decimals);
            clearInterval(counter);
        } else {
            element.textContent = current.toFixed(decimals);
        }
    }, 16);
}

// ===== PAGE OBSERVERS =====
function initializePageObservers() {
    // Observe cards for fade-in animation
    const cards = document.querySelectorAll('.card, .stat-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => observer.observe(card));

    // Handle window resize for responsive behavior
    window.addEventListener('resize', debounce(() => {
        handleResizeChanges();
    }, 250));
}

function handleResizeChanges() {
    const width = window.innerWidth;
    
    // Adjust grid layout if needed
    if (width <= 768) {
        console.log('Mobile layout activated');
    } else {
        console.log('Desktop layout activated');
    }
}

// ===== UTILITY FUNCTIONS =====
function debounce(func, delay) {
    let timeoutId;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeoutId);
            func(...args);
        };
        clearTimeout(timeoutId);
        timeoutId = setTimeout(later, delay);
    };
}

function addTooltip(element) {
    // Placeholder for tooltip functionality
    console.log('Tooltip added to:', element);
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', (e) => {
    // Ctrl+K or Cmd+K to open quick actions search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openQuickSearch();
    }

    // Escape to close any open modals
    if (e.key === 'Escape') {
        closeAllModals();
    }
});

function openQuickSearch() {
    console.log('Quick search should open');
    // Placeholder for quick search functionality
}

function closeAllModals() {
    document.querySelectorAll('[data-modal]').forEach(modal => {
        modal.style.display = 'none';
    });
}

// ===== EXPORT FOR TESTING =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeStatistics,
        initializeScheduleInteraction,
        initializeNotifications,
        initializeQuickActions,
        initializeProgressAnimation,
        markNotificationAsRead,
        dismissNotification,
        handleQuickAction,
        debounce
    };
}
