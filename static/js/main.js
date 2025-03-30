/**
 * Main JavaScript for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create Project
    const createProjectBtn = document.getElementById('createProjectBtn');
    if (createProjectBtn) {
        createProjectBtn.addEventListener('click', createProject);
    }
    
    // Delete Project
    const deleteProjectBtns = document.querySelectorAll('.delete-project');
    deleteProjectBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const projectId = this.getAttribute('data-project-id');
            if (confirm('Are you sure you want to delete this project? This cannot be undone.')) {
                deleteProject(projectId);
            }
        });
    });
    
    // Add Paper buttons
    const addPaperBtn = document.getElementById('addPaperBtn');
    if (addPaperBtn) {
        addPaperBtn.addEventListener('click', function() {
            const addPaperModal = new bootstrap.Modal(document.getElementById('addPaperModal'));
            addPaperModal.show();
        });
    }
    
    const addPaperBtn2 = document.getElementById('addPaperBtn2');
    if (addPaperBtn2) {
        addPaperBtn2.addEventListener('click', function() {
            const addPaperModal = new bootstrap.Modal(document.getElementById('addPaperModal'));
            addPaperModal.show();
        });
    }
    
    // Save Paper
    const savePaperBtn = document.getElementById('savePaperBtn');
    if (savePaperBtn) {
        savePaperBtn.addEventListener('click', savePaper);
    }
    
    // Search Papers
    const paperSearchBtn = document.getElementById('paperSearchBtn');
    if (paperSearchBtn) {
        paperSearchBtn.addEventListener('click', searchPapers);
    }
    
    // View Paper
    const viewPaperBtns = document.querySelectorAll('.view-paper');
    viewPaperBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const paperId = this.getAttribute('data-paper-id');
            viewPaper(paperId);
        });
    });
    
    // Research Query Form
    const researchQueryForm = document.getElementById('researchQueryForm');
    if (researchQueryForm) {
        researchQueryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitResearchQuery();
        });
    }
    
    // TensorFlow Analysis
    const runAnalysisBtn = document.getElementById('runAnalysisBtn');
    if (runAnalysisBtn) {
        runAnalysisBtn.addEventListener('click', runTensorFlowAnalysis);
    }
    
    // Export Results
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportResults);
    }
    
    // Generate Hypothesis
    const generateHypothesisBtn = document.getElementById('generateHypothesisBtn');
    if (generateHypothesisBtn) {
        generateHypothesisBtn.addEventListener('click', generateHypothesis);
    }
});

/**
 * Create a new research project
 */
function createProject() {
    const title = document.getElementById('projectTitle').value.trim();
    const description = document.getElementById('projectDescription').value.trim();
    
    if (!title) {
        alert('Please enter a project title');
        return;
    }
    
    fetch('/api/projects', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title,
            description: description
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createProjectModal'));
            modal.hide();
            
            // Redirect to new project
            window.location.href = `/research/${data.id}`;
        }
    })
    .catch(error => {
        console.error('Error creating project:', error);
        alert('Error creating project. Please try again.');
    });
}

/**
 * Delete a research project
 */
function deleteProject(projectId) {
    fetch(`/api/projects/${projectId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Reload the page
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error deleting project:', error);
        alert('Error deleting project. Please try again.');
    });
}

/**
 * Save a new paper to the project
 */
function savePaper() {
    const title = document.getElementById('addPaperTitle').value.trim();
    const authors = document.getElementById('addPaperAuthors').value.trim();
    const abstract = document.getElementById('addPaperAbstract').value.trim();
    const url = document.getElementById('addPaperUrl').value.trim();
    const publishedDate = document.getElementById('addPaperPublishedDate').value;
    
    if (!title) {
        alert('Please enter a paper title');
        return;
    }
    
    // Process authors into an array
    let authorsArray = [];
    if (authors) {
        authorsArray = authors.split(',').map(author => author.trim());
    }
    
    fetch(`/api/projects/${projectId}/papers`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title,
            authors: authorsArray,
            abstract: abstract,
            url: url,
            published_date: publishedDate,
            source: 'manual'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addPaperModal'));
            modal.hide();
            
            // Reload the page
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error adding paper:', error);
        alert('Error adding paper. Please try again.');
    });
}

/**
 * Search for papers
 */
function searchPapers() {
    const query = document.getElementById('paperSearchInput').value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    // Show loading state
    document.getElementById('paperSearchBtn').disabled = true;
    document.getElementById('paperSearchBtn').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
    
    // Close search modal and open results modal
    const searchModal = bootstrap.Modal.getInstance(document.getElementById('searchPapersModal'));
    searchModal.hide();
    
    const resultsModal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
    resultsModal.show();
    
    // Set loading state in results modal
    document.getElementById('searchResultsContent').innerHTML = `
        <div class="spinner-container">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="ms-3">Searching academic papers...</p>
        </div>
    `;
    
    // Make API call to search for papers
    fetch(`/api/search?query=${encodeURIComponent(query)}&project_id=${projectId}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        // Reset search button
        document.getElementById('paperSearchBtn').disabled = false;
        document.getElementById('paperSearchBtn').textContent = 'Search';
        
        if (data.error) {
            document.getElementById('searchResultsContent').innerHTML = `
                <div class="alert alert-danger">
                    <p>Error: ${data.error}</p>
                </div>
            `;
        } else if (data.papers && data.papers.length > 0) {
            // Display results
            let resultsHtml = `
                <p>${data.papers.length} papers found for "${query}"</p>
                <div class="list-group">
            `;
            
            data.papers.forEach(paper => {
                resultsHtml += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5>${paper.title}</h5>
                                <p class="mb-1">
                                    <small class="text-muted">
                                        ${paper.authors.join(', ') || 'Unknown authors'}
                                    </small>
                                </p>
                                <p class="mb-1">${paper.abstract?.substring(0, 200) || ''}${paper.abstract?.length > 200 ? '...' : ''}</p>
                                <div class="mt-2">
                                    <span class="badge bg-secondary me-2">${paper.source}</span>
                                    ${paper.published_date ? `<span class="badge bg-secondary">${new Date(paper.published_date).toISOString().split('T')[0]}</span>` : ''}
                                </div>
                            </div>
                            <div class="ms-3">
                                <button class="btn btn-sm btn-info add-search-paper" data-paper-id="${paper.id}">
                                    Add to Project
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            resultsHtml += `</div>`;
            document.getElementById('searchResultsContent').innerHTML = resultsHtml;
            
            // Add event listeners to add paper buttons
            document.querySelectorAll('.add-search-paper').forEach(btn => {
                btn.addEventListener('click', function() {
                    const paperId = this.getAttribute('data-paper-id');
                    addPaperFromSearch(paperId);
                });
            });
        } else {
            document.getElementById('searchResultsContent').innerHTML = `
                <div class="alert alert-secondary">
                    <p>No papers found for "${query}"</p>
                    <p>Try a different search query or add a paper manually.</p>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Error searching papers:', error);
        document.getElementById('paperSearchBtn').disabled = false;
        document.getElementById('paperSearchBtn').textContent = 'Search';
        document.getElementById('searchResultsContent').innerHTML = `
            <div class="alert alert-danger">
                <p>Error searching papers. Please try again.</p>
            </div>
        `;
    });
}

/**
 * Add a paper from search results
 */
function addPaperFromSearch(paperId) {
    fetch(`/api/papers/${paperId}/add?project_id=${projectId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Update button to show success
            const btn = document.querySelector(`.add-search-paper[data-paper-id="${paperId}"]`);
            btn.classList.remove('btn-info');
            btn.classList.add('btn-success');
            btn.disabled = true;
            btn.textContent = 'Added';
            
            // Reload page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    })
    .catch(error => {
        console.error('Error adding paper:', error);
        alert('Error adding paper. Please try again.');
    });
}

/**
 * View paper details
 */
function viewPaper(paperId) {
    fetch(`/api/projects/${projectId}/papers/${paperId}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Populate modal with paper details
            document.getElementById('paperTitle').textContent = data.title;
            document.getElementById('paperAuthors').textContent = data.authors?.join(', ') || 'Unknown authors';
            document.getElementById('paperAbstract').textContent = data.abstract || 'No abstract available';
            document.getElementById('paperSource').textContent = data.source || '-';
            document.getElementById('paperDate').textContent = data.published_date ? new Date(data.published_date).toLocaleDateString() : '-';
            
            // Set URLs if available
            const paperUrl = document.getElementById('paperUrl');
            const paperPdfUrl = document.getElementById('paperPdfUrl');
            
            if (data.url) {
                paperUrl.href = data.url;
                paperUrl.classList.remove('d-none');
            } else {
                paperUrl.classList.add('d-none');
            }
            
            if (data.pdf_url) {
                paperPdfUrl.href = data.pdf_url;
                paperPdfUrl.classList.remove('d-none');
            } else {
                paperPdfUrl.classList.add('d-none');
            }
            
            // Configure summarize button
            const summarizeBtn = document.getElementById('summarizePaperBtn');
            if (data.summary) {
                summarizeBtn.textContent = 'View Summary';
                summarizeBtn.setAttribute('data-has-summary', 'true');
            } else {
                summarizeBtn.textContent = 'Summarize with TensorFlow';
                summarizeBtn.setAttribute('data-has-summary', 'false');
            }
            
            summarizeBtn.setAttribute('data-paper-id', paperId);
            
            // Add event listener for summarize button
            summarizeBtn.addEventListener('click', function() {
                const hasSummary = this.getAttribute('data-has-summary') === 'true';
                if (hasSummary) {
                    viewSummary(paperId);
                } else {
                    summarizePaper(paperId);
                }
            });
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('viewPaperModal'));
            modal.show();
        }
    })
    .catch(error => {
        console.error('Error fetching paper details:', error);
        alert('Error fetching paper details. Please try again.');
    });
}

/**
 * Summarize a paper
 */
function summarizePaper(paperId) {
    // Update button to show loading state
    const summarizeBtn = document.getElementById('summarizePaperBtn');
    summarizeBtn.disabled = true;
    summarizeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Summarizing...';
    
    fetch(`/api/projects/${projectId}/papers/${paperId}/summarize`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Reset button
        summarizeBtn.disabled = false;
        
        if (data.error) {
            summarizeBtn.textContent = 'Summarize with TensorFlow';
            alert('Error: ' + data.error);
        } else {
            summarizeBtn.textContent = 'View Summary';
            summarizeBtn.setAttribute('data-has-summary', 'true');
            
            // Reload the page to show the updated summary
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error summarizing paper:', error);
        summarizeBtn.disabled = false;
        summarizeBtn.textContent = 'Summarize with TensorFlow';
        alert('Error summarizing paper. Please try again.');
    });
}

/**
 * Submit a research query
 */
function submitResearchQuery() {
    const queryText = document.getElementById('queryText').value.trim();
    
    if (!queryText) {
        alert('Please enter a research query');
        return;
    }
    
    // Disable form
    const submitBtn = document.querySelector('#researchQueryForm button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Researching...';
    
    fetch(`/api/projects/${projectId}/research`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query_text: queryText
        })
    })
    .then(response => response.json())
    .then(data => {
        // Reset form
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="tensorflow-badge small">TF</span> Research with TensorFlow';
        
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Show results
            const resultsCard = document.getElementById('analysisResults');
            resultsCard.classList.remove('d-none');
            
            // Populate results
            document.getElementById('analysisContent').innerHTML = `
                <h5>Research Results</h5>
                <p>${data.message || 'Research completed successfully'}</p>
                <div class="mt-4">
                    <h6>Key Findings:</h6>
                    <ul>
                        ${data.findings ? data.findings.map(finding => `<li>${finding}</li>`).join('') : '<li>No specific findings to display</li>'}
                    </ul>
                </div>
            `;
            
            // Scroll to results
            resultsCard.scrollIntoView({ behavior: 'smooth' });
            
            // If visualization data is available, render it
            if (data.visualization_data) {
                renderVisualization(data.visualization_data);
            }
        }
    })
    .catch(error => {
        console.error('Error submitting research query:', error);
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="tensorflow-badge small">TF</span> Research with TensorFlow';
        alert('Error submitting research query. Please try again.');
    });
}

/**
 * Run TensorFlow analysis
 */
function runTensorFlowAnalysis() {
    // Get selected analysis type
    let analysisType = 'all';
    document.querySelectorAll('input[name="analysisType"]').forEach(radio => {
        if (radio.checked) {
            analysisType = radio.id.replace('analysisType', '').toLowerCase();
        }
    });
    
    // Close the modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('tensorflowModal'));
    modal.hide();
    
    // Show loading state
    const analysisContainer = document.getElementById('tfAnalysisResults') || document.getElementById('analysisContent');
    analysisContainer.innerHTML = `
        <div class="spinner-container">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="ms-3">Running TensorFlow analysis...</p>
        </div>
    `;
    
    // Make the analysis tab active if it exists
    if (document.getElementById('analysis-tab')) {
        bootstrap.Tab.getOrCreateInstance(document.getElementById('analysis-tab')).show();
    }
    
    // Run analysis
    fetch(`/api/projects/${projectId}/tf-analysis`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            analysis_type: analysisType === 'all' ? 'all' : analysisType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            analysisContainer.innerHTML = `
                <div class="alert alert-danger">
                    <p>Error: ${data.error}</p>
                </div>
            `;
        } else {
            // Handle different types of analysis
            if (analysisType === 'gap' || analysisType === 'all') {
                displayResearchGaps(data, analysisContainer);
            } else {
                displayAnalysisResults(data, analysisContainer, analysisType);
            }
            
            // If visualization data is available, render it
            if (data.visualization_data) {
                renderVisualization(data.visualization_data);
            }
        }
    })
    .catch(error => {
        console.error('Error running TensorFlow analysis:', error);
        analysisContainer.innerHTML = `
            <div class="alert alert-danger">
                <p>Error running TensorFlow analysis. Please try again.</p>
            </div>
        `;
    });
}

/**
 * Display analysis results
 */
function displayAnalysisResults(data, container, analysisType) {
    let html = `
        <div class="alert alert-info">
            <p>${data.message || 'TensorFlow analysis completed successfully'}</p>
        </div>
    `;
    
    // Topic analysis
    if (data.topic_analysis && (analysisType === 'topic' || analysisType === 'all')) {
        html += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0">Topic Analysis</h4>
                </div>
                <div class="card-body">
                    <p>${data.topic_analysis.description || 'Topic modeling was performed on the research papers.'}</p>
                    <div class="row">
        `;
        
        data.topic_analysis.topics.forEach(topic => {
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0">Topic ${topic.id}</h5>
                        </div>
                        <div class="card-body">
                            <p class="card-text">${topic.description}</p>
                            <h6>Key Terms:</h6>
                            <p>${topic.keywords.join(', ')}</p>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
    }
    
    // Cluster analysis
    if (data.cluster_analysis && (analysisType === 'cluster' || analysisType === 'all')) {
        html += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0">Cluster Analysis</h4>
                </div>
                <div class="card-body">
                    <p>${data.cluster_analysis.description || 'Papers were clustered based on their content.'}</p>
                    <div id="clusterVisualization" class="visualization-container mt-4"></div>
                </div>
            </div>
        `;
    }
    
    // Trend analysis
    if (data.trend_analysis && (analysisType === 'trend' || analysisType === 'all')) {
        html += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0">Trend Analysis</h4>
                </div>
                <div class="card-body">
                    <p>${data.trend_analysis.description || 'Research trends were analyzed over time.'}</p>
                    <div id="trendVisualization" class="visualization-container mt-4"></div>
                </div>
            </div>
        `;
    }
    
    // Update container
    container.innerHTML = html;
}

/**
 * Display research gaps
 */
function displayResearchGaps(data, container) {
    let html = `
        <div class="alert alert-info">
            <p>${data.message || 'Research gap analysis completed successfully'}</p>
        </div>
        <div class="card mb-4">
            <div class="card-header bg-info text-white">
                <h4 class="mb-0">Research Gaps</h4>
            </div>
            <div class="card-body">
                <p>${data.description || 'The following research gaps were identified based on TensorFlow analysis.'}</p>
                <div class="mt-4">
    `;
    
    if (data.gaps && data.gaps.length > 0) {
        html += '<div class="row">';
        data.gaps.forEach(gap => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Research Gap</h5>
                            <span class="badge bg-info">${gap.confidence * 100}% Confidence</span>
                        </div>
                        <div class="card-body">
                            <p>${gap.description}</p>
                            <h6>Potential Research Directions:</h6>
                            <ul>
            `;
            
            gap.suggestions.forEach(suggestion => {
                html += `<li>${suggestion}</li>`;
            });
            
            html += `
                            </ul>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-sm btn-outline-info generate-hypothesis-from-gap" data-gap="${encodeURIComponent(gap.description)}">
                                Generate Hypothesis
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += `
            <div class="alert alert-secondary">
                <p>No specific research gaps were identified.</p>
                <p>This could indicate that the research area is well-covered or that more papers are needed for analysis.</p>
            </div>
        `;
    }
    
    html += `
                </div>
            </div>
        </div>
    `;
    
    // Update container
    container.innerHTML = html;
    
    // Add event listeners for generate hypothesis buttons
    document.querySelectorAll('.generate-hypothesis-from-gap').forEach(btn => {
        btn.addEventListener('click', function() {
            const gapDescription = decodeURIComponent(this.getAttribute('data-gap'));
            const modal = new bootstrap.Modal(document.getElementById('generateHypothesisModal'));
            document.getElementById('researchQuestion').value = gapDescription;
            modal.show();
        });
    });
}

/**
 * Generate a hypothesis based on research
 */
function generateHypothesis() {
    const researchQuestion = document.getElementById('researchQuestion').value.trim();
    
    if (!researchQuestion) {
        alert('Please enter a research question');
        return;
    }
    
    // Disable button and show loading state
    const generateBtn = document.getElementById('generateHypothesisBtn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
    
    fetch(`/api/projects/${projectId}/hypothesis`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            research_question: researchQuestion
        })
    })
    .then(response => response.json())
    .then(data => {
        // Reset button
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="tensorflow-badge small">TF</span> Generate';
        
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('generateHypothesisModal'));
            modal.hide();
            
            // Reload the page to show the new hypothesis
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error generating hypothesis:', error);
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="tensorflow-badge small">TF</span> Generate';
        alert('Error generating hypothesis. Please try again.');
    });
}

/**
 * Export project results
 */
function exportResults() {
    // Get export options
    const includeHypotheses = document.getElementById('exportHypotheses').checked;
    const includeExperiments = document.getElementById('exportExperiments').checked;
    const includePaperSummaries = document.getElementById('exportPaperSummaries').checked;
    const includeTensorFlowAnalysis = document.getElementById('exportTensorFlowAnalysis').checked;
    const format = document.getElementById('exportFormatJSON').checked ? 'json' : 'md';
    
    // Generate filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `aura-project-${projectId}-${timestamp}.${format === 'json' ? 'json' : 'md'}`;
    
    // Make export request
    fetch(`/api/projects/${projectId}/export`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            include_hypotheses: includeHypotheses,
            include_experiments: includeExperiments,
            include_paper_summaries: includePaperSummaries,
            include_tensorflow_analysis: includeTensorFlowAnalysis,
            format: format
        })
    })
    .then(response => {
        if (format === 'json') {
            return response.json();
        } else {
            return response.text();
        }
    })
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Create download link
            const blob = format === 'json' 
                ? new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
                : new Blob([data], { type: 'text/markdown' });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
            modal.hide();
        }
    })
    .catch(error => {
        console.error('Error exporting results:', error);
        alert('Error exporting results. Please try again.');
    });
}