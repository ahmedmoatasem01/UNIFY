/**
 * Academic Advisor Chatbot JavaScript
 * Handles chat interface and API interactions
 */

class AdvisorChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.studentId = STUDENT_ID;
        this.currentConversationId = null;
        
        // Tab elements
        this.tabBtns = document.querySelectorAll('.advisor-tab-btn');
        this.tabPanes = document.querySelectorAll('.advisor-tab-pane');
        this.currentTab = 'chat';
        
        this.init();
    }
    
    init() {
        // Tab switching
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });
        
        // Send button
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Quick action buttons
        document.querySelectorAll('.advisor-quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.getAttribute('data-question');
                this.messageInput.value = question;
                this.autoResizeTextarea();
                this.sendMessage();
            });
        });
        
        // New appointment button
        const newAppointmentBtn = document.getElementById('newAppointmentBtn');
        if (newAppointmentBtn) {
            newAppointmentBtn.addEventListener('click', () => {
                this.showAppointmentModal();
            });
        }
        
        // Load initial data based on current tab
        this.loadTabData();
    }
    
    async showAppointmentModal() {
        // Create modal for scheduling appointment
        const modal = document.createElement('div');
        modal.className = 'advisor-modal-overlay';
        modal.innerHTML = `
            <div class="advisor-modal">
                <div class="advisor-modal-header">
                    <h2>Schedule Appointment</h2>
                    <button class="advisor-modal-close" onclick="this.closest('.advisor-modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="advisor-modal-body">
                    <div class="advisor-form-group">
                        <label>Select Advisor</label>
                        <select id="advisorSelect" class="advisor-form-input">
                            <option value="">Loading advisors...</option>
                        </select>
                    </div>
                    <div class="advisor-form-group">
                        <label>Date & Time</label>
                        <input type="datetime-local" id="appointmentDateTime" class="advisor-form-input" required>
                    </div>
                    <div class="advisor-form-group">
                        <label>Reason for Appointment</label>
                        <textarea id="appointmentReason" class="advisor-form-input" rows="3" 
                                  placeholder="e.g., Degree planning, Course selection, Academic concerns..."></textarea>
                    </div>
                </div>
                <div class="advisor-modal-footer">
                    <button class="cr-btn-ghost" onclick="this.closest('.advisor-modal-overlay').remove()">Cancel</button>
                    <button class="cr-btn-primary" id="confirmAppointmentBtn">Schedule</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Load advisors
        try {
            const response = await fetch('/api/advisor/advisors');
            if (response.ok) {
                const advisors = await response.json();
                const select = document.getElementById('advisorSelect');
                select.innerHTML = '<option value="">Select an advisor...</option>';
                advisors.forEach(advisor => {
                    const option = document.createElement('option');
                    option.value = advisor.Instructor_ID;
                    option.textContent = `${advisor.name || 'Advisor'} - ${advisor.Department || 'General'}`;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading advisors:', error);
            document.getElementById('advisorSelect').innerHTML = '<option value="">Error loading advisors</option>';
        }
        
        // Set minimum date to today
        const dateInput = document.getElementById('appointmentDateTime');
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.min = now.toISOString().slice(0, 16);
        
        // Handle confirm button
        document.getElementById('confirmAppointmentBtn').addEventListener('click', async () => {
            await this.createAppointment(modal);
        });
    }
    
    async createAppointment(modal) {
        const advisorId = document.getElementById('advisorSelect').value;
        const dateTime = document.getElementById('appointmentDateTime').value;
        const reason = document.getElementById('appointmentReason').value;
        
        if (!advisorId || !dateTime) {
            alert('Please select an advisor and date/time');
            return;
        }
        
        try {
            // Convert local datetime to ISO string
            const scheduledDate = new Date(dateTime).toISOString();
            
            const response = await fetch('/api/advisor/appointments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    student_id: this.studentId,
                    advisor_id: parseInt(advisorId),
                    scheduled_date: scheduledDate,
                    reason: reason || null,
                    created_from_conversation_id: this.currentConversationId || null
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create appointment');
            }
            
            // Close modal
            modal.remove();
            
            // Reload appointments list
            if (this.currentTab === 'appointments') {
                this.loadAppointments();
            }
            
            // Show success message
            alert('Appointment scheduled successfully!');
            
        } catch (error) {
            console.error('Error creating appointment:', error);
            alert(`Error: ${error.message}`);
        }
    }
    
    switchTab(tab) {
        // Update tab buttons
        this.tabBtns.forEach(btn => {
            if (btn.getAttribute('data-tab') === tab) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update tab panes
        this.tabPanes.forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Show selected tab
        const tabMap = {
            'chat': 'chatTab',
            'conversations': 'conversationsTab',
            'appointments': 'appointmentsTab',
            'progress': 'progressTab'
        };
        
        const paneId = tabMap[tab];
        if (paneId) {
            const pane = document.getElementById(paneId);
            if (pane) {
                pane.classList.add('active');
                this.currentTab = tab;
                this.loadTabData();
            }
        }
    }
    
    loadTabData() {
        switch(this.currentTab) {
            case 'conversations':
                this.loadConversations();
                break;
            case 'appointments':
                this.loadAppointments();
                break;
            case 'progress':
                this.loadProgress();
                break;
        }
    }
    
    async sendMessage() {
        const messageText = this.messageInput.value.trim();
        if (!messageText) return;
        
        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Remove welcome message if present
        const welcomeMsg = this.chatMessages.querySelector('.advisor-welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        // Add user message
        this.addMessage('student', messageText);
        
        // Show analyzing/loading message
        const loadingMsgId = this.addLoadingMessage();
        
        // Disable input
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
        
        try {
            // Send message to API - use "new" if no conversation ID
            const convId = this.currentConversationId || 'new';
            const response = await fetch(`/api/advisor/chat/conversations/${convId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message_text: messageText
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            const data = await response.json();
            
            // Update conversation ID
            if (data.conversation_id) {
                this.currentConversationId = data.conversation_id;
            }
            
            // Remove loading message
            this.removeLoadingMessage(loadingMsgId);
            
            // Add AI response
            this.addMessage('ai', data.response_text);
            
        } catch (error) {
            console.error('Error sending message:', error);
            // Remove loading message
            this.removeLoadingMessage(loadingMsgId);
            this.addMessage('ai', 'Sorry, I encountered an error. Please try again.');
        } finally {
            // Re-enable input
            this.messageInput.disabled = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    addLoadingMessage() {
        const loadingId = 'loading-msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = loadingId;
        messageDiv.className = 'advisor-message ai';
        
        const avatar = document.createElement('div');
        avatar.className = 'advisor-message-avatar';
        avatar.innerHTML = '<i class="fas fa-user-graduate"></i>';
        
        const content = document.createElement('div');
        content.className = 'advisor-message-content advisor-loading-message';
        
        const textEl = document.createElement('div');
        textEl.className = 'advisor-loading-text';
        textEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing your question...';
        
        content.appendChild(textEl);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        return loadingId;
    }
    
    removeLoadingMessage(loadingId) {
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) {
            loadingMsg.remove();
        }
    }
    
    addMessage(senderType, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `advisor-message ${senderType}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'advisor-message-avatar';
        avatar.innerHTML = senderType === 'student' 
            ? '<i class="fas fa-user"></i>' 
            : '<i class="fas fa-user-graduate"></i>';
        
        const content = document.createElement('div');
        content.className = 'advisor-message-content';
        
        const textEl = document.createElement('p');
        textEl.className = 'advisor-message-text';
        textEl.textContent = text;
        
        const timeEl = document.createElement('div');
        timeEl.className = 'advisor-message-time';
        timeEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        content.appendChild(textEl);
        content.appendChild(timeEl);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    async loadConversations() {
        const listContainer = document.getElementById('conversationsList');
        listContainer.innerHTML = '<div class="advisor-loading"><i class="fas fa-spinner fa-spin"></i><p>Loading conversations...</p></div>';
        
        try {
            const response = await fetch(`/api/advisor/chat/conversations/student/${this.studentId}`);
            if (!response.ok) throw new Error('Failed to load conversations');
            
            const conversations = await response.json();
            
            if (conversations.length === 0) {
                listContainer.innerHTML = '<div class="advisor-empty-state"><i class="fas fa-inbox"></i><p>No conversations yet</p></div>';
                return;
            }
            
            listContainer.innerHTML = conversations.map(conv => `
                <div class="advisor-conversation-item" data-conversation-id="${conv.Conversation_ID}">
                    <div class="advisor-conversation-header">
                        <span class="advisor-conversation-type">${conv.Conversation_Type || 'general'}</span>
                        <span class="advisor-conversation-status ${conv.Status}">${conv.Status}</span>
                    </div>
                    <div class="advisor-conversation-date">
                        ${conv.Last_Message_At ? new Date(conv.Last_Message_At).toLocaleString() : 'No messages'}
                    </div>
                </div>
            `).join('');
            
            // Add click handlers
            listContainer.querySelectorAll('.advisor-conversation-item').forEach(item => {
                item.addEventListener('click', () => {
                    const convId = item.getAttribute('data-conversation-id');
                    this.loadConversation(convId);
                    this.switchTab('chat');
                });
            });
            
        } catch (error) {
            console.error('Error loading conversations:', error);
            listContainer.innerHTML = '<div class="advisor-empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading conversations</p></div>';
        }
    }
    
    async loadConversation(conversationId) {
        this.currentConversationId = conversationId;
        
        // Clear messages
        this.chatMessages.innerHTML = '';
        
        try {
            const response = await fetch(`/api/advisor/chat/conversations/${conversationId}/messages`);
            if (!response.ok) throw new Error('Failed to load messages');
            
            const messages = await response.json();
            
            messages.forEach(msg => {
                this.addMessage(msg.Sender_Type, msg.Message_Text);
            });
            
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    }
    
    async loadAppointments() {
        const listContainer = document.getElementById('appointmentsList');
        listContainer.innerHTML = '<div class="advisor-loading"><i class="fas fa-spinner fa-spin"></i><p>Loading appointments...</p></div>';
        
        try {
            const response = await fetch(`/api/advisor/appointments/student/${this.studentId}?upcoming=true`);
            if (!response.ok) throw new Error('Failed to load appointments');
            
            const appointments = await response.json();
            
            if (appointments.length === 0) {
                listContainer.innerHTML = '<div class="advisor-empty-state"><i class="fas fa-calendar-times"></i><p>No upcoming appointments</p></div>';
                return;
            }
            
            listContainer.innerHTML = appointments.map(apt => `
                <div class="advisor-appointment-item">
                    <div class="advisor-appointment-header">
                        <div class="advisor-appointment-date">
                            ${new Date(apt.Scheduled_Date).toLocaleString()}
                        </div>
                        <span class="advisor-appointment-status ${apt.Status}">${apt.Status}</span>
                    </div>
                    ${apt.Reason ? `<div class="advisor-appointment-reason">${apt.Reason}</div>` : ''}
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error loading appointments:', error);
            listContainer.innerHTML = '<div class="advisor-empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading appointments</p></div>';
        }
    }
    
    async loadProgress() {
        const container = document.getElementById('progressContainer');
        container.innerHTML = '<div class="advisor-loading"><i class="fas fa-spinner fa-spin"></i><p>Loading degree progress...</p></div>';
        
        try {
            const response = await fetch(`/api/advisor/degree-progress/student/${this.studentId}`);
            if (!response.ok) throw new Error('Failed to load progress');
            
            const progress = await response.json();
            
            container.innerHTML = `
                <div class="advisor-progress-card">
                    <div class="advisor-progress-header">
                        <h3>Degree Progress</h3>
                        ${progress.department ? `<p style="color: var(--cr-text-muted); margin: 0;">${progress.department}</p>` : ''}
                    </div>
                    <div class="advisor-progress-bar-container">
                        <div class="advisor-progress-bar-label">
                            <span>Progress</span>
                            <span class="percentage">${progress.progress_percent}%</span>
                        </div>
                        <div class="advisor-progress-bar">
                            <div class="advisor-progress-bar-fill" style="width: ${progress.progress_percent}%">
                                ${progress.progress_percent >= 5 ? progress.progress_percent + '%' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="advisor-progress-stats">
                        <div class="advisor-progress-stat">
                            <div class="advisor-progress-stat-value">${progress.completed_credits}</div>
                            <div class="advisor-progress-stat-label">Completed Credits</div>
                        </div>
                        <div class="advisor-progress-stat">
                            <div class="advisor-progress-stat-value">${progress.remaining_credits}</div>
                            <div class="advisor-progress-stat-label">Remaining Credits</div>
                        </div>
                        <div class="advisor-progress-stat">
                            <div class="advisor-progress-stat-value">${progress.total_required_credits}</div>
                            <div class="advisor-progress-stat-label">Total Required</div>
                        </div>
                        ${progress.gpa ? `
                        <div class="advisor-progress-stat">
                            <div class="advisor-progress-stat-value">${progress.gpa.toFixed(2)}</div>
                            <div class="advisor-progress-stat-label">GPA</div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
        } catch (error) {
            console.error('Error loading progress:', error);
            container.innerHTML = '<div class="advisor-empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading degree progress</p></div>';
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AdvisorChatbot();
});
