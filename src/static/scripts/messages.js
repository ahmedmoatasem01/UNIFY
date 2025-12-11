/**
 * Messages Application - Handles in-app messaging functionality
 */

let currentConversationUserId = null;
let conversations = [];
let pollInterval = null;

// Initialize the messaging app
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    loadUsers();
    setupEventListeners();
    startPolling();
});

// Setup event listeners
function setupEventListeners() {
    // Search conversations
    document.getElementById('searchConversations').addEventListener('input', handleSearchConversations);
    
    // New message button
    document.getElementById('newMessageBtn').addEventListener('click', openNewMessageModal);
    
    // Modal controls
    document.getElementById('closeModalBtn').addEventListener('click', closeNewMessageModal);
    document.getElementById('cancelModalBtn').addEventListener('click', closeNewMessageModal);
    document.getElementById('sendNewMessageBtn').addEventListener('click', sendNewMessage);
    
    // Message form
    document.getElementById('messageForm').addEventListener('submit', handleSendMessage);
    
    // Auto-resize textarea
    const textarea = document.getElementById('messageInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Close modal on outside click
    document.getElementById('newMessageModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeNewMessageModal();
        }
    });
}

// Load conversations list
async function loadConversations() {
    try {
        const response = await fetch('/messages/api/conversations');
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Failed to load conversations');
        }
        
        conversations = await response.json();
        renderConversations(conversations);
    } catch (error) {
        console.error('Error loading conversations:', error);
        showError('Failed to load conversations');
    }
}

// Render conversations list
function renderConversations(conversationsToRender) {
    const container = document.getElementById('conversationsList');
    
    if (conversationsToRender.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-inbox"></i>
                <p>No conversations yet</p>
                <button class="btn-primary" onclick="openNewMessageModal()">Start a conversation</button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = conversationsToRender.map(conv => `
        <div class="conversation-item ${conv.User_ID === currentConversationUserId ? 'active' : ''}" 
             data-user-id="${conv.User_ID}"
             onclick="loadConversation(${conv.User_ID}, '${escapeHtml(conv.Username)}')">
            <div class="conversation-avatar">
                <i class="fa-solid fa-user"></i>
            </div>
            <div class="conversation-content">
                <div class="conversation-header">
                    <h4 class="conversation-name">${escapeHtml(conv.Username)}</h4>
                    <span class="conversation-time">${formatTime(conv.Last_Message_Time)}</span>
                </div>
                <div class="conversation-preview">
                    <p class="last-message">${escapeHtml(conv.Last_Message || 'No messages')}</p>
                    ${conv.Unread_Count > 0 ? `<span class="unread-badge">${conv.Unread_Count}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// Search conversations
function handleSearchConversations(e) {
    const searchTerm = e.target.value.toLowerCase();
    const filtered = conversations.filter(conv => 
        conv.Username.toLowerCase().includes(searchTerm) ||
        (conv.Last_Message && conv.Last_Message.toLowerCase().includes(searchTerm))
    );
    renderConversations(filtered);
}

// Load conversation with a specific user
async function loadConversation(userId, username) {
    currentConversationUserId = userId;
    
    // Update UI
    document.getElementById('chatEmpty').style.display = 'none';
    document.getElementById('chatWindow').style.display = 'flex';
    document.getElementById('chatUserName').textContent = username;
    
    // Mark conversation as active
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.toggle('active', item.dataset.userId == userId);
    });
    
    try {
        const response = await fetch(`/messages/api/conversation/${userId}`);
        if (!response.ok) throw new Error('Failed to load conversation');
        
        const messages = await response.json();
        renderMessages(messages);
        
        // Reload conversations to update unread counts
        loadConversations();
    } catch (error) {
        console.error('Error loading conversation:', error);
        showError('Failed to load messages');
    }
}

// Render messages in chat window
function renderMessages(messages) {
    const container = document.getElementById('chatMessages');
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="empty-messages">
                <i class="fa-solid fa-comment-dots"></i>
                <p>No messages yet. Start the conversation!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = messages.map(msg => {
        const isSent = msg.Sender_ID !== currentConversationUserId;
        const messageClass = isSent ? 'message-sent' : 'message-received';
        
        return `
            <div class="message ${messageClass}">
                <div class="message-bubble">
                    <p class="message-text">${escapeHtml(msg.Message_Text)}</p>
                    <span class="message-time">${formatMessageTime(msg.Timestamp)}</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Handle sending message from chat window
async function handleSendMessage(e) {
    e.preventDefault();
    
    const messageInput = document.getElementById('messageInput');
    const messageText = messageInput.value.trim();
    
    if (!messageText || !currentConversationUserId) return;
    
    try {
        const response = await fetch('/messages/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                receiver_id: currentConversationUserId,
                message_text: messageText
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Reload conversation
        const username = document.getElementById('chatUserName').textContent;
        await loadConversation(currentConversationUserId, username);
        await loadConversations();
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message');
    }
}

// Load users for new message modal
async function loadUsers() {
    try {
        const response = await fetch('/messages/api/users');
        if (!response.ok) throw new Error('Failed to load users');
        
        const users = await response.json();
        const select = document.getElementById('recipientSelect');
        
        select.innerHTML = '<option value="">Select recipient...</option>' + 
            users.map(user => `
                <option value="${user.User_ID}">${escapeHtml(user.Username)} (${escapeHtml(user.Email)})</option>
            `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Open new message modal
function openNewMessageModal() {
    document.getElementById('newMessageModal').classList.add('show');
    document.getElementById('recipientSelect').value = '';
    document.getElementById('newMessageText').value = '';
}

// Close new message modal
function closeNewMessageModal() {
    document.getElementById('newMessageModal').classList.remove('show');
}

// Send new message from modal
async function sendNewMessage() {
    const recipientId = document.getElementById('recipientSelect').value;
    const messageText = document.getElementById('newMessageText').value.trim();
    
    if (!recipientId || !messageText) {
        showError('Please select a recipient and enter a message');
        return;
    }
    
    try {
        const response = await fetch('/messages/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                receiver_id: parseInt(recipientId),
                message_text: messageText
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        closeNewMessageModal();
        
        // Load the new conversation
        const select = document.getElementById('recipientSelect');
        const username = select.options[select.selectedIndex].text.split(' (')[0];
        await loadConversation(parseInt(recipientId), username);
        await loadConversations();
        
        showSuccess('Message sent successfully');
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message');
    }
}

// Start polling for new messages
function startPolling() {
    // Poll every 5 seconds for new messages
    pollInterval = setInterval(async () => {
        if (currentConversationUserId) {
            const username = document.getElementById('chatUserName').textContent;
            const response = await fetch(`/messages/api/conversation/${currentConversationUserId}`);
            if (response.ok) {
                const messages = await response.json();
                renderMessages(messages);
            }
        }
        
        // Update conversations list
        await loadConversations();
    }, 5000);
}

// Stop polling when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (pollInterval) clearInterval(pollInterval);
    } else {
        startPolling();
    }
});

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
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
}

function formatMessageTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showError(message) {
    // Simple alert for now - you can implement a better toast notification
    alert(message);
}

function showSuccess(message) {
    // Simple alert for now - you can implement a better toast notification
    console.log(message);
}
