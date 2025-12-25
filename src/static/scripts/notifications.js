/**
 * Notification System JavaScript
 * Handles notification bell icon, dropdown, and real-time updates
 */

(function() {
    'use strict';

    let notificationDropdown = null;
    let unreadCount = 0;

    function initNotifications() {
        const notificationBtn = document.getElementById('cr-notification-toggle');
        const notificationBadge = document.getElementById('cr-notification-badge');
        
        if (!notificationBtn) return;

        // Create notification dropdown
        createNotificationDropdown();

        // Load initial notifications
        loadNotifications();

        // Click handler for notification button
        notificationBtn.addEventListener('click', toggleNotificationDropdown);

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (notificationDropdown && !notificationDropdown.contains(e.target) && !notificationBtn.contains(e.target)) {
                hideNotificationDropdown();
            }
        });

        // Auto-refresh notifications every 30 seconds
        setInterval(loadNotifications, 30000);
    }

    function createNotificationDropdown() {
        notificationDropdown = document.createElement('div');
        notificationDropdown.id = 'cr-notification-dropdown';
        notificationDropdown.className = 'cr-notification-dropdown';
        notificationDropdown.innerHTML = `
            <div class="cr-notification-dropdown-header">
                <h3>Notifications</h3>
                <button id="mark-all-read-btn" class="cr-mark-all-read-btn">Mark all as read</button>
            </div>
            <div class="cr-notification-dropdown-list" id="notification-list">
                <div class="cr-notification-loading">Loading notifications...</div>
            </div>
            <div class="cr-notification-dropdown-footer">
                <a href="/notifications/" class="cr-view-all-link">View all notifications</a>
            </div>
        `;
        document.body.appendChild(notificationDropdown);

        // Mark all as read handler
        const markAllBtn = document.getElementById('mark-all-read-btn');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', markAllAsRead);
        }
    }

    function toggleNotificationDropdown(e) {
        e.stopPropagation();
        if (notificationDropdown.classList.contains('active')) {
            hideNotificationDropdown();
        } else {
            showNotificationDropdown();
            loadNotifications(); // Refresh when opening
        }
    }

    function showNotificationDropdown() {
        if (notificationDropdown) {
            notificationDropdown.classList.add('active');
            positionDropdown();
        }
    }

    function hideNotificationDropdown() {
        if (notificationDropdown) {
            notificationDropdown.classList.remove('active');
        }
    }

    function positionDropdown() {
        const notificationBtn = document.getElementById('cr-notification-toggle');
        if (!notificationBtn || !notificationDropdown) return;

        const rect = notificationBtn.getBoundingClientRect();
        notificationDropdown.style.top = `${rect.bottom + 8}px`;
        notificationDropdown.style.right = `${window.innerWidth - rect.right}px`;
    }

    async function loadNotifications() {
        try {
            const response = await fetch('/notifications/unread');
            if (!response.ok) throw new Error('Failed to load notifications');
            
            const data = await response.json();
            unreadCount = data.count || 0;
            
            updateNotificationBadge();
            updateNotificationList(data.notifications || []);
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    function updateNotificationBadge() {
        const badge = document.getElementById('cr-notification-badge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    function updateNotificationList(notifications) {
        const list = document.getElementById('notification-list');
        if (!list) return;

        if (notifications.length === 0) {
            list.innerHTML = '<div class="cr-notification-empty">No new notifications</div>';
            return;
        }

        list.innerHTML = notifications.map(notif => {
            const timeAgo = formatTimeAgo(notif.created_at);
            const iconClass = getNotificationIcon(notif.type);
            const priorityClass = notif.priority || 'medium';
            
            return `
                <div class="cr-notification-item ${notif.is_read ? '' : 'unread'} priority-${priorityClass}" 
                     data-notification-id="${notif.notification_id}"
                     ${notif.action_url ? `onclick="window.location.href='${notif.action_url}'"` : ''}>
                    <div class="cr-notification-icon ${iconClass}">
                        <i class="${getNotificationIconClass(notif.type)}"></i>
                    </div>
                    <div class="cr-notification-content">
                        <h4>${escapeHtml(notif.title)}</h4>
                        <p>${escapeHtml(notif.message)}</p>
                        <span class="cr-notification-time">${timeAgo}</span>
                    </div>
                    ${!notif.is_read ? '<div class="cr-notification-dot"></div>' : ''}
                </div>
            `;
        }).join('');

        // Add click handlers for marking as read
        list.querySelectorAll('.cr-notification-item').forEach(item => {
            item.addEventListener('click', async (e) => {
                const notificationId = item.dataset.notificationId;
                if (notificationId && !item.classList.contains('read')) {
                    await markAsRead(notificationId);
                }
            });
        });
    }

    async function markAsRead(notificationId) {
        try {
            const response = await fetch(`/notifications/${notificationId}/read`, {
                method: 'PUT'
            });
            if (response.ok) {
                loadNotifications(); // Reload to update UI
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async function markAllAsRead() {
        try {
            const response = await fetch('/notifications/mark-all-read', {
                method: 'POST'
            });
            if (response.ok) {
                loadNotifications(); // Reload to update UI
            }
        } catch (error) {
            console.error('Error marking all as read:', error);
        }
    }

    function formatTimeAgo(dateString) {
        if (!dateString) return 'Just now';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            return date.toLocaleDateString();
        } catch {
            return 'Recently';
        }
    }

    function getNotificationIcon(type) {
        const icons = {
            'task': 'fa-tasks',
            'assignment': 'fa-file-alt',
            'grade': 'fa-graduation-cap',
            'announcement': 'fa-bullhorn',
            'message': 'fa-envelope',
            'system': 'fa-info-circle'
        };
        return icons[type] || 'fa-bell';
    }

    function getNotificationIconClass(type) {
        return `fa-solid ${getNotificationIcon(type)}`;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNotifications);
    } else {
        initNotifications();
    }
})();
