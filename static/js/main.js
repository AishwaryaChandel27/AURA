/**
 * Main JavaScript for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Project creation
    const createProjectBtn = document.getElementById('createProjectBtn');
    if (createProjectBtn) {
        createProjectBtn.addEventListener('click', createProject);
    }
    
    // Project deletion
    const deleteProjectBtns = document.querySelectorAll('.delete-project-btn');
    deleteProjectBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project-id');
            document.getElementById('deleteProjectId').value = projectId;
        });
    });
    
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', deleteProject);
    }
    
    // Paper search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            searchPapers();
        });
    }
    
    // Hypothesis generation
    const generateHypothesisBtn = document.getElementById('generateHypothesisBtn');
    if (generateHypothesisBtn) {
        generateHypothesisBtn.addEventListener('click', generateHypothesis);
    }
    
    // Experiment design
    const experimentModalBtns = document.querySelectorAll('[data-bs-target="#designExperimentModal"]');
    experimentModalBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const hypothesisId = this.getAttribute('data-hypothesis-id');
            const hypothesisText = document.querySelector(`#hypothesis${hypothesisId} .accordion-body p:first-child`).textContent;
            document.getElementById('hypothesisId').value = hypothesisId;
            document.getElementById('selectedHypothesis').textContent = hypothesisText;
        });
    });
    
    const designExperimentBtn = document.getElementById('designExperimentBtn');
    if (designExperimentBtn) {
        designExperimentBtn.addEventListener('click', designExperiment);
    }
    
    // TensorFlow analysis
    const analysisBtn = document.getElementById('analysisBtn');
    if (analysisBtn) {
        analysisBtn.addEventListener('click', function() {
            runTensorFlowAnalysis('all');
        });
    }
    
    const gapsBtn = document.getElementById('gapsBtn');
    if (gapsBtn) {
        gapsBtn.addEventListener('click', identifyResearchGaps);
    }
    
    // Paper summarization
    const summarizeBtns = document.querySelectorAll('.summarize-btn');
    summarizeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const paperId = this.getAttribute('data-paper-id');
            summarizePaper(paperId);
        });
    });
    
    // Initialize tooltips and popovers
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });
});

/**
 * Create a new research project
 */
function createProject() {
    const title = document.getElementById('projectTitle').value;
    const description = document.getElementById('projectDescription').value;
    
    if (!title) {
        alert('Project title is required');
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
    .then(response => {
        if (!response.ok) {
            throw new Error('Error creating project');
        }
        return response.json();
    })
    .then(data => {
        // Redirect to the new project's research page
        window.location.href = `/research/${data.id}`;
    })
    .catch(error => {
        console.error('Error creating project:', error);
        alert('Failed to create project. Please try again.');
    });
}

/**
 * Delete a research project
 */
function deleteProject() {
    const projectId = document.getElementById('deleteProjectId').value;
    
    if (!projectId) {
        return;
    }
    
    fetch(`/api/projects/${projectId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error deleting project');
        }
        return response.json();
    })
    .then(data => {
        // Refresh the page to update the project list
        window.location.reload();
    })
    .catch(error => {
        console.error('Error deleting project:', error);
        alert('Failed to delete project. Please try again.');
    });
}

/**
 * Search for papers based on the query
 */
function searchPapers() {
    const query = document.getElementById('searchQuery').value;
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    // Show loading spinner
    document.getElementById('searchLoading').classList.remove('d-none');
    document.getElementById('searchResults').classList.add('d-none');
    
    fetch(`/api/projects/${projectId}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: query
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error searching for papers');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading spinner
        document.getElementById('searchLoading').classList.add('d-none');
        
        // Display results
        const resultsList = document.getElementById('resultsList');
        resultsList.innerHTML = '';
        
        if (data.results && data.results.length > 0) {
            data.results.forEach(paper => {
                const paperItem = document.createElement('div');
                paperItem.className = 'list-group-item bg-dark mb-2';
                
                // Create paper HTML
                let authorText = 'Unknown Authors';
                if (paper.authors && paper.authors.length > 0) {
                    authorText = paper.authors.join(', ');
                }
                
                paperItem.innerHTML = `
                    <h6>${paper.title}</h6>
                    <p class="small text-muted mb-1">${authorText}</p>
                    <p class="small mb-2">${paper.abstract ? paper.abstract.substring(0, 200) + '...' : 'No abstract available'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        ${paper.url ? `<a href="${paper.url}" target="_blank" class="btn btn-sm btn-outline-info">View Original</a>` : ''}
                        <button class="btn btn-sm btn-primary add-paper-btn">Add to Project</button>
                    </div>
                `;
                
                // Add event listener to the Add button
                paperItem.querySelector('.add-paper-btn').addEventListener('click', function() {
                    addPaperToProject(paper);
                });
                
                resultsList.appendChild(paperItem);
            });
            
            document.getElementById('searchResults').classList.remove('d-none');
        } else {
            resultsList.innerHTML = '<div class="alert alert-info">No papers found for your query. Try broadening your search terms.</div>';
            document.getElementById('searchResults').classList.remove('d-none');
        }
    })
    .catch(error => {
        console.error('Error searching for papers:', error);
        document.getElementById('searchLoading').classList.add('d-none');
        alert('Failed to search for papers. Please try again.');
    });
}

/**
 * Add a paper to the current project
 */
function addPaperToProject(paper) {
    fetch(`/api/projects/${projectId}/papers`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(paper)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error adding paper');
        }
        return response.json();
    })
    .then(data => {
        alert('Paper added to your project successfully');
        // Reload the page to show the new paper
        window.location.reload();
    })
    .catch(error => {
        console.error('Error adding paper:', error);
        alert('Failed to add paper. Please try again.');
    });
}

/**
 * Summarize a paper
 */
function summarizePaper(paperId) {
    const button = document.querySelector(`.summarize-btn[data-paper-id="${paperId}"]`);
    button.disabled = true;
    button.textContent = 'Summarizing...';
    
    fetch(`/api/papers/${paperId}/summarize`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error summarizing paper');
        }
        return response.json();
    })
    .then(data => {
        alert('Paper summarized successfully');
        // Reload the page to show the summary
        window.location.reload();
    })
    .catch(error => {
        console.error('Error summarizing paper:', error);
        button.disabled = false;
        button.textContent = 'Summarize';
        alert('Failed to summarize paper. Please try again.');
    });
}

/**
 * Generate a hypothesis based on the research question
 */
function generateHypothesis() {
    const researchQuestion = document.getElementById('researchQuestion').value;
    
    if (!researchQuestion) {
        alert('Please enter a research question');
        return;
    }
    
    // Show loading indicator
    document.getElementById('hypothesisLoading').classList.remove('d-none');
    
    fetch(`/api/projects/${projectId}/hypotheses`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            research_question: researchQuestion
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error generating hypothesis');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        document.getElementById('hypothesisLoading').classList.add('d-none');
        alert('Hypothesis generated successfully');
        // Reload the page to show the new hypothesis
        window.location.reload();
    })
    .catch(error => {
        console.error('Error generating hypothesis:', error);
        document.getElementById('hypothesisLoading').classList.add('d-none');
        alert('Failed to generate hypothesis. Please try again.');
    });
}

/**
 * Design an experiment for a hypothesis
 */
function designExperiment() {
    const hypothesisId = document.getElementById('hypothesisId').value;
    
    if (!hypothesisId) {
        return;
    }
    
    // Show loading indicator
    document.getElementById('experimentLoading').classList.remove('d-none');
    document.getElementById('experimentResult').classList.add('d-none');
    
    fetch(`/api/hypotheses/${hypothesisId}/experiments`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error designing experiment');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator and show result
        document.getElementById('experimentLoading').classList.add('d-none');
        document.getElementById('experimentResult').classList.remove('d-none');
        
        // Disable the design button
        document.getElementById('designExperimentBtn').disabled = true;
    })
    .catch(error => {
        console.error('Error designing experiment:', error);
        document.getElementById('experimentLoading').classList.add('d-none');
        alert('Failed to design experiment. Please try again.');
    });
}

/**
 * Run TensorFlow analysis on project papers
 */
function runTensorFlowAnalysis(analysisType) {
    // Show loading in the results area
    const resultsContainer = document.getElementById('analysisResults');
    resultsContainer.classList.remove('d-none');
    resultsContainer.innerHTML = `
        <div class="text-center my-4">
            <div class="loading-spinner"></div>
            <p class="mt-2">Running TensorFlow analysis...</p>
        </div>
    `;
    
    fetch(`/api/projects/${projectId}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            analysis_type: analysisType
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error running analysis');
        }
        return response.json();
    })
    .then(data => {
        // Display analysis results
        displayAnalysisResults(data);
    })
    .catch(error => {
        console.error('Error running TensorFlow analysis:', error);
        resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <p class="mb-0">Error running TensorFlow analysis. Please try again.</p>
            </div>
        `;
    });
}

/**
 * Display TensorFlow analysis results
 */
function displayAnalysisResults(data) {
    const resultsContainer = document.getElementById('analysisResults');
    const resultContent = document.getElementById('resultContent');
    const visualizationContainer = document.getElementById('visualizationContainer');
    
    // Create results HTML
    let html = `<div class="alert alert-info mb-4">
        <p class="mb-0">${data.analysis_summary}</p>
    </div>`;
    
    // Add clustering results if available
    if (data.clustering && !data.clustering.error) {
        html += `<div class="card bg-dark mb-4">
            <div class="card-header">
                <h6 class="mb-0">Paper Clusters</h6>
            </div>
            <div class="card-body">
                <p>Papers have been clustered into ${data.clustering.num_clusters} groups based on content similarity.</p>
                <div class="accordion" id="clusterAccordion">`;
        
        data.clustering.clusters.forEach((cluster, index) => {
            html += `
                <div class="accordion-item bg-dark">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed bg-dark text-white" type="button" data-bs-toggle="collapse" data-bs-target="#cluster${index}">
                            Cluster ${index + 1} (${cluster.paper_count} papers)
                        </button>
                    </h2>
                    <div id="cluster${index}" class="accordion-collapse collapse" data-bs-parent="#clusterAccordion">
                        <div class="accordion-body">
                            <p><strong>Keywords:</strong> ${cluster.keywords.join(', ')}</p>
                            <p><strong>Papers in this cluster:</strong></p>
                            <ul>
                                ${cluster.papers.map(paper => `<li>${paper}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>`;
        });
        
        html += `</div></div></div>`;
    }
    
    // Add TensorFlow insights
    if (data.tensorflow_insights) {
        html += `<div class="card bg-dark mb-4">
            <div class="card-header">
                <h6 class="mb-0">TensorFlow Insights</h6>
            </div>
            <div class="card-body">
                <p><strong>TensorFlow papers:</strong> ${data.tensorflow_insights.tensorflow_papers_count} (${data.tensorflow_insights.tensorflow_percentage}% of total)</p>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <p><strong>Key TensorFlow Applications:</strong></p>
                        <ul>
                            ${data.tensorflow_insights.key_tensorflow_applications.map(app => `<li>${app}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Research Domains:</strong></p>
                        <ul>
                            ${data.tensorflow_insights.tensorflow_research_domains.map(domain => `<li>${domain}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    // Update the results container
    resultContent.innerHTML = html;
    
    // If we have trend data, visualize it
    if (data.trend_analysis && data.trend_analysis.trend_data && data.trend_analysis.trend_data.length > 0) {
        createTrendChart(data.trend_analysis.trend_data, visualizationContainer);
    }
}

/**
 * Identify research gaps in the project
 */
function identifyResearchGaps() {
    // Show loading in the results area
    const resultsContainer = document.getElementById('analysisResults');
    resultsContainer.classList.remove('d-none');
    resultsContainer.innerHTML = `
        <div class="text-center my-4">
            <div class="loading-spinner"></div>
            <p class="mt-2">Identifying research gaps...</p>
        </div>
    `;
    
    fetch(`/api/projects/${projectId}/gaps`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error identifying gaps');
        }
        return response.json();
    })
    .then(data => {
        // Display research gaps
        displayResearchGaps(data);
    })
    .catch(error => {
        console.error('Error identifying research gaps:', error);
        resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <p class="mb-0">Error identifying research gaps. Please try again.</p>
            </div>
        `;
    });
}

/**
 * Display research gaps
 */
function displayResearchGaps(data) {
    const resultsContainer = document.getElementById('analysisResults');
    const resultContent = document.getElementById('resultContent');
    
    // Create results HTML
    let html = `<div class="alert alert-info mb-4">
        <p class="mb-0">Research gaps identified with ${Math.round(data.gap_confidence * 100)}% confidence</p>
    </div>`;
    
    html += `<div class="card bg-dark mb-4">
        <div class="card-header">
            <h6 class="mb-0">Potential Research Gaps</h6>
        </div>
        <div class="card-body">
            <ul class="list-group list-group-flush">
                ${data.research_gaps.map(gap => `
                    <li class="list-group-item bg-dark">${gap}</li>
                `).join('')}
            </ul>
        </div>
    </div>`;
    
    // Add emerging and declining topics
    if (data.emerging_topics && data.emerging_topics.length > 0) {
        html += `<div class="card bg-dark mb-4">
            <div class="card-header">
                <h6 class="mb-0">Topic Trends</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Emerging Topics:</strong></p>
                        <ul class="list-group list-group-flush">
                            ${data.emerging_topics.map(topic => `
                                <li class="list-group-item bg-dark text-success">
                                    <i class="bi bi-arrow-up-right"></i> ${topic}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Declining Topics:</strong></p>
                        <ul class="list-group list-group-flush">
                            ${data.declining_topics.map(topic => `
                                <li class="list-group-item bg-dark text-warning">
                                    <i class="bi bi-arrow-down-right"></i> ${topic}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    // Update the results container
    resultContent.innerHTML = html;
}