/**
 * AURA - AI-Driven Autonomous Research Assistant
 * Export functionality
 */

// Initialize export functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Set up export buttons if they exist
  const exportPdfButton = document.getElementById('export-pdf');
  if (exportPdfButton) {
    exportPdfButton.addEventListener('click', exportProjectAsPdf);
  }
  
  const exportJsonButton = document.getElementById('export-json');
  if (exportJsonButton) {
    exportJsonButton.addEventListener('click', exportProjectAsJson);
  }
  
  const exportCsvButton = document.getElementById('export-csv');
  if (exportCsvButton) {
    exportCsvButton.addEventListener('click', exportPapersAsCsv);
  }
  
  const exportBibButton = document.getElementById('export-bibtex');
  if (exportBibButton) {
    exportBibButton.addEventListener('click', exportPapersAsBibtex);
  }
});

/**
 * Export project as PDF
 */
async function exportProjectAsPdf() {
  // Get project ID from page
  const projectContainer = document.querySelector('[data-project-id]');
  if (!projectContainer) {
    showToast('Project ID not found', 'danger');
    return;
  }
  
  const projectId = projectContainer.dataset.projectId;
  
  try {
    // Show loading toast
    showToast('Generating PDF report...', 'info');
    
    // Fetch project data
    const projectData = await fetch(`/api/export/${projectId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(handleFetchErrors);
    
    if (projectData.error) {
      showToast(`Error: ${projectData.error}`, 'danger');
      return;
    }
    
    // Generate PDF using browser capabilities
    // For this implementation, we'll create a printable page in a new window
    const printWindow = window.open('', '_blank');
    
    if (!printWindow) {
      showToast('Pop-up blocked. Please allow pop-ups for this site.', 'warning');
      return;
    }
    
    // Prepare HTML content
    const projectTitle = projectData.project?.title || 'Research Project';
    const projectDesc = projectData.project?.description || '';
    
    let papersHtml = '';
    if (projectData.papers && projectData.papers.length > 0) {
      papersHtml = `
        <h2>Research Papers (${projectData.papers.length})</h2>
        <div class="papers-list">
          ${projectData.papers.map((paper, index) => `
            <div class="paper">
              <h3>${index + 1}. ${paper.title}</h3>
              <p><strong>Authors:</strong> ${Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors || 'Unknown'}</p>
              <p><strong>Source:</strong> ${paper.source || 'Unknown'}</p>
              ${paper.summary ? `
                <div class="summary">
                  <h4>Summary</h4>
                  <p>${paper.summary.text || ''}</p>
                  ${paper.summary.key_findings && paper.summary.key_findings.length > 0 ? `
                    <h4>Key Findings</h4>
                    <ul>
                      ${paper.summary.key_findings.map(finding => `<li>${finding}</li>`).join('')}
                    </ul>
                  ` : ''}
                </div>
              ` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }
    
    let hypothesesHtml = '';
    if (projectData.hypotheses && projectData.hypotheses.length > 0) {
      hypothesesHtml = `
        <h2>Research Hypotheses (${projectData.hypotheses.length})</h2>
        <div class="hypotheses-list">
          ${projectData.hypotheses.map((hyp, index) => `
            <div class="hypothesis">
              <h3>Hypothesis ${index + 1}</h3>
              <p>${hyp.text}</p>
              ${hyp.reasoning ? `<p><strong>Reasoning:</strong> ${hyp.reasoning}</p>` : ''}
              ${hyp.confidence_score ? `<p><strong>Confidence:</strong> ${Math.round(hyp.confidence_score * 100)}%</p>` : ''}
              
              ${hyp.experiments && hyp.experiments.length > 0 ? `
                <div class="experiments">
                  <h4>Proposed Experiments</h4>
                  ${hyp.experiments.map(exp => `
                    <div class="experiment">
                      <h5>${exp.title}</h5>
                      <p><strong>Methodology:</strong> ${exp.methodology || 'Not specified'}</p>
                      <p><strong>Expected Outcomes:</strong> ${exp.expected_outcomes || 'Not specified'}</p>
                    </div>
                  `).join('')}
                </div>
              ` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }
    
    // Write content to the new window
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>${projectTitle} - Research Report</title>
        <meta charset="UTF-8">
        <style>
          body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 30px;
            color: #333;
          }
          h1, h2, h3, h4 {
            color: #2c3e50;
          }
          h1 {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
          }
          h2 {
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
          }
          .paper, .hypothesis {
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px dotted #ddd;
          }
          .summary, .experiments {
            margin-left: 20px;
            padding-left: 15px;
            border-left: 3px solid #f0f0f0;
          }
          .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
          }
          @media print {
            body {
              margin: 20mm;
            }
            .no-print {
              display: none;
            }
          }
        </style>
      </head>
      <body>
        <div class="no-print" style="text-align: right; margin-bottom: 20px;">
          <button onclick="window.print()">Print Report</button>
        </div>
        
        <h1>${projectTitle}</h1>
        <p>${projectDesc}</p>
        
        <div class="report-date">
          <p><strong>Report Generated:</strong> ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}</p>
        </div>
        
        ${papersHtml}
        
        ${hypothesesHtml}
        
        <div class="footer">
          <p>Generated by AURA: AI-Driven Autonomous Research Assistant</p>
        </div>
      </body>
      </html>
    `);
    
    printWindow.document.close();
    
  } catch (error) {
    console.error('Error in exportProjectAsPdf:', error);
    showToast(`Export failed: ${error.message}`, 'danger');
  }
}

/**
 * Export project as JSON
 */
async function exportProjectAsJson() {
  // Get project ID from page
  const projectContainer = document.querySelector('[data-project-id]');
  if (!projectContainer) {
    showToast('Project ID not found', 'danger');
    return;
  }
  
  const projectId = projectContainer.dataset.projectId;
  
  try {
    // Show loading toast
    showToast('Generating JSON export...', 'info');
    
    // Fetch project data
    const projectData = await fetch(`/api/export/${projectId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(handleFetchErrors);
    
    if (projectData.error) {
      showToast(`Error: ${projectData.error}`, 'danger');
      return;
    }
    
    // Convert to formatted JSON string
    const jsonString = JSON.stringify(projectData, null, 2);
    
    // Create Blob and download link
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create filename from project title
    const projectTitle = projectData.project?.title || 'research_project';
    const filename = `${projectTitle.toLowerCase().replace(/\s+/g, '_')}_export.json`;
    
    // Create download link and click it
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
    
    showToast('JSON export complete', 'success');
    
  } catch (error) {
    console.error('Error in exportProjectAsJson:', error);
    showToast(`Export failed: ${error.message}`, 'danger');
  }
}

/**
 * Export papers as CSV
 */
async function exportPapersAsCsv() {
  // Get project ID from page
  const projectContainer = document.querySelector('[data-project-id]');
  if (!projectContainer) {
    showToast('Project ID not found', 'danger');
    return;
  }
  
  const projectId = projectContainer.dataset.projectId;
  
  try {
    // Show loading toast
    showToast('Generating CSV export...', 'info');
    
    // Fetch project data
    const projectData = await fetch(`/api/export/${projectId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(handleFetchErrors);
    
    if (projectData.error) {
      showToast(`Error: ${projectData.error}`, 'danger');
      return;
    }
    
    if (!projectData.papers || projectData.papers.length === 0) {
      showToast('No papers to export', 'warning');
      return;
    }
    
    // Create CSV content
    const headers = ['Title', 'Authors', 'Abstract', 'URL', 'Source', 'Published Date'];
    let csvContent = headers.join(',') + '\n';
    
    // Add paper rows
    projectData.papers.forEach(paper => {
      const authors = Array.isArray(paper.authors) ? paper.authors.join('; ') : paper.authors || '';
      
      // Escape fields to handle commas and quotes
      const escapeCsvField = field => {
        if (field === null || field === undefined) return '';
        const stringField = String(field).replace(/"/g, '""');
        return `"${stringField}"`;
      };
      
      const row = [
        escapeCsvField(paper.title),
        escapeCsvField(authors),
        escapeCsvField(paper.abstract),
        escapeCsvField(paper.url),
        escapeCsvField(paper.source),
        escapeCsvField(paper.published_date)
      ];
      
      csvContent += row.join(',') + '\n';
    });
    
    // Create Blob and download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    // Create filename from project title
    const projectTitle = projectData.project?.title || 'research_papers';
    const filename = `${projectTitle.toLowerCase().replace(/\s+/g, '_')}_papers.csv`;
    
    // Create download link and click it
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
    
    showToast('CSV export complete', 'success');
    
  } catch (error) {
    console.error('Error in exportPapersAsCsv:', error);
    showToast(`Export failed: ${error.message}`, 'danger');
  }
}

/**
 * Export papers as BibTeX
 */
async function exportPapersAsBibtex() {
  // Get project ID from page
  const projectContainer = document.querySelector('[data-project-id]');
  if (!projectContainer) {
    showToast('Project ID not found', 'danger');
    return;
  }
  
  const projectId = projectContainer.dataset.projectId;
  
  try {
    // Show loading toast
    showToast('Generating BibTeX export...', 'info');
    
    // Fetch project data
    const projectData = await fetch(`/api/export/${projectId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(handleFetchErrors);
    
    if (projectData.error) {
      showToast(`Error: ${projectData.error}`, 'danger');
      return;
    }
    
    if (!projectData.papers || projectData.papers.length === 0) {
      showToast('No papers to export', 'warning');
      return;
    }
    
    // Create BibTeX content
    let bibtexContent = '';
    
    // Add paper entries
    projectData.papers.forEach((paper, index) => {
      // Create citation key
      let firstAuthor = 'Unknown';
      if (Array.isArray(paper.authors) && paper.authors.length > 0) {
        firstAuthor = paper.authors[0].split(' ').pop(); // Last name of first author
      }
      
      // Get year from published date
      let year = new Date().getFullYear();
      if (paper.published_date) {
        year = new Date(paper.published_date).getFullYear();
      }
      
      const citationKey = `${firstAuthor}${year}${paper.source || ''}`;
      
      // Determine publication type
      let pubType = 'article'; // Default
      if (paper.source === 'arxiv') {
        pubType = 'misc'; // ArXiv preprints are usually misc
      }
      
      // Format authors for BibTeX
      let authorString = '';
      if (Array.isArray(paper.authors) && paper.authors.length > 0) {
        authorString = paper.authors.join(' and ');
      }
      
      // Create BibTeX entry
      bibtexContent += `@${pubType}{${citationKey},
  title = {${paper.title || 'Unknown Title'}},
  author = {${authorString}},
  ${paper.published_date ? `year = {${year}},` : ''}
  ${paper.abstract ? `abstract = {${paper.abstract.replace(/[{}]/g, '')}},` : ''}
  ${paper.url ? `url = {${paper.url}},` : ''}
  ${paper.source ? `note = {Source: ${paper.source}}` : ''}
}

`;
    });
    
    // Create Blob and download link
    const blob = new Blob([bibtexContent], { type: 'application/x-bibtex' });
    const url = URL.createObjectURL(blob);
    
    // Create filename from project title
    const projectTitle = projectData.project?.title || 'research_papers';
    const filename = `${projectTitle.toLowerCase().replace(/\s+/g, '_')}_references.bib`;
    
    // Create download link and click it
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
    
    showToast('BibTeX export complete', 'success');
    
  } catch (error) {
    console.error('Error in exportPapersAsBibtex:', error);
    showToast(`Export failed: ${error.message}`, 'danger');
  }
}
