// Deadline Notifications JavaScript

let currentFilter = 'all';
let currentView = 'list';
let deadlines = [];
let userPreferences = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeFilters();
    initializeViewToggle();
    loadDeadlines();
    loadPreferences();
});

// Filter initialization
function initializeFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderDeadlines();
        });
    });
}

// View toggle initialization
function initializeViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    viewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            viewButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            toggleView();
        });
    });
}

// Toggle between list and calendar view
function toggleView() {
    const listView = document.getElementById('list-view');
    const calendarView = document.getElementById('calendar-view');
    
    if (currentView === 'list') {
        listView.style.display = 'block';
        calendarView.style.display = 'none';
        renderDeadlines();
    } else {
        listView.style.display = 'none';
        calendarView.style.display = 'block';
        renderCalendar();
    }
}

// Load deadlines from API
async function loadDeadlines() {
    try {
        const response = await fetch('/deadline-notifications/api/upcoming?limit=100');
        if (!response.ok) throw new Error('Failed to load deadlines');
        
        deadlines = await response.json();
        updateStatistics();
        renderDeadlines();
    } catch (error) {
        console.error('Error loading deadlines:', error);
        showError('Failed to load deadlines. Please try again.');
    }
}

// Render deadlines list
function renderDeadlines() {
    const container = document.getElementById('deadlines-list');
    
    if (!deadlines || deadlines.length === 0) {
        container.innerHTML = '';
        document.getElementById('empty-state').style.display = 'block';
        return;
    }
    
    document.getElementById('empty-state').style.display = 'none';
    
    // Filter deadlines
    let filteredDeadlines = deadlines;
    if (currentFilter !== 'all') {
        filteredDeadlines = deadlines.filter(d => {
            if (currentFilter === 'upcoming') {
                return d.Status === 'active' && new Date(d.Deadline_Date) > new Date();
            } else if (currentFilter === 'urgent') {
                const deadlineDate = new Date(d.Deadline_Date);
                const now = new Date();
                const hoursUntil = (deadlineDate - now) / (1000 * 60 * 60);
                return d.Status === 'active' && hoursUntil <= 24 && hoursUntil > 0;
            } else if (currentFilter === 'overdue') {
                return d.Status === 'overdue' || (new Date(d.Deadline_Date) < new Date() && d.Status === 'active');
            } else if (currentFilter === 'completed') {
                return d.Status === 'completed';
            }
            return true;
        });
    }
    
    if (filteredDeadlines.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fa-solid fa-check-circle"></i><h3>No deadlines found</h3><p>Try selecting a different filter.</p></div>';
        return;
    }
    
    // Sort by deadline date
    filteredDeadlines.sort((a, b) => new Date(a.Deadline_Date) - new Date(b.Deadline_Date));
    
    container.innerHTML = filteredDeadlines.map(deadline => createDeadlineCard(deadline)).join('');
    
    // Attach event listeners
    attachEventListeners();
}

// Create deadline card HTML
function createDeadlineCard(deadline) {
    const deadlineDate = new Date(deadline.Deadline_Date);
    const now = new Date();
    const hoursUntil = (deadlineDate - now) / (1000 * 60 * 60);
    const daysUntil = hoursUntil / 24;
    
    let urgencyClass = 'medium';
    if (hoursUntil <= 24 && hoursUntil > 0) {
        urgencyClass = 'urgent';
    } else if (hoursUntil <= 72 && hoursUntil > 24) {
        urgencyClass = 'high';
    } else if (hoursUntil > 72) {
        urgencyClass = 'low';
    }
    
    if (deadline.Status === 'overdue' || (deadlineDate < now && deadline.Status === 'active')) {
        urgencyClass = 'urgent';
    }
    
    const countdownText = getCountdownText(deadlineDate, now);
    const typeIcon = getTypeIcon(deadline.Deadline_Type);
    
    return `
        <div class="deadline-item ${urgencyClass} ${deadline.Status}" data-id="${deadline.Notification_ID}">
            <div class="deadline-icon">
                <i class="${typeIcon}"></i>
            </div>
            <div class="deadline-content">
                <div class="deadline-header">
                    <h3 class="deadline-title">${escapeHtml(deadline.Title)}</h3>
                    <div class="deadline-actions">
                        ${deadline.Status === 'active' ? `
                            <button class="deadline-action-btn complete-btn" onclick="markComplete(${deadline.Notification_ID})">
                                <i class="fa-solid fa-check"></i> Complete
                            </button>
                        ` : ''}
                        <button class="deadline-action-btn delete-btn" onclick="deleteDeadline(${deadline.Notification_ID})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="deadline-meta">
                    <span class="deadline-type-badge ${deadline.Deadline_Type}">${deadline.Deadline_Type}</span>
                    <span class="deadline-meta-item">
                        <i class="fa-solid fa-calendar"></i>
                        ${formatDate(deadlineDate)}
                    </span>
                    <span class="deadline-meta-item deadline-countdown">
                        <i class="fa-solid fa-clock"></i>
                        ${countdownText}
                    </span>
                    ${deadline.Priority ? `
                        <span class="deadline-meta-item">
                            <i class="fa-solid fa-flag"></i>
                            ${deadline.Priority}
                        </span>
                    ` : ''}
                </div>
                ${deadline.Description ? `
                    <div class="deadline-description">${escapeHtml(deadline.Description)}</div>
                ` : ''}
            </div>
        </div>
    `;
}

// Get countdown text
function getCountdownText(deadlineDate, now) {
    const diff = deadlineDate - now;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    
    if (diff < 0) {
        const overdueHours = Math.abs(hours);
        const overdueDays = Math.floor(overdueHours / 24);
        if (overdueDays > 0) {
            return `${overdueDays} day${overdueDays > 1 ? 's' : ''} overdue`;
        }
        return `${overdueHours} hour${overdueHours > 1 ? 's' : ''} overdue`;
    }
    
    if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} left`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} left`;
    } else {
        const minutes = Math.floor(diff / (1000 * 60));
        return `${minutes} minute${minutes > 1 ? 's' : ''} left`;
    }
}

// Get type icon
function getTypeIcon(type) {
    const icons = {
        'task': 'fa-solid fa-list-check',
        'assignment': 'fa-solid fa-file-alt',
        'exam': 'fa-solid fa-clipboard-check',
        'project': 'fa-solid fa-folder-open',
        'calendar': 'fa-solid fa-calendar'
    };
    return icons[type] || 'fa-solid fa-clock';
}

// Format date
function formatDate(date) {
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Update statistics
function updateStatistics() {
    const now = new Date();
    
    const urgent = deadlines.filter(d => {
        if (d.Status !== 'active') return false;
        const deadlineDate = new Date(d.Deadline_Date);
        const hoursUntil = (deadlineDate - now) / (1000 * 60 * 60);
        return hoursUntil <= 24 && hoursUntil > 0;
    }).length;
    
    const upcoming = deadlines.filter(d => {
        if (d.Status !== 'active') return false;
        const deadlineDate = new Date(d.Deadline_Date);
        return deadlineDate > now;
    }).length;
    
    const completed = deadlines.filter(d => d.Status === 'completed').length;
    
    document.getElementById('urgent-count').textContent = urgent;
    document.getElementById('upcoming-count').textContent = upcoming;
    document.getElementById('completed-count').textContent = completed;
    document.getElementById('total-count').textContent = deadlines.length;
}

// Mark deadline as complete
async function markComplete(notificationId) {
    try {
        const response = await fetch(`/deadline-notifications/api/${notificationId}/complete`, {
            method: 'PUT'
        });
        
        if (!response.ok) throw new Error('Failed to mark deadline as complete');
        
        // Reload deadlines
        await loadDeadlines();
    } catch (error) {
        console.error('Error marking deadline as complete:', error);
        showError('Failed to mark deadline as complete. Please try again.');
    }
}

// Delete deadline
async function deleteDeadline(notificationId) {
    if (!confirm('Are you sure you want to delete this deadline notification?')) {
        return;
    }
    
    try {
        const response = await fetch(`/deadline-notifications/api/${notificationId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete deadline');
        
        // Reload deadlines
        await loadDeadlines();
    } catch (error) {
        console.error('Error deleting deadline:', error);
        showError('Failed to delete deadline. Please try again.');
    }
}

// Sync deadlines
async function syncDeadlines() {
    try {
        const syncBtn = document.querySelector('.sync-deadlines-btn');
        syncBtn.disabled = true;
        syncBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Syncing...';
        
        const response = await fetch('/deadline-notifications/api/check-deadlines', {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed to sync deadlines');
        
        const result = await response.json();
        
        // Reload deadlines
        await loadDeadlines();
        
        showSuccess(`Synced ${result.synced.total} deadlines (${result.synced.tasks} tasks, ${result.synced.calendar} calendar events)`);
    } catch (error) {
        console.error('Error syncing deadlines:', error);
        showError('Failed to sync deadlines. Please try again.');
    } finally {
        const syncBtn = document.querySelector('.sync-deadlines-btn');
        syncBtn.disabled = false;
        syncBtn.innerHTML = '<i class="fa-solid fa-sync"></i> Sync Deadlines';
    }
}

// Load preferences
async function loadPreferences() {
    try {
        // Get user_id from session or extract from API response
        const response = await fetch('/deadline-notifications/api/preferences/1'); // TODO: Get actual user_id
        if (response.ok) {
            const prefs = await response.json();
            if (prefs && prefs.length > 0) {
                userPreferences = prefs[0];
            }
        }
    } catch (error) {
        console.error('Error loading preferences:', error);
    }
}

// Open settings modal
function openSettings() {
    const modal = document.getElementById('settings-modal');
    modal.style.display = 'flex';
    
    // Load current preferences if available
    if (userPreferences) {
        // Set alert intervals checkboxes
        const intervals = userPreferences.Alert_Intervals_List || [4320, 1440, 60];
        document.getElementById('interval-7d').checked = intervals.includes(10080);
        document.getElementById('interval-3d').checked = intervals.includes(4320);
        document.getElementById('interval-1d').checked = intervals.includes(1440);
        document.getElementById('interval-12h').checked = intervals.includes(720);
        document.getElementById('interval-1h').checked = intervals.includes(60);
        document.getElementById('interval-30m').checked = intervals.includes(30);
        
        // Set notification channels
        document.getElementById('in-app-enabled').checked = userPreferences.In_App_Enabled !== false;
        document.getElementById('email-enabled').checked = userPreferences.Email_Enabled === true;
        
        // Set quiet hours
        if (userPreferences.Quiet_Hours_Start) {
            document.getElementById('quiet-hours-start').value = userPreferences.Quiet_Hours_Start;
        }
        if (userPreferences.Quiet_Hours_End) {
            document.getElementById('quiet-hours-end').value = userPreferences.Quiet_Hours_End;
        }
    }
}

// Close settings modal
function closeSettings() {
    const modal = document.getElementById('settings-modal');
    modal.style.display = 'none';
}

// Save settings
async function saveSettings() {
    try {
        // Collect alert intervals
        const intervals = [];
        if (document.getElementById('interval-7d').checked) intervals.push(10080);
        if (document.getElementById('interval-3d').checked) intervals.push(4320);
        if (document.getElementById('interval-1d').checked) intervals.push(1440);
        if (document.getElementById('interval-12h').checked) intervals.push(720);
        if (document.getElementById('interval-1h').checked) intervals.push(60);
        if (document.getElementById('interval-30m').checked) intervals.push(30);
        
        // Default intervals if none selected
        if (intervals.length === 0) {
            intervals.push(1440, 60); // 1 day, 1 hour
        }
        
        const preferences = {
            Deadline_Type: 'all',
            Alert_Intervals: intervals,
            Email_Enabled: document.getElementById('email-enabled').checked,
            In_App_Enabled: document.getElementById('in-app-enabled').checked,
            Quiet_Hours_Start: document.getElementById('quiet-hours-start').value,
            Quiet_Hours_End: document.getElementById('quiet-hours-end').value
        };
        
        const response = await fetch('/deadline-notifications/api/preferences/1', { // TODO: Get actual user_id
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(preferences)
        });
        
        if (!response.ok) throw new Error('Failed to save preferences');
        
        userPreferences = await response.json();
        closeSettings();
        showSuccess('Settings saved successfully');
    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings. Please try again.');
    }
}

// Render calendar view
function renderCalendar() {
    // Simple calendar implementation
    const container = document.getElementById('calendar-container');
    container.innerHTML = '<p>Calendar view coming soon. Please use the list view for now.</p>';
}

// Attach event listeners
function attachEventListeners() {
    // Add any additional event listeners here
}

// Show success message
function showSuccess(message) {
    // Simple alert for now - can be replaced with a toast notification
    alert(message);
}

// Show error message
function showError(message) {
    // Simple alert for now - can be replaced with a toast notification
    alert(message);
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('settings-modal');
    if (e.target === modal) {
        closeSettings();
    }
});

