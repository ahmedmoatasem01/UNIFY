/**
 * Study Plans JavaScript
 * Handles all client-side interactions for study plan management
 */

// Global state
let currentStudentId = null;
let currentPlanId = null;
let allPlans = [];
let allTasks = [];
let currentFilter = 'all';

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the detail page or list page
    if (typeof PLAN_ID !== 'undefined') {
        currentPlanId = PLAN_ID;
        initDetailPage();
    } else {
        initListPage();
    }
    
    // Set up event listeners
    setupEventListeners();
});

function initListPage() {
    loadStudyPlans();
    loadCourses();
    setDefaultDates();
}

function initDetailPage() {
    loadPlanDetails();
    loadPlanTasks();
    loadRecommendations();
}

function setupEventListeners() {
    // Create plan button
    const createPlanBtn = document.getElementById('createPlanBtn');
    if (createPlanBtn) {
        createPlanBtn.addEventListener('click', showCreatePlanModal);
    }
    
    // Create plan form
    const createPlanForm = document.getElementById('createPlanForm');
    if (createPlanForm) {
        createPlanForm.addEventListener('submit', handleCreatePlan);
    }
    
    // Add task button
    const addTaskBtn = document.getElementById('addTaskBtn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', showAddTaskModal);
    }
    
    // Add task form
    const addTaskForm = document.getElementById('addTaskForm');
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', handleAddTask);
    }
    
    // Edit task form
    const editTaskForm = document.getElementById('editTaskForm');
    if (editTaskForm) {
        editTaskForm.addEventListener('submit', handleEditTask);
    }
    
    // Filters
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', handleFilterChange);
    }
    
    const courseFilter = document.getElementById('courseFilter');
    if (courseFilter) {
        courseFilter.addEventListener('change', handleFilterChange);
    }
    
    // Task filters
    const taskFilterBtns = document.querySelectorAll('.filter-btn');
    taskFilterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            taskFilterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            filterTasks();
        });
    });
    
    // Adjust plan button
    const adjustPlanBtn = document.getElementById('adjustPlanBtn');
    if (adjustPlanBtn) {
        adjustPlanBtn.addEventListener('click', handleAdjustPlan);
    }
    
    // Refresh recommendations
    const refreshRecommendations = document.getElementById('refreshRecommendations');
    if (refreshRecommendations) {
        refreshRecommendations.addEventListener('click', loadRecommendations);
    }
}

// ============================================================================
// API Calls
// ============================================================================

async function loadStudyPlans() {
    try {
        const response = await fetch('/api/study-plans/student/1'); // Replace with actual student ID
        if (!response.ok) throw new Error('Failed to load study plans');
        
        allPlans = await response.json();
        displayStudyPlans(allPlans);
    } catch (error) {
        console.error('Error loading study plans:', error);
        showError('Failed to load study plans');
    }
}

async function loadPlanDetails() {
    try {
        const response = await fetch(`/api/study-plans/${currentPlanId}`);
        if (!response.ok) throw new Error('Failed to load plan details');
        
        const plan = await response.json();
        displayPlanDetails(plan);
        
        // Load analytics
        const analyticsResponse = await fetch(`/api/study-plans/${currentPlanId}/analytics`);
        if (analyticsResponse.ok) {
            const analytics = await analyticsResponse.json();
            displayAnalytics(analytics);
        }
    } catch (error) {
        console.error('Error loading plan details:', error);
        showError('Failed to load plan details');
    }
}

async function loadPlanTasks() {
    try {
        const response = await fetch(`/api/study-plans/${currentPlanId}/tasks`);
        if (!response.ok) throw new Error('Failed to load tasks');
        
        allTasks = await response.json();
        displayTasks(allTasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
        showError('Failed to load tasks');
    }
}

async function loadRecommendations() {
    try {
        const container = document.getElementById('recommendationsContainer');
        if (!container) return;
        
        container.innerHTML = '<div class="loading">Loading recommendations...</div>';
        
        const response = await fetch('/api/study-plans/recommendations/student/1'); // Replace with actual student ID
        if (!response.ok) throw new Error('Failed to load recommendations');
        
        const recommendations = await response.json();
        displayRecommendations(recommendations);
    } catch (error) {
        console.error('Error loading recommendations:', error);
        showError('Failed to load recommendations');
    }
}

async function loadCourses() {
    try {
        const response = await fetch('/api/courses');
        if (!response.ok) return;
        
        const courses = await response.json();
        populateCourseSelects(courses);
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

// ============================================================================
// Display Functions
// ============================================================================

function displayStudyPlans(plans) {
    const container = document.getElementById('plansContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (!plans || plans.length === 0) {
        container.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }
    
    container.style.display = 'grid';
    if (emptyState) emptyState.style.display = 'none';
    
    container.innerHTML = plans.map(plan => `
        <div class="plan-card" onclick="window.location.href='/study-plans/${plan.Plan_ID}'">
            <div class="plan-card-header">
                <h3>${escapeHtml(plan.Plan_Name)}</h3>
                <span class="status-badge ${plan.Status}">${plan.Status}</span>
            </div>
            <div class="plan-card-body">
                <div class="date-range">
                    📅 ${formatDate(plan.Start_Date)} - ${formatDate(plan.End_Date)}
                </div>
                <div class="plan-progress">
                    <div class="progress-label">
                        <span>Progress</span>
                        <span>${Math.round(plan.Completion_Percentage || 0)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${plan.Completion_Percentage || 0}%"></div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function displayPlanDetails(plan) {
    document.getElementById('planTitle').textContent = plan.Plan_Name;
    document.getElementById('planStatus').textContent = plan.Status;
    document.getElementById('planStatus').className = `status-badge ${plan.Status}`;
    document.getElementById('planDates').textContent = 
        `${formatDate(plan.Start_Date)} - ${formatDate(plan.End_Date)}`;
    
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const percentage = Math.round(plan.Completion_Percentage || 0);
    
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
}

function displayAnalytics(analytics) {
    document.getElementById('totalTasks').textContent = analytics.total_tasks || 0;
    document.getElementById('completedTasks').textContent = analytics.completed_tasks || 0;
    document.getElementById('pendingTasks').textContent = analytics.pending_tasks || 0;
    document.getElementById('estimatedHours').textContent = 
        `${Math.round(analytics.total_estimated_hours || 0)}h`;
}

function displayTasks(tasks) {
    const container = document.getElementById('tasksContainer');
    
    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No tasks yet. Add your first task!</p></div>';
        return;
    }
    
    container.innerHTML = tasks.map(task => `
        <div class="task-item" onclick="showEditTaskModal(${task.Task_ID})">
            <div class="task-header">
                <div class="task-title">${escapeHtml(task.Task_Title)}</div>
                <span class="task-priority ${task.Priority}">${task.Priority}</span>
            </div>
            ${task.Description ? `<div class="task-description">${escapeHtml(task.Description)}</div>` : ''}
            <div class="task-meta">
                ${task.Due_Date ? `<span class="task-meta-item">📅 ${formatDateTime(task.Due_Date)}</span>` : ''}
                ${task.Estimated_Hours ? `<span class="task-meta-item">⏱️ ${task.Estimated_Hours}h</span>` : ''}
                <span class="task-meta-item status-badge ${task.Status}">${task.Status.replace('_', ' ')}</span>
            </div>
        </div>
    `).join('');
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No recommendations available.</p></div>';
        return;
    }
    
    container.innerHTML = recommendations.map(rec => `
        <div class="recommendation-item">
            <span class="recommendation-type">${getResourceTypeIcon(rec.Resource_Type)} ${rec.Resource_Type}</span>
            <div class="recommendation-topic">${escapeHtml(rec.Topic || 'Study Resource')}</div>
            <div class="recommendation-reason">${escapeHtml(rec.Reason || 'Recommended for you')}</div>
            ${rec.Resource_Link ? `<a href="${rec.Resource_Link}" class="recommendation-link">View Resource →</a>` : ''}
        </div>
    `).join('');
}

function filterTasks() {
    if (currentFilter === 'all') {
        displayTasks(allTasks);
    } else {
        const filtered = allTasks.filter(task => task.Status === currentFilter);
        displayTasks(filtered);
    }
}

// ============================================================================
// Modal Functions
// ============================================================================

function showCreatePlanModal() {
    const modal = document.getElementById('createPlanModal');
    modal.classList.add('active');
}

function closeCreatePlanModal() {
    const modal = document.getElementById('createPlanModal');
    modal.classList.remove('active');
    document.getElementById('createPlanForm').reset();
}

function showAddTaskModal() {
    const modal = document.getElementById('addTaskModal');
    modal.classList.add('active');
}

function closeAddTaskModal() {
    const modal = document.getElementById('addTaskModal');
    modal.classList.remove('active');
    document.getElementById('addTaskForm').reset();
}

function showEditTaskModal(taskId) {
    const task = allTasks.find(t => t.Task_ID === taskId);
    if (!task) return;
    
    document.getElementById('editTaskId').value = task.Task_ID;
    document.getElementById('editTaskTitle').value = task.Task_Title;
    document.getElementById('editTaskDescription').value = task.Description || '';
    document.getElementById('editEstimatedHours').value = task.Estimated_Hours || '';
    document.getElementById('editActualHours').value = task.Actual_Hours || '';
    document.getElementById('editTaskPriority').value = task.Priority;
    document.getElementById('editTaskStatus').value = task.Status;
    
    if (task.Due_Date) {
        const date = new Date(task.Due_Date);
        document.getElementById('editTaskDueDate').value = formatDateTimeLocal(date);
    }
    
    const modal = document.getElementById('editTaskModal');
    modal.classList.add('active');
}

function closeEditTaskModal() {
    const modal = document.getElementById('editTaskModal');
    modal.classList.remove('active');
    document.getElementById('editTaskForm').reset();
}

// ============================================================================
// Form Handlers
// ============================================================================

async function handleCreatePlan(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        plan_name: formData.get('planName'),
        course_id: formData.get('courseId') || null,
        start_date: formData.get('startDate'),
        end_date: formData.get('endDate'),
        include_existing_tasks: formData.get('includeExisting') === 'on'
    };
    
    try {
        const response = await fetch('/api/study-plans/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to create study plan');
        
        const plan = await response.json();
        closeCreatePlanModal();
        showSuccess('Study plan created successfully!');
        
        // Redirect to the new plan
        setTimeout(() => {
            window.location.href = `/study-plans/${plan.Plan_ID}`;
        }, 1000);
    } catch (error) {
        console.error('Error creating plan:', error);
        showError('Failed to create study plan');
    }
}

async function handleAddTask(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        task_title: formData.get('taskTitle'),
        description: formData.get('taskDescription'),
        estimated_hours: parseFloat(formData.get('estimatedHours')) || null,
        due_date: formData.get('taskDueDate') || null,
        priority: formData.get('taskPriority'),
        auto_decompose: formData.get('autoDecompose') === 'on'
    };
    
    try {
        const response = await fetch(`/api/study-plans/${currentPlanId}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to add task');
        
        closeAddTaskModal();
        showSuccess('Task added successfully!');
        loadPlanTasks();
        loadPlanDetails(); // Refresh to update progress
    } catch (error) {
        console.error('Error adding task:', error);
        showError('Failed to add task');
    }
}

async function handleEditTask(e) {
    e.preventDefault();
    
    const taskId = document.getElementById('editTaskId').value;
    const formData = new FormData(e.target);
    const data = {
        task_title: formData.get('taskTitle'),
        description: formData.get('taskDescription'),
        estimated_hours: parseFloat(formData.get('estimatedHours')) || null,
        actual_hours: parseFloat(formData.get('actualHours')) || null,
        due_date: formData.get('taskDueDate') || null,
        priority: formData.get('taskPriority'),
        status: formData.get('taskStatus')
    };
    
    try {
        const response = await fetch(`/api/study-plans/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to update task');
        
        closeEditTaskModal();
        showSuccess('Task updated successfully!');
        loadPlanTasks();
        loadPlanDetails(); // Refresh to update progress
    } catch (error) {
        console.error('Error updating task:', error);
        showError('Failed to update task');
    }
}

async function deleteTask() {
    const taskId = document.getElementById('editTaskId').value;
    
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`/api/study-plans/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete task');
        
        closeEditTaskModal();
        showSuccess('Task deleted successfully!');
        loadPlanTasks();
        loadPlanDetails();
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('Failed to delete task');
    }
}

async function handleAdjustPlan() {
    try {
        const response = await fetch(`/api/study-plans/${currentPlanId}/adjust`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: 'manual' })
        });
        
        if (!response.ok) throw new Error('Failed to adjust plan');
        
        showSuccess('Study plan adjusted successfully!');
        loadPlanDetails();
        loadPlanTasks();
    } catch (error) {
        console.error('Error adjusting plan:', error);
        showError('Failed to adjust plan');
    }
}

function handleFilterChange() {
    const statusFilter = document.getElementById('statusFilter').value;
    const courseFilter = document.getElementById('courseFilter').value;
    
    let filtered = allPlans;
    
    if (statusFilter !== 'all') {
        filtered = filtered.filter(plan => plan.Status === statusFilter);
    }
    
    if (courseFilter !== 'all') {
        filtered = filtered.filter(plan => plan.Course_ID == courseFilter);
    }
    
    displayStudyPlans(filtered);
}

// ============================================================================
// Utility Functions
// ============================================================================

function setDefaultDates() {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput && endDateInput) {
        const today = new Date();
        const endDate = new Date(today);
        endDate.setDate(endDate.getDate() + 30);
        
        startDateInput.value = today.toISOString().split('T')[0];
        endDateInput.value = endDate.toISOString().split('T')[0];
    }
}

function populateCourseSelects(courses) {
    const selects = ['courseFilter', 'courseSelect'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.Course_ID;
            option.textContent = course.Course_Name;
            select.appendChild(option);
        });
    });
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getResourceTypeIcon(type) {
    const icons = {
        'note': '📝',
        'video': '🎥',
        'practice': '✏️',
        'textbook': '📚'
    };
    return icons[type] || '📄';
}

function showSuccess(message) {
    // Simple alert for now - can be replaced with a toast notification
    alert(message);
}

function showError(message) {
    // Simple alert for now - can be replaced with a toast notification
    alert('Error: ' + message);
}

// Close modals when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
}
