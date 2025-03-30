/**
 * Export JavaScript for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Export button click handler
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            // Show loading state
            exportBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exporting...';
            exportBtn.disabled = true;
            
            // Fetch project data
            fetch(`/api/projects/${projectId}/export`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Create a formatted JSON string
                    const jsonStr = JSON.stringify(data, null, 2);
                    
                    // Create a Blob containing the data
                    const blob = new Blob([jsonStr], { type: 'application/json' });
                    
                    // Create an URL for the Blob
                    const url = URL.createObjectURL(blob);
                    
                    // Create a temporary download link
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `aura-research-project-${projectId}.json`;
                    document.body.appendChild(a);
                    
                    // Trigger download
                    a.click();
                    
                    // Clean up
                    URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    // Reset button state
                    exportBtn.innerHTML = 'Export Project';
                    exportBtn.disabled = false;
                    
                    // Show success message
                    showExportMessage('success', 'Project exported successfully!');
                })
                .catch(error => {
                    console.error('Error exporting project:', error);
                    
                    // Reset button state
                    exportBtn.innerHTML = 'Export Project';
                    exportBtn.disabled = false;
                    
                    // Show error message
                    showExportMessage('danger', 'Error exporting project. Please try again.');
                });
        });
    }
});

/**
 * Show an export message
 * 
 * @param {string} type - 'success' or 'danger'
 * @param {string} message - The message to display
 */
function showExportMessage(type, message) {
    // Create alert element
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
    alertEl.setAttribute('role', 'alert');
    alertEl.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(alertEl);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertEl.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(alertEl);
        }, 150);
    }, 5000);
}