// Modern AI Assistant Frontend
class AIAssistant {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.typingIndicator = document.getElementById('typing-indicator');
        
        this.conversationId = this.generateConversationId();
        this.isProcessing = false;
        
        this.initializeEventListeners();
        this.createParticles();
        this.addWelcomeMessage();
    }
    
    generateConversationId() {
        return 'conv_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key to send (Shift+Enter for new line)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Focus input on page load
        this.chatInput.focus();
    }
    
    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }
    
    createParticles() {
        const particlesContainer = document.querySelector('.particles');
        const particleCount = 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particlesContainer.appendChild(particle);
        }
    }
    
    addWelcomeMessage() {
        const welcomeMessage = `👋 您好！我是您的AI Assistant。我可以帮助您：

• **天气信息** - 询问任何城市的天气情况
• **数学计算** - 解决数学问题
• **网络搜索** - 在线查找信息
• **通用问答** - 聊任何话题！

今天您想了解什么呢？`;

        this.addMessage('assistant', welcomeMessage);
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isProcessing) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input and reset height
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Disable input while processing
        this.setProcessingState(true);
        
        try {
            await this.sendToAPI(message);
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('assistant', '❌ 抱歉，我遇到了一个错误。请重试。');
        } finally {
            this.hideTypingIndicator();
            this.setProcessingState(false);
        }
    }
    
    async sendToAPI(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: this.conversationId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';
        let messageElement = null;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.error) {
                            // Handle error from server
                            if (!messageElement) {
                                messageElement = this.addMessage('assistant', '', true);
                            }
                            this.updateMessageContent(messageElement, data.chunk || '❌ 服务器处理出错');
                            return;
                        }

                        if (data.chunk && !data.done) {
                            assistantMessage += data.chunk;

                            // Create message element if it doesn't exist
                            if (!messageElement) {
                                messageElement = this.addMessage('assistant', '', true);
                            }

                            // Update the message content
                            this.updateMessageContent(messageElement, assistantMessage);
                        }

                        if (data.done) {
                            // Finalize the message
                            if (messageElement && data.full_response) {
                                this.updateMessageContent(messageElement, data.full_response);
                            }
                            return;
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    }
    
    addMessage(sender, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isStreaming) {
            contentDiv.innerHTML = this.formatMessage('');
        } else {
            contentDiv.innerHTML = this.formatMessage(content);
        }
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    updateMessageContent(messageElement, content) {
        const contentDiv = messageElement.querySelector('.message-content');
        contentDiv.innerHTML = this.formatMessage(content);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        
        // Format bullet points
        formatted = formatted.replace(/^• (.*?)(<br>|$)/gm, '<div class="bullet-point">• $1</div>');
        
        return formatted;
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    setProcessingState(isProcessing) {
        this.isProcessing = isProcessing;
        this.sendButton.disabled = isProcessing;
        this.chatInput.disabled = isProcessing;
        
        if (isProcessing) {
            this.sendButton.innerHTML = '<div class="spinner"></div>';
        } else {
            this.sendButton.innerHTML = '发送';
            this.chatInput.focus();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Initialize the assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AIAssistant();
});

// Add some CSS for the spinner
const style = document.createElement('style');
style.textContent = `
    .spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top: 2px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .bullet-point {
        margin: 0.5rem 0;
        padding-left: 1rem;
    }
    
    code {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.9em;
    }
`;
document.head.appendChild(style);
