/**
 * Chat JavaScript for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Chat form submission
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const chatInput = document.getElementById('chatInput');
            const message = chatInput.value.trim();
            
            if (!message) {
                return;
            }
            
            // Add user message to chat
            addMessageToChat('user', message);
            
            // Clear input
            chatInput.value = '';
            
            // Show loading indicator
            const loadingId = addLoadingMessage();
            
            // Send message to server
            fetch(`/api/projects/${projectId}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Remove loading indicator
                removeLoadingMessage(loadingId);
                
                // Add agent response to chat
                addMessageToChat('agent', data.content, data.agent_type);
                
                // Scroll to bottom
                scrollChatToBottom();
            })
            .catch((error) => {
                console.error('Error sending message:', error);
                
                // Remove loading indicator
                removeLoadingMessage(loadingId);
                
                // Add error message
                addMessageToChat('agent', 'Sorry, there was an error processing your request. Please try again.', 'error');
                
                // Scroll to bottom
                scrollChatToBottom();
            });
            
            // Scroll to bottom
            scrollChatToBottom();
        });
    }
    
    // Scroll chat to bottom on load
    scrollChatToBottom();
});

/**
 * Add a message to the chat container
 * 
 * @param {string} role - 'user' or 'agent'
 * @param {string} content - Message content
 * @param {string} agentType - Agent type (for agent messages only)
 */
function addMessageToChat(role, content, agentType = '') {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;
    
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `chat-message ${role}`;
    
    // Create message content
    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';
    contentEl.textContent = content;
    messageEl.appendChild(contentEl);
    
    // Create message metadata
    const metaEl = document.createElement('div');
    metaEl.className = 'message-meta text-muted small';
    
    // Add agent type if available
    if (role === 'agent' && agentType) {
        const agentTypeEl = document.createElement('span');
        agentTypeEl.className = 'agent-type';
        agentTypeEl.textContent = agentType;
        metaEl.appendChild(agentTypeEl);
        metaEl.appendChild(document.createTextNode(' • '));
    }
    
    // Add timestamp
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    metaEl.appendChild(document.createTextNode(timeStr));
    
    messageEl.appendChild(metaEl);
    
    // Add to chat container
    chatContainer.appendChild(messageEl);
}

/**
 * Add a loading message to the chat
 * 
 * @returns {string} ID of the loading message
 */
function addLoadingMessage() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return '';
    
    // Generate a unique ID
    const id = 'loading-' + Date.now();
    
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message agent';
    messageEl.id = id;
    
    // Create loading indicator
    messageEl.innerHTML = `
        <div class="message-content">
            <div class="d-flex align-items-center">
                <span class="me-2">Thinking</span>
                <div class="spinner-grow spinner-grow-sm text-info" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    `;
    
    // Add to chat container
    chatContainer.appendChild(messageEl);
    
    // Scroll to bottom
    scrollChatToBottom();
    
    return id;
}

/**
 * Remove a loading message from the chat
 * 
 * @param {string} id - ID of the loading message
 */
function removeLoadingMessage(id) {
    const loadingEl = document.getElementById(id);
    if (loadingEl) {
        loadingEl.remove();
    }
}

/**
 * Scroll the chat container to the bottom
 */
function scrollChatToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}