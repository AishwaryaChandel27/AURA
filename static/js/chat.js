/**
 * Chat functionality for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatContainer = document.getElementById('chatContainer');
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (!message) {
                return;
            }
            
            // Add user message to chat
            addChatMessage('user', message);
            
            // Clear input
            chatInput.value = '';
            
            // Send message to server
            sendChatMessage(message);
        });
    }
    
    // Scroll chat to bottom on load
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

/**
 * Add a message to the chat container
 * 
 * @param {string} role - Message role ('user' or 'agent')
 * @param {string} content - Message content
 * @param {string} agentType - Agent type (for agent messages)
 */
function addChatMessage(role, content, agentType = null) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    // Create message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    // Create message metadata
    const metaDiv = document.createElement('div');
    metaDiv.className = 'message-meta text-muted small';
    
    // Add agent type for agent messages
    if (role === 'agent' && agentType) {
        const agentTypeSpan = document.createElement('span');
        agentTypeSpan.className = 'agent-type';
        agentTypeSpan.textContent = agentType;
        metaDiv.appendChild(agentTypeSpan);
        metaDiv.appendChild(document.createTextNode(' • '));
    }
    
    // Add timestamp
    metaDiv.appendChild(document.createTextNode('Just now'));
    
    // Assemble message
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(metaDiv);
    
    // Add to chat container
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Send a chat message to the server
 * 
 * @param {string} message - Message to send
 */
function sendChatMessage(message) {
    fetch(`/api/projects/${projectId}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error sending message');
        }
        return response.json();
    })
    .then(data => {
        // Add agent response to chat
        addChatMessage('agent', data.content, data.agent_type);
    })
    .catch(error => {
        console.error('Error sending message:', error);
        addChatMessage('agent', 'Sorry, I encountered an error while processing your message. Please try again.', 'error');
    });
}