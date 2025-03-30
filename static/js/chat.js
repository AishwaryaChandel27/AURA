/**
 * Chat functionality for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatContainer = document.getElementById('chatContainer');
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendChatMessage();
        });
    }
    
    /**
     * Send a chat message
     */
    function sendChatMessage() {
        const message = messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        messageInput.value = '';
        
        // Disable input while waiting for response
        messageInput.disabled = true;
        document.querySelector('#chatForm button').disabled = true;
        
        // Add loading indicator
        const loadingId = addLoadingMessage();
        
        // Send message to server
        fetch(`/api/projects/${projectId}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            removeLoadingMessage(loadingId);
            
            // Enable input
            messageInput.disabled = false;
            document.querySelector('#chatForm button').disabled = false;
            
            if (data.error) {
                addMessageToChat('system', `Error: ${data.error}`);
            } else {
                const agentType = data.agent_type || 'general';
                addMessageToChat('agent', data.message, agentType);
            }
            
            // Focus input
            messageInput.focus();
        })
        .catch(error => {
            console.error('Error sending message:', error);
            
            // Remove loading indicator
            removeLoadingMessage(loadingId);
            
            // Enable input
            messageInput.disabled = false;
            document.querySelector('#chatForm button').disabled = false;
            
            // Show error
            addMessageToChat('system', 'Error sending message. Please try again.');
            
            // Focus input
            messageInput.focus();
        });
    }
    
    /**
     * Add a message to the chat
     */
    function addMessageToChat(role, content, agentType = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        // Add TensorFlow badge for TensorFlow agent
        let messageContent = content;
        if (role === 'agent' && agentType === 'tensorflow') {
            messageContent = `<span class="tensorflow-badge small">TF</span> ${content}`;
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${messageContent}
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    /**
     * Add a loading message to the chat
     */
    function addLoadingMessage() {
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message agent-message';
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="spinner-border spinner-border-sm text-info" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span class="ms-2">Thinking...</span>
            </div>
        `;
        
        chatContainer.appendChild(loadingDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return loadingId;
    }
    
    /**
     * Remove a loading message from the chat
     */
    function removeLoadingMessage(loadingId) {
        const loadingDiv = document.getElementById(loadingId);
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
});