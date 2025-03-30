/**
 * Export functionality for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize export functionality
    const exportBtn = document.getElementById('exportBtn');
    
    if (exportBtn) {
        exportBtn.addEventListener('click', exportProject);
    }
});

/**
 * Export the current project as JSON
 */
function exportProject() {
    const exportBtn = document.getElementById('exportBtn');
    exportBtn.disabled = true;
    exportBtn.textContent = 'Exporting...';
    
    fetch(`/api/projects/${projectId}/export`, {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error exporting project');
        }
        return response.json();
    })
    .then(data => {
        // Convert data to JSON string
        const jsonData = JSON.stringify(data, null, 2);
        
        // Create a blob and download link
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // Create and trigger a download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `aura_project_${projectId}_export.json`;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            exportBtn.disabled = false;
            exportBtn.textContent = 'Export Project';
        }, 100);
    })
    .catch(error => {
        console.error('Error exporting project:', error);
        alert('Failed to export project. Please try again.');
        exportBtn.disabled = false;
        exportBtn.textContent = 'Export Project';
    });
}