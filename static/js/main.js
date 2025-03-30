// Main JavaScript for AURA Research Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Project creation
    const createProjectBtn = document.getElementById('createProjectBtn');
    if (createProjectBtn) {
        createProjectBtn.addEventListener('click', createProject);
    }
    
    // Project deletion
    const deleteButtons = document.querySelectorAll('.delete-project');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const projectId = this.getAttribute('data-project-id');
            deleteProject(projectId);
        });
    });
});

// Create a new research project
function createProject() {
    const title = document.getElementById('projectTitle').value;
    const description = document.getElementById('projectDescription').value;
    
    if (!title) {
        alert('Please enter a project title');
        return;
    }
    
    fetch('/api/projects', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, description })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Project created:', data);
        window.location.href = `/research/${data.id}`;
    })
    .catch(error => {
        console.error('Error creating project:', error);
        alert('Error creating project. Please try again.');
    });
}

// Delete a research project
function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
        return;
    }
    
    fetch(`/api/projects/${projectId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Remove the project card from the page
            const projectCard = document.querySelector(`[data-project-id="${projectId}"]`).closest('.col-md-4');
            projectCard.remove();
            
            // Refresh if no projects remain
            if (document.querySelectorAll('.research-projects .card').length === 0) {
                window.location.reload();
            }
        } else {
            throw new Error('Failed to delete project');
        }
    })
    .catch(error => {
        console.error('Error deleting project:', error);
        alert('Error deleting project. Please try again.');
    });
}

// Format a date string for display
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric'
    }).format(date);
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<span class="loader"></span>';
    element.disabled = true;
}

// Hide loading spinner
function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Display an error message
function showError(container, message) {
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Convert markdown-like text to HTML
function markdownToHtml(text) {
    if (!text) return '';
    
    // Convert line breaks
    let html = text.replace(/\n/g, '<br>');
    
    // Bold text
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Lists
    html = html.replace(/^\s*-\s+(.*?)(?:\n|$)/gm, '<li>$1</li>');
    html = html.replace(/<li>(.*?)<\/li>(?:\s*<li>)/g, '<li>$1</li><li>');
    html = html.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
    
    return html;
}

// Format confidence score as a badge
function formatConfidenceScore(score) {
    let badgeClass = 'bg-danger';
    if (score >= 0.7) {
        badgeClass = 'bg-success';
    } else if (score >= 0.4) {
        badgeClass = 'bg-warning';
    }
    
    return `<span class="badge ${badgeClass}">${(score * 100).toFixed(0)}%</span>`;
}

// Format authors list
function formatAuthors(authors) {
    if (!authors || authors.length === 0) return '';
    
    if (authors.length === 1) {
        return authors[0];
    } else if (authors.length === 2) {
        return `${authors[0]} and ${authors[1]}`;
    } else {
        return `${authors[0]} et al.`;
    }
}