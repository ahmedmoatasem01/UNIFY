/**
 * Smart Reminders Dashboard - JavaScript
 * Handles loading, rendering, and managing reminders and alerts
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadRemindersData();
    setupQuickAdd();
    
    // Auto-refresh every 5 minutes
    setInterval(loadRemindersData, 5 * 60 * 1000);
});

/**
 * Load reminders and tasks data from the server
 */
async function loadRemindersData() {
    try {
        // Fetch tasks and calendar events
        const [tasksRes, calendarRes] = await Promise.all([
            fetch('/tasks/api/user'),
            fetch('/calendar/api/user')
        ]);

        const tasks = await tasksRes.json();
        const calendar = calendarRes.ok ? await calendarRes.json() : [];

        renderDashboard(tasks, calendar);
    } catch (error) {
        console.error('Error loading reminders data:', error);
        showError('Failed to load reminders. Please refresh the page.');
    }
}

/**
 * Render the entire dashboard with categorized items
 */
function renderDashboard(tasks, calendarEvents) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

    // Categorize items
    const urgent = [];
    const todayItems = [];
    const weekItems = [];

    // Process tasks
    tasks.forEach(task => {
        if (task.Status === 'completed') return;

        const dueDate = new Date(task.Due_Date);
        const hoursUntilDue = (dueDate - now) / (1000 * 60 * 60);

        const item = {
            type: 'task',
            title: task.Task_Title,
            dueDate: dueDate,
            priority: task.Priority,
            id: task.Task_ID
        };

        // Urgent: due within 24 hours
        if (hoursUntilDue < 24 && hoursUntilDue > 0) {
            urgent.push(item);
        }

        // Today
        if (dueDate >= today && dueDate < new Date(today.getTime() + 24 * 60 * 60 * 1000)) {
            todayItems.push(item);
        }

        // This week
        if (dueDate >= today && dueDate < weekFromNow) {
            weekItems.push(item);
        }
    });

    // Process calendar events
    calendarEvents.forEach(event => {
        const eventDate = new Date(event.Date);
        
        const item = {
            type: 'event',
            title: event.Title,
            dueDate: eventDate,
            priority: 'medium',
            id: event.Event_ID
        };

        // Today
        if (eventDate >= today && eventDate < new Date(today.getTime() + 24 * 60 * 60 * 1000)) {
            todayItems.push(item);
        }

        // This week
        if (eventDate >= today && eventDate < weekFromNow) {
            weekItems.push(item);
        }
    });

    // Update stats
    document.getElementById('urgentCount').textContent = urgent.length;
    document.getElementById('todayCount').textContent = todayItems.length;
    document.getElementById('weekCount').textContent = weekItems.length;
    document.getElementById('priorityCount').textContent = urgent.length;

    // Render sections
    renderPriorityAlerts(urgent);
    renderTodayAgenda(todayItems);
    renderUpcomingTimeline(weekItems);
}

/**
 * Render priority alerts section
 */
function renderPriorityAlerts(items) {
    const container = document.getElementById('priorityAlertsContainer');
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-check-circle"></i>
                <p>No urgent items! You're all caught up.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = items.map(item => {
        const hoursLeft = Math.floor((item.dueDate - new Date()) / (1000 * 60 * 60));
        const icon = item.priority === 'high' ? 'urgent' : 'warning';
        
        return `
            <div class="alert-item ${item.priority === 'high' ? '' : 'warning'}">
                <div class="alert-item-icon ${icon}">
                    <i class="fa-solid fa-${item.priority === 'high' ? 'exclamation-triangle' : 'clock'}"></i>
                </div>
                <div class="alert-item-content">
                    <div class="alert-item-title">${escapeHtml(item.title)}</div>
                    <div class="alert-item-time">
                        ${hoursLeft > 0 ? `Due in ${hoursLeft} hour${hoursLeft !== 1 ? 's' : ''}` : 'Due now!'}
                    </div>
                    <div class="alert-item-actions">
                        <button class="alert-btn alert-btn-primary" onclick="markComplete(${item.id}, '${item.type}')">
                            <i class="fa-solid fa-check"></i> Complete
                        </button>
                        <button class="alert-btn alert-btn-ghost" onclick="viewItem(${item.id}, '${item.type}')">
                            <i class="fa-solid fa-eye"></i> View
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render today's agenda
 */
function renderTodayAgenda(items) {
    const container = document.getElementById('todayAgendaContainer');
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-calendar"></i>
                <p>No items for today</p>
            </div>
        `;
        return;
    }

    // Sort by time
    items.sort((a, b) => a.dueDate - b.dueDate);

    container.innerHTML = items.map(item => `
        <div class="alert-item info">
            <div class="alert-item-icon info">
                <i class="fa-solid fa-${item.type === 'task' ? 'list-check' : 'calendar'}"></i>
            </div>
            <div class="alert-item-content">
                <div class="alert-item-title">${escapeHtml(item.title)}</div>
                <div class="alert-item-time">
                    ${item.dueDate.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Render upcoming timeline
 */
function renderUpcomingTimeline(items) {
    const container = document.getElementById('upcomingTimeline');
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-inbox"></i>
                <p>No upcoming items this week</p>
            </div>
        `;
        return;
    }

    // Sort by date
    items.sort((a, b) => a.dueDate - b.dueDate);

    container.innerHTML = items.slice(0, 10).map(item => `
        <div class="timeline-item">
            <div class="timeline-marker ${item.priority === 'high' ? 'urgent' : item.priority === 'medium' ? 'warning' : ''}"></div>
            <div class="timeline-content">
                <div class="timeline-time">
                    ${item.dueDate.toLocaleDateString('en-US', {weekday: 'short', month: 'short', day: 'numeric'})} 
                    at ${item.dueDate.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}
                </div>
                <div class="timeline-title">${escapeHtml(item.title)}</div>
                <span class="timeline-badge ${item.priority}">${item.priority.toUpperCase()}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Setup quick add form
 */
function setupQuickAdd() {
    document.getElementById('quickAddForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const title = document.getElementById('reminderTitle').value;
        const time = document.getElementById('reminderTime').value;
        const priority = document.getElementById('reminderPriority').value;

        if (!title || !time) {
            showError('Please fill in all fields');
            return;
        }

        try {
            // Create as a task since reminders are derived from tasks
            const response = await fetch('/tasks/api', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    Task_Title: title,
                    Due_Date: time,
                    Priority: priority,
                    Status: 'pending'
                })
            });

            if (response.ok) {
                showSuccess('✅ Reminder created successfully!');
                document.getElementById('quickAddForm').reset();
                await loadRemindersData();
            } else {
                showError('Failed to create reminder');
            }
        } catch (error) {
            console.error('Error creating reminder:', error);
            showError('Error creating reminder');
        }
    });
}

/**
 * Mark task as complete
 */
async function markComplete(id, type) {
    if (type !== 'task') return;

    try {
        const response = await fetch(`/tasks/api/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({Status: 'completed'})
        });

        if (response.ok) {
            showSuccess('✅ Task completed!');
            await loadRemindersData();
        } else {
            showError('Failed to complete task');
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showError('Error completing task');
    }
}

/**
 * View item details
 */
function viewItem(id, type) {
    if (type === 'task') {
        window.location.href = '/tasks';
    } else if (type === 'event') {
        window.location.href = '/calendar';
    }
}

/**
 * Utility: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show success message
 */
function showSuccess(message) {
    alert(message); // TODO: Replace with toast notification
}

/**
 * Show error message
 */
function showError(message) {
    alert(message); // TODO: Replace with toast notification
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        const response = await fetch('/auth/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/login';
    }
}

