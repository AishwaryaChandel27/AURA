// Chat functionality for AURA Research Assistant

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatContainer = document.getElementById('chatContainer');
    const projectId = chatContainer ? chatContainer.getAttribute('data-project-id') : null;
    
    if (chatForm && chatInput && chatContainer && projectId) {
        // Initialize chat
        loadChatHistory(projectId);
        
        // Set up form submission
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            
            if (message) {
                // Add user message to chat
                addMessageToChat('user', message);
                
                // Clear input
                chatInput.value = '';
                
                // Show typing indicator
                addTypingIndicator();
                
                // Send message to server
                sendChatMessage(projectId, message);
            }
        });
    }
});

// Load chat history for a project
function loadChatHistory(projectId) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Clear existing messages
    while (chatContainer.firstChild) {
        chatContainer.removeChild(chatContainer.firstChild);
    }
    
    // Add welcome message
    const welcomeMessage = `
        Welcome to AURA - AI-Driven Autonomous Research Assistant with TensorFlow Integration.
        
        I can help you with:
        - Retrieving academic papers
        - Summarizing research findings
        - Generating hypotheses
        - Designing experiments using TensorFlow
        - Analyzing papers with TensorFlow machine learning
        
        What would you like to research today?
    `;
    
    addMessageToChat('agent', welcomeMessage);
    
    // Scroll to bottom
    scrollToBottom();
}

// Add a message to the chat display
function addMessageToChat(role, content) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}-message`;
    
    // Format content with markdown-like syntax
    const formattedContent = markdownToHtml(escapeHtml(content));
    
    // Set content
    messageDiv.innerHTML = formattedContent;
    
    // Add agent type badge if it's an agent message
    if (role === 'agent' && content.startsWith('[') && content.includes(']')) {
        const agentType = content.substring(1, content.indexOf(']'));
        if (agentType) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-info float-end';
            badge.innerText = agentType;
            messageDiv.prepend(badge);
        }
    }
    
    // Remove typing indicator if exists
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    
    // Append message
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

// Add typing indicator to chat
function addTypingIndicator() {
    const chatContainer = document.getElementById('chatContainer');
    
    // Create typing indicator
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'chat-message agent-message typing-indicator';
    indicatorDiv.innerHTML = `
        <div class="typing-dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
    `;
    
    // Append indicator
    chatContainer.appendChild(indicatorDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

// Send chat message to server
function sendChatMessage(projectId, message) {
    fetch(`/api/projects/${projectId}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        // Handle agent response
        if (data.message) {
            addMessageToChat('agent', data.message);
        }
        
        // If there's any error, display it
        if (data.error) {
            showError(document.getElementById('chatContainer'), data.error);
        }
        
        // If there are papers, update paper list
        if (data.papers && typeof updatePapersList === 'function') {
            updatePapersList(data.papers);
        }
        
        // If there are hypotheses, update hypotheses list
        if (data.hypotheses && typeof updateHypothesesList === 'function') {
            updateHypothesesList(data.hypotheses);
        }
        
        // If there's a TensorFlow analysis, update visualization
        if (data.analysis_results && typeof updateTensorFlowAnalysis === 'function') {
            updateTensorFlowAnalysis(data.analysis_results);
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        
        // Remove typing indicator
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        // Add error message
        addMessageToChat('agent', 'Sorry, there was an error processing your request. Please try again.');
    });
}

// Scroll chat to bottom
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Submit a research query
function submitResearchQuery(projectId, query) {
    // Show loading status
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="text-center my-5"><span class="loader"></span><p class="mt-3">Processing your research query...</p></div>';
    }
    
    // Send query to server
    fetch(`/api/projects/${projectId}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    })
    .then(response => response.json())
    .then(data => {
        // Update UI with results
        if (data.message) {
            // Add to chat if available
            if (document.getElementById('chatContainer')) {
                addMessageToChat('agent', data.message);
            }
            
            // Update results container
            if (resultsContainer) {
                let resultsHTML = `<div class="alert alert-info">${data.message}</div>`;
                resultsContainer.innerHTML = resultsHTML;
            }
        }
        
        // If there are papers, update paper list
        if (data.papers && typeof updatePapersList === 'function') {
            updatePapersList(data.papers);
        }
        
        // If there are hypotheses, update hypotheses list
        if (data.hypotheses && typeof updateHypothesesList === 'function') {
            updateHypothesesList(data.hypotheses);
        }
        
        // If there's a TensorFlow analysis, update visualization
        if (data.analysis_results && typeof updateTensorFlowAnalysis === 'function') {
            updateTensorFlowAnalysis(data.analysis_results);
        }
        
        // If there's an error, display it
        if (data.error) {
            if (resultsContainer) {
                resultsContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            }
        }
    })
    .catch(error => {
        console.error('Error submitting research query:', error);
        
        // Show error in results container
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="alert alert-danger">An error occurred while processing your research query. Please try again.</div>';
        }
    });
}