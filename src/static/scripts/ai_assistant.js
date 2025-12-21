/**
 * AI Assistant JavaScript
 * Handles chat interface and API interactions
 */

class AIAssistant {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.questionInput = document.getElementById('questionInput');
        this.chatForm = document.getElementById('chatForm');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.clearHistoryBtn = document.getElementById('clearHistoryBtn');
        this.clearHistoryBtn2 = document.getElementById('clearHistoryBtn2');
        this.newChatBtn = document.getElementById('newChatBtn');
        
        // Model selector elements
        this.unifyModelBtn = document.getElementById('unifyModelBtn');
        this.ollamaModelBtn = document.getElementById('ollamaModelBtn');
        this.selectedModel = localStorage.getItem('ai_model_preference') || 'unify';
        
        // Tab elements
        this.tabBtns = document.querySelectorAll('.ai-tab-btn');
        this.tabPanes = document.querySelectorAll('.ai-tab-pane');
        this.currentTab = 'chat';
        
        // Data loaded flags
        this.historyLoaded = false;
        this.knowledgeLoaded = false;
        this.categoriesLoaded = false;
        
        // Store welcome message HTML for restoration
        this.welcomeMessageHTML = null;
        this.initWelcomeMessage();
        
        this.init();
    }
    
    initWelcomeMessage() {
        // Store the initial welcome message HTML
        const welcomeMsg = document.querySelector('.welcome-message-new');
        if (welcomeMsg) {
            this.welcomeMessageHTML = welcomeMsg.outerHTML;
        }
    }
    
    init() {
        // Tab switching
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });
        
        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Clear history buttons
        this.clearHistoryBtn.addEventListener('click', () => {
            this.clearHistory();
        });
        
        if (this.clearHistoryBtn2) {
            this.clearHistoryBtn2.addEventListener('click', () => {
                this.clearHistory();
            });
        }
        
        // New chat button
        if (this.newChatBtn) {
            this.newChatBtn.addEventListener('click', () => {
                this.newChat();
            });
        }
        
        // Model selector buttons
        if (this.unifyModelBtn) {
            this.unifyModelBtn.addEventListener('click', () => {
                this.selectModel('unify');
            });
        }
        
        if (this.ollamaModelBtn) {
            this.ollamaModelBtn.addEventListener('click', () => {
                this.selectModel('ollama');
            });
        }
        
        // Initialize model selector UI
        this.updateModelSelectorUI();
        
        // Sample questions
        document.querySelectorAll('.sample-question, .sample-question-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.getAttribute('data-question');
                this.questionInput.value = question;
                this.sendMessage();
            });
        });
        
        // Category tags
        document.querySelectorAll('.category-tag, .category-tag-btn').forEach(tag => {
            tag.addEventListener('click', () => {
                const category = tag.getAttribute('data-category');
                this.questionInput.value = `Tell me about ${category}`;
                this.sendMessage();
            });
        });
        
        // Auto-resize textarea
        this.questionInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Enter to send (Shift+Enter for new line)
        this.questionInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
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
            'history': 'historyTab',
            'knowledge': 'knowledgeTab',
            'categories': 'categoriesTab'
        };
        
        const paneId = tabMap[tab];
        const pane = document.getElementById(paneId);
        if (pane) {
            pane.classList.add('active');
        }
        
        this.currentTab = tab;
        
        // Load data for tab if not loaded
        if (tab === 'history' && !this.historyLoaded) {
            this.loadFullHistory();
        } else if (tab === 'knowledge' && !this.knowledgeLoaded) {
            this.loadKnowledgeBase();
        } else if (tab === 'categories' && !this.categoriesLoaded) {
            this.loadCategories();
        }
    }
    
    async loadFullHistory() {
        const container = document.getElementById('fullHistoryList');
        
        try {
            const response = await fetch('/ai-assistant/history?limit=100');
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                container.innerHTML = data.history.map(chat => `
                    <div class="history-item">
                        <div class="history-question">
                            <i class="fas fa-user"></i>
                            ${this.escapeHtml(chat.Question)}
                        </div>
                        <div class="history-answer">
                            ${this.escapeHtml(chat.Answer)}
                        </div>
                        <div class="history-meta">
                            <span>
                                <i class="fas fa-clock"></i>
                                ${this.formatDate(chat.Created_Date)}
                            </span>
                            ${chat.Sources ? `
                                <span>
                                    <i class="fas fa-book"></i>
                                    ${chat.Sources.split(',').length} sources
                                </span>
                            ` : ''}
                        </div>
                    </div>
                `).join('');
                
                this.historyLoaded = true;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No conversation history yet</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading history:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Failed to load history</p>
                </div>
            `;
        }
    }
    
    async loadKnowledgeBase(category = null) {
        const container = document.getElementById('knowledgeGrid');
        
        try {
            const url = category ? `/ai-assistant/knowledge-base?category=${encodeURIComponent(category)}` : '/ai-assistant/knowledge-base';
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.documents && data.documents.length > 0) {
                container.innerHTML = data.documents.map(doc => `
                    <div class="knowledge-item">
                        <div class="knowledge-item-header">
                            <h3 class="knowledge-item-title">${this.escapeHtml(doc.Title)}</h3>
                            <span class="knowledge-item-category">${this.escapeHtml(doc.Category)}</span>
                        </div>
                        <div class="knowledge-item-content">
                            ${this.escapeHtml(doc.Content)}
                        </div>
                        ${doc.Keywords ? `
                            <div class="knowledge-item-keywords">
                                ${doc.Keywords.split(',').map(kw => `
                                    <span class="knowledge-keyword">${this.escapeHtml(kw.trim())}</span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('');
                
                this.knowledgeLoaded = true;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-book"></i>
                        <p>No documents found</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading knowledge base:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Failed to load knowledge base</p>
                </div>
            `;
        }
    }
    
    async loadCategories() {
        const container = document.getElementById('categoriesGrid');
        
        try {
            const response = await fetch('/ai-assistant/categories');
            const data = await response.json();
            
            if (data.categories && data.categories.length > 0) {
                const categoryIcons = {
                    'Courses': 'fa-graduation-cap',
                    'Schedule': 'fa-calendar',
                    'Academic Policies': 'fa-book',
                    'Registration': 'fa-clipboard-check',
                    'Fees': 'fa-dollar-sign',
                    'Campus': 'fa-building',
                    'Resources': 'fa-tools',
                    'Exams': 'fa-file-alt'
                };
                
                container.innerHTML = data.categories.map(category => {
                    const icon = categoryIcons[category] || 'fa-tag';
                    return `
                        <div class="category-card" data-category="${this.escapeHtml(category)}">
                            <div class="category-icon">
                                <i class="fas ${icon}"></i>
                            </div>
                            <div class="category-name">${this.escapeHtml(category)}</div>
                            <div class="category-count">Click to explore</div>
                        </div>
                    `;
                }).join('');
                
                // Add click handlers to category cards
                document.querySelectorAll('.category-card').forEach(card => {
                    card.addEventListener('click', () => {
                        const category = card.getAttribute('data-category');
                        this.switchTab('knowledge');
                        this.loadKnowledgeBase(category);
                    });
                });
                
                this.categoriesLoaded = true;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-tags"></i>
                        <p>No categories available</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Failed to load categories</p>
                </div>
            `;
        }
    }
    
    autoResizeTextarea() {
        this.questionInput.style.height = 'auto';
        this.questionInput.style.height = this.questionInput.scrollHeight + 'px';
    }
    
    async sendMessage() {
        const question = this.questionInput.value.trim();
        
        if (!question) {
            return;
        }
        
        // Hide welcome message if visible
        const welcomeMessage = document.querySelector('.welcome-message, .welcome-message-new');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Add user message to chat
        this.addUserMessage(question);
        
        // Clear input
        this.questionInput.value = '';
        this.questionInput.style.height = 'auto';
        
        // Show loading
        this.showLoading();
        
        try {
            // Send request to backend with model choice
            const response = await fetch('/ai-assistant/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    question,
                    model: this.selectedModel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addAssistantMessage(data.answer, data.sources, data.confidence);
            } else {
                this.addErrorMessage(data.error || 'An error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            this.addErrorMessage('Failed to get response. Please try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">You</span>
                    <span class="message-time">${timeString}</span>
                </div>
                <div class="message-text">${this.escapeHtml(text)}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addAssistantMessage(answer, sources, confidence) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Format answer (preserve line breaks and bold text)
        const formattedAnswer = this.formatAnswer(answer);
        
        // Build sources HTML
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="message-sources">
                    <div class="message-sources-title">
                        <i class="fas fa-book"></i>
                        Sources
                    </div>
                    ${sources.map(source => `
                        <div class="source-item">
                            <div class="source-title">${this.escapeHtml(source.title)}</div>
                            ${source.category ? `<div class="source-category">${this.escapeHtml(source.category)}</div>` : ''}
                            <div class="source-excerpt">${this.escapeHtml(source.excerpt)}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        // Confidence badge
        const confidenceBadge = `
            <span class="confidence-badge confidence-${confidence}">
                ${confidence.charAt(0).toUpperCase() + confidence.slice(1)} Confidence
            </span>
        `;
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">AI Assistant</span>
                    <span class="message-time">${timeString}</span>
                </div>
                <div class="message-text">${formattedAnswer}</div>
                ${sourcesHtml}
                ${confidenceBadge}
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Update recent chats in sidebar
        this.updateRecentChats();
    }
    
    addErrorMessage(errorText) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-sender">System</span>
                    <span class="message-time">${timeString}</span>
                </div>
                <div class="message-text" style="background: #fed7d7; border-color: #fc8181; color: #742a2a;">
                    ${this.escapeHtml(errorText)}
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatAnswer(text) {
        // Escape HTML first
        let formatted = this.escapeHtml(text);
        
        // Convert **text** to bold
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }
    
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
    
    async updateRecentChats() {
        try {
            const response = await fetch('/ai-assistant/history?limit=10');
            const data = await response.json();
            
            if (data.success && data.history) {
                const recentChatsDiv = document.getElementById('recentChats');
                
                if (data.history.length === 0) {
                    recentChatsDiv.innerHTML = `
                        <div class="no-history">
                            <i class="fas fa-inbox"></i>
                            <p>No conversation history yet</p>
                        </div>
                    `;
                } else {
                    recentChatsDiv.innerHTML = data.history.map(chat => `
                        <div class="chat-preview-item" data-chat-id="${chat.Chat_ID}">
                            <div class="chat-preview-icon">
                                <i class="fas fa-comment-dots"></i>
                            </div>
                            <div class="chat-preview-content">
                                <div class="chat-preview-question">${this.escapeHtml(chat.Question.substring(0, 60))}${chat.Question.length > 60 ? '...' : ''}</div>
                                <div class="chat-preview-time">${this.formatDate(chat.Created_Date)}</div>
                            </div>
                        </div>
                    `).join('');
                }
            }
        } catch (error) {
            console.error('Error updating recent chats:', error);
        }
    }
    
    newChat() {
        // Clear all chat messages
        this.chatMessages.innerHTML = '';
        
        // Restore the full welcome message with all its content
        this.chatMessages.innerHTML = `
            <div class="welcome-message-new">
                <div class="welcome-icon-new">
                    <i class="fas fa-robot"></i>
                </div>
                <h2>Hello! I'm your AI Assistant</h2>
                <p>I can help you with:</p>
                
                <div class="capabilities-grid-new">
                    <div class="capability-item">
                        <i class="fas fa-graduation-cap"></i>
                        <div>
                            <h4>Course Information</h4>
                            <p>Prerequisites, syllabi, and details</p>
                        </div>
                    </div>
                    <div class="capability-item">
                        <i class="fas fa-calendar"></i>
                        <div>
                            <h4>Schedule & Deadlines</h4>
                            <p>Class times and exam dates</p>
                        </div>
                    </div>
                    <div class="capability-item">
                        <i class="fas fa-book"></i>
                        <div>
                            <h4>Academic Policies</h4>
                            <p>Rules and procedures</p>
                        </div>
                    </div>
                    <div class="capability-item">
                        <i class="fas fa-question-circle"></i>
                        <div>
                            <h4>General Questions</h4>
                            <p>Campus and resources</p>
                        </div>
                    </div>
                </div>

                <div class="sample-questions-new">
                    <p class="sample-title">Try asking:</p>
                    <button class="sample-question-btn" data-question="What are the prerequisites for Data Structures?">
                        <i class="fas fa-lightbulb"></i>
                        "What are the prerequisites for Data Structures?"
                    </button>
                    <button class="sample-question-btn" data-question="When is the deadline for course registration?">
                        <i class="fas fa-lightbulb"></i>
                        "When is the deadline for course registration?"
                    </button>
                    <button class="sample-question-btn" data-question="How do I calculate my GPA?">
                        <i class="fas fa-lightbulb"></i>
                        "How do I calculate my GPA?"
                    </button>
                </div>
            </div>
        `;
        
        // Clear input field
        this.questionInput.value = '';
        this.questionInput.style.height = 'auto';
        
        // Re-initialize sample questions after restoring welcome message
        setTimeout(() => {
            // Re-attach event listeners to sample questions
            document.querySelectorAll('.sample-question, .sample-question-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const question = btn.getAttribute('data-question');
                    this.questionInput.value = question;
                    this.sendMessage();
                });
            });
        }, 100);
        
        // Scroll to top
        this.chatMessages.scrollTop = 0;
    }
    
    async clearHistory() {
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
                // Clear chat messages
                this.chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <h2>History Cleared!</h2>
                        <p>Your conversation history has been cleared. Start a new conversation!</p>
                    </div>
                `;
                
                // Update sidebar
                this.updateRecentChats();
                
                // Reset history loaded flag and reload if on history tab
                this.historyLoaded = false;
                if (this.currentTab === 'history') {
                    const container = document.getElementById('fullHistoryList');
                    container.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>No conversation history yet</p>
                        </div>
                    `;
                }
                
                // Show success message
                this.showNotification('History cleared successfully', 'success');
            } else {
                this.showNotification(data.error || 'Failed to clear history', 'error');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            this.showNotification('Failed to clear history', 'error');
        }
    }
    
    selectModel(model) {
        this.selectedModel = model;
        localStorage.setItem('ai_model_preference', model);
        this.updateModelSelectorUI();
        
        // Show notification
        const modelName = model === 'unify' ? 'Unify Model' : 'Ollama';
        this.showNotification(`Switched to ${modelName}`, 'success');
    }
    
    updateModelSelectorUI() {
        if (this.unifyModelBtn && this.ollamaModelBtn) {
            if (this.selectedModel === 'unify') {
                this.unifyModelBtn.classList.add('active');
                this.ollamaModelBtn.classList.remove('active');
            } else {
                this.unifyModelBtn.classList.remove('active');
                this.ollamaModelBtn.classList.add('active');
            }
        }
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (seconds < 60) {
            return 'Just now';
        } else if (minutes < 60) {
            return `${minutes} min ago`;
        } else if (hours < 24) {
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else if (days < 7) {
            return `${days} day${days > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    showNotification(message, type = 'info') {
        // Simple notification (you can enhance this)
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#48bb78' : '#f56565'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AIAssistant();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
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
