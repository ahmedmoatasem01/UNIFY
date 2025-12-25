// Focus Session Timer and Productivity Tracker

let timerInterval = null;
let timerSeconds = 0;
let timerStartTime = null;
let isRunning = false;
let isPaused = false;
let dailyChart = null;
let weeklyChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadProductivityData();
    updateTimerDisplay();
});

// Timer Functions
function startTimer() {
    if (!isRunning) {
        timerStartTime = new Date();
        isRunning = true;
        isPaused = false;
        
        // Start interval
        timerInterval = setInterval(() => {
            timerSeconds++;
            updateTimerDisplay();
        }, 1000);
        
        // Update UI
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('pauseBtn').style.display = 'flex';
        document.getElementById('stopBtn').style.display = 'flex';
        document.getElementById('timerLabel').textContent = 'Focusing...';
    }
}

function pauseTimer() {
    if (isRunning && !isPaused) {
        clearInterval(timerInterval);
        isPaused = true;
        document.getElementById('pauseBtn').innerHTML = '<i class="fa-solid fa-play"></i><span>Resume</span>';
        document.getElementById('timerLabel').textContent = 'Paused';
    } else if (isPaused) {
        // Resume
        timerInterval = setInterval(() => {
            timerSeconds++;
            updateTimerDisplay();
        }, 1000);
        isPaused = false;
        document.getElementById('pauseBtn').innerHTML = '<i class="fa-solid fa-pause"></i><span>Pause</span>';
        document.getElementById('timerLabel').textContent = 'Focusing...';
    }
}

async function stopTimer() {
    if (isRunning || isPaused) {
        clearInterval(timerInterval);
        
        // Save session if duration > 0
        if (timerSeconds > 0) {
            await saveSession();
        }
        
        // Reset timer
        timerSeconds = 0;
        timerStartTime = null;
        isRunning = false;
        isPaused = false;
        
        // Update UI
        document.getElementById('startBtn').style.display = 'flex';
        document.getElementById('pauseBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'none';
        document.getElementById('timerLabel').textContent = 'Ready to focus';
        updateTimerDisplay();
        
        // Reload productivity data
        await loadProductivityData();
    }
}

function updateTimerDisplay() {
    const hours = Math.floor(timerSeconds / 3600);
    const minutes = Math.floor((timerSeconds % 3600) / 60);
    const seconds = timerSeconds % 60;
    
    const timeString = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timerDisplay').textContent = timeString;
    
    // Update circular progress
    const totalSeconds = 25 * 60; // 25 minutes (Pomodoro default)
    const progress = (timerSeconds % totalSeconds) / totalSeconds;
    const circumference = 2 * Math.PI * 90;
    const offset = circumference * (1 - progress);
    
    const progressCircle = document.getElementById('timerProgressCircle');
    if (progressCircle) {
        progressCircle.style.strokeDashoffset = offset;
    }
}

// API Functions
async function saveSession() {
    try {
        const endTime = new Date();
        const startTime = timerStartTime || endTime;
        
        const response = await fetch('/focus-session/api/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                duration: timerSeconds,
                start_time: startTime.toISOString(),
                end_time: endTime.toISOString(),
                completed: !isPaused
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to save session');
        }
        
        const data = await response.json();
        console.log('Session saved:', data);
    } catch (error) {
        console.error('Error saving session:', error);
        alert('Failed to save session. Please try again.');
    }
}

async function loadProductivityData() {
    try {
        const response = await fetch('/focus-session/api/productivity');
        if (!response.ok) {
            throw new Error('Failed to load productivity data');
        }
        
        const data = await response.json();
        
        // Update statistics
        updateStatistics(data);
        
        // Update charts
        updateDailyChart(data.daily);
        updateWeeklyChart(data.weekly);
        
        // Update sessions table
        await updateSessionsTable();
    } catch (error) {
        console.error('Error loading productivity data:', error);
    }
}

function updateStatistics(data) {
    // Today's stats
    const todayHours = Math.floor(data.today.duration / 3600);
    const todayMinutes = Math.floor((data.today.duration % 3600) / 60);
    document.getElementById('todayDuration').textContent = `${todayHours}h ${todayMinutes}m`;
    document.getElementById('todaySessions').textContent = `${data.today.sessions} session${data.today.sessions !== 1 ? 's' : ''}`;
    
    // This week's stats
    const weekHours = Math.floor(data.this_week.duration / 3600);
    const weekMinutes = Math.floor((data.this_week.duration % 3600) / 60);
    document.getElementById('weekDuration').textContent = `${weekHours}h ${weekMinutes}m`;
    document.getElementById('weekSessions').textContent = `${data.this_week.sessions} session${data.this_week.sessions !== 1 ? 's' : ''}`;
    
    // Overall stats
    document.getElementById('totalSessions').textContent = data.overall.total_sessions;
    document.getElementById('totalDuration').textContent = `${data.overall.total_duration_hours} hours`;
    
    // Average session
    const avgMinutes = Math.floor(data.overall.avg_session_duration / 60);
    document.getElementById('avgSession').textContent = `${avgMinutes}m`;
}

function updateDailyChart(dailyData) {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;
    
    const labels = dailyData.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    });
    
    const durations = dailyData.map(d => d.duration_hours);
    
    if (dailyChart) {
        dailyChart.destroy();
    }
    
    dailyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Hours',
                data: durations,
                backgroundColor: 'rgba(99, 102, 241, 0.6)',
                borderColor: '#6366f1',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e6eef8',
                    bodyColor: '#9ca3af',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const hours = Math.floor(context.parsed.y);
                            const minutes = Math.round((context.parsed.y - hours) * 60);
                            return `${hours}h ${minutes}m`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#9ca3af',
                        callback: function(value) {
                            return value + 'h';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            }
        }
    });
}

function updateWeeklyChart(weeklyData) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    
    const labels = weeklyData.map(d => d.week);
    const durations = weeklyData.map(d => d.duration_hours);
    
    if (weeklyChart) {
        weeklyChart.destroy();
    }
    
    weeklyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Hours',
                data: durations,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e6eef8',
                    bodyColor: '#9ca3af',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const hours = Math.floor(context.parsed.y);
                            const minutes = Math.round((context.parsed.y - hours) * 60);
                            return `${hours}h ${minutes}m`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#9ca3af',
                        callback: function(value) {
                            return value + 'h';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            }
        }
    });
}

async function updateSessionsTable() {
    try {
        const response = await fetch('/focus-session/api/sessions?limit=20');
        if (!response.ok) {
            throw new Error('Failed to load sessions');
        }
        
        const data = await response.json();
        const tbody = document.getElementById('sessionsTableBody');
        
        if (data.sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="fs-empty-state">No recent sessions. Start a focus session to track your time!</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.sessions.map(session => {
            const date = new Date(session.date);
            const formattedDate = date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
            
            const statusClass = session.completed ? 'fs-status-completed' : 'fs-status-paused';
            const statusText = session.completed ? 'Completed' : 'Paused';
            
            return `
                <tr>
                    <td>${formattedDate}</td>
                    <td>${session.start_time || 'N/A'}</td>
                    <td>${session.duration}</td>
                    <td><span class="fs-status-badge ${statusClass}">${statusText}</span></td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading sessions:', error);
        const tbody = document.getElementById('sessionsTableBody');
        tbody.innerHTML = '<tr><td colspan="4" class="fs-empty-state">Error loading sessions</td></tr>';
    }
}

// Logout handler
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

