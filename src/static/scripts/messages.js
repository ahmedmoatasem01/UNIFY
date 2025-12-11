/**
 * Messages Page - JavaScript
 * Handles real-time messaging with database integration
 */

// ============================================================================
// STATE
// ============================================================================

let currentUserId = null;
let currentConversationUserId = null;
let allConversations = [];
let allUsers = [];
let refreshInterval = null;

// ============================================================================
// DOM ELEMENTS
// ============================================================================

const conversationsList = document.getElementById('conversationsList');
const chatEmpty = document.getElementById('chatEmpty');
const chatWindow = document.getElementById('chatWindow');
const chatMessages = document.getElementById('chatMessages');
const chatUserName = document.getElementById('chatUserName');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const searchInput = document.getElementById('searchConversations');

// Modal elements
const newMessageBtn = document.getElementById('newMessageBtn');
const newMessageModal = document.getElementById('newMessageModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelModalBtn = document.getElementById('cancelModalBtn');
const sendNewMessageBtn = document.getElementById('sendNewMessageBtn');
const recipientSelect = document.getElementById('recipientSelect');
const newMessageText = document.getElementById('newMessageText');

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    await loadConversations();
    await loadUsers();
    setupEventListeners();
    startAutoRefresh();
}

// ============================================================================
// API CALLS
// ============================================================================

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

        allConversations = await response.json();
        renderConversations(allConversations);
    } catch (error) {
        console.error('Error loading conversations:', error);
        conversationsList.innerHTML = `
            <div class="loading-spinner">
                <i class="fa-solid fa-exclamation-circle"></i>
                <p>Failed to load conversations</p>
            </div>
        `;
    }
}

async function loadConversation(otherUserId) {
    try {
        const response = await fetch(`/messages/api/conversation/${otherUserId}`);
        if (!response.ok) {
            throw new Error('Failed to load conversation');
        }

        const messages = await response.json();
        currentConversationUserId = otherUserId;
        renderMessages(messages);
        showChatWindow();

        // Update conversation name
        const conversation = allConversations.find(c => c.Other_User_ID === otherUserId);
        if (conversation) {
            chatUserName.textContent = conversation.Other_Username;
        }

        // Mark as active
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.userId) === otherUserId) {
                item.classList.add('active');
            }
        });

        // Scroll to bottom
        scrollToBottom();
    } catch (error) {
        console.error('Error loading conversation:', error);
        alert('Failed to load conversation');
    }
}

async function sendMessage() {
    const messageText = messageInput.value.trim();

    if (!messageText) {
        return;
    }

    if (!currentConversationUserId) {
        console.error('No conversation selected');
        return;
    }

    console.log('Sending message:', {
        receiver_id: parseInt(currentConversationUserId),
        message_text: messageText
    });

    try {
        const response = await fetch('/messages/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                receiver_id: parseInt(currentConversationUserId),
                message_text: messageText
            })
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert('Failed to send message: ' + (errorData.error || 'Unknown error'));
            return;
        }

        const result = await response.json();
        console.log('Message sent successfully:', result);

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Reload conversation
        await loadConversation(currentConversationUserId);

        // Reload conversations list
        await loadConversations();
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message: ' + error.message);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/messages/api/users');
        if (!response.ok) {
            throw new Error('Failed to load users');
        }

        allUsers = await response.json();
        populateRecipientSelect();
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function sendNewMessage() {
    const receiverId = recipientSelect.value;
    const messageText = newMessageText.value.trim();

    console.log('sendNewMessage called - receiverId:', receiverId, 'messageText:', messageText);

    if (!receiverId || receiverId === '') {
        alert('Please select a recipient');
        return;
    }

    if (!messageText) {
        alert('Please enter a message');
        return;
    }

    const payload = {
        receiver_id: parseInt(receiverId),
        message_text: messageText
    };

    console.log('Sending new message with payload:', payload);

    try {
        const response = await fetch('/messages/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert('Failed to send message: ' + (errorData.error || 'Unknown error'));
            return;
        }

        const result = await response.json();
        console.log('Message sent successfully:', result);

        // Close modal
        closeModal();

        // Reload conversations
        await loadConversations();

        // Open the new conversation
        await loadConversation(parseInt(receiverId));
    } catch (error) {
        console.error('Error sending new message:', error);
        alert('Failed to send message: ' + error.message);
    }
}

// ============================================================================
// RENDERING
// ============================================================================

function renderConversations(conversations) {
    if (!conversations || conversations.length === 0) {
        conversationsList.innerHTML = `
            <div class="loading-spinner">
                <i class="fa-solid fa-inbox"></i>
                <p>No conversations yet</p>
                <small>Start a new conversation!</small>
            </div>
        `;
        return;
    }

    conversationsList.innerHTML = conversations.map(conv => `
        <div class="conversation-item" data-user-id="${conv.Other_User_ID}" onclick="loadConversation(${conv.Other_User_ID})">
            <div class="conversation-avatar">
                ${conv.Other_Username ? conv.Other_Username.charAt(0).toUpperCase() : 'U'}
            </div>
            <div class="conversation-info">
                <div class="conversation-header">
                    <span class="conversation-name">${conv.Other_Username || 'Unknown User'}</span>
                    <span class="conversation-time">${formatTime(conv.Last_Message_Time)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p class="conversation-preview">${conv.Last_Message_Text || 'No messages'}</p>
                    ${conv.Unread_Count > 0 ? `<span class="conversation-badge">${conv.Unread_Count}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function renderMessages(messages) {
    if (!messages || messages.length === 0) {
        chatMessages.innerHTML = `
            <div style="text-align: center; color: var(--cr-text-muted); padding: 40px 20px;">
                <i class="fa-solid fa-comments" style="font-size: 3rem; margin-bottom: 16px; opacity: 0.5;"></i>
                <p>No messages yet. Start the conversation!</p>
            </div>
        `;
        return;
    }

    chatMessages.innerHTML = messages.map(msg => {
        const isSent = msg.Is_Sent; // This should be set based on current user
        return `
            <div class="message-bubble ${isSent ? 'sent' : 'received'}">
                <p class="message-text">${escapeHtml(msg.Message_Text)}</p>
                <span class="message-time">${formatTime(msg.Timestamp)}</span>
            </div>
        `;
    }).join('');
}

function populateRecipientSelect() {
    recipientSelect.innerHTML = '<option value="">Select recipient...</option>' +
        allUsers.map(user => `
            <option value="${user.User_ID}">${user.Username} (${user.Email})</option>
        `).join('');
}

// ============================================================================
// UI HELPERS
// ============================================================================

function showChatWindow() {
    chatEmpty.style.display = 'none';
    chatWindow.style.display = 'flex';
}

function hideChatWindow() {
    chatEmpty.style.display = 'flex';
    chatWindow.style.display = 'none';
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function openModal() {
    newMessageModal.classList.add('active');
}

function closeModal() {
    newMessageModal.classList.remove('active');
    recipientSelect.value = '';
    newMessageText.value = '';
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Message form
    messageForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });

    // Search conversations
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allConversations.filter(conv =>
            conv.Other_Username && conv.Other_Username.toLowerCase().includes(query)
        );
        renderConversations(filtered);
    });

    // New message modal
    newMessageBtn.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);
    sendNewMessageBtn.addEventListener('click', sendNewMessage);

    // Close modal on outside click
    newMessageModal.addEventListener('click', (e) => {
        if (e.target === newMessageModal) {
            closeModal();
        }
    });

    // Enter to send (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// ============================================================================
// AUTO REFRESH
// ============================================================================

function startAutoRefresh() {
    // Refresh conversations every 10 seconds
    refreshInterval = setInterval(async () => {
        await loadConversations();
        
        // Refresh current conversation if open
        if (currentConversationUserId) {
            await loadConversation(currentConversationUserId);
        }
    }, 10000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Stop refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

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

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// EXPORTS (for inline onclick handlers)
// ============================================================================

window.loadConversation = loadConversation;
