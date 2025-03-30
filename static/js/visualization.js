// Visualization for TensorFlow analysis in AURA Research Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Check if visualization container exists
    const visualizationContainer = document.getElementById('tensorflowVisualization');
    if (visualizationContainer) {
        // Initialize empty visualization
        createEmptyVisualization(visualizationContainer);
    }
    
    // Set up TensorFlow analysis button
    const analyzeButton = document.getElementById('analyzeWithTensorFlowBtn');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project-id');
            const analysisType = document.getElementById('analysisType').value;
            
            // Disable button during analysis
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
            
            // Perform TensorFlow analysis
            performTensorFlowAnalysis(projectId, analysisType);
        });
    }
});

// Create empty visualization container
function createEmptyVisualization(container) {
    container.innerHTML = `
        <div class="tensorflow-section mb-4">
            <span class="tensorflow-badge">TensorFlow</span>
            <h4>Research Paper Analysis</h4>
            <p>Select an analysis type and click "Analyze with TensorFlow" to begin.</p>
            <div class="row mb-3">
                <div class="col-md-6">
                    <select id="analysisType" class="form-select">
                        <option value="all">Complete Analysis</option>
                        <option value="embeddings">Paper Embeddings</option>
                        <option value="trends">Research Trends</option>
                        <option value="impact">Citation Impact Prediction</option>
                        <option value="similarities">Paper Similarities</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <button id="analyzeWithTensorFlowBtn" class="btn btn-info" data-project-id="${container.getAttribute('data-project-id')}">
                        Analyze with TensorFlow
                    </button>
                </div>
            </div>
            <div id="analysisResults" class="mt-4">
                <div class="alert alert-secondary">
                    No analysis has been performed yet. Select an analysis type and click "Analyze with TensorFlow".
                </div>
            </div>
        </div>
    `;
}

// Perform TensorFlow analysis
function performTensorFlowAnalysis(projectId, analysisType) {
    const analysisResults = document.getElementById('analysisResults');
    
    // Show loading state
    analysisResults.innerHTML = `
        <div class="text-center my-5">
            <span class="loader"></span>
            <p class="mt-3">Performing TensorFlow analysis...</p>
        </div>
    `;
    
    // Make API request
    fetch(`/api/projects/${projectId}/tf-analysis`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ analysis_type: analysisType })
    })
    .then(response => response.json())
    .then(data => {
        // Update visualization with results
        updateTensorFlowAnalysis(data);
        
        // Re-enable button
        const analyzeButton = document.getElementById('analyzeWithTensorFlowBtn');
        if (analyzeButton) {
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = 'Analyze with TensorFlow';
        }
    })
    .catch(error => {
        console.error('Error performing TensorFlow analysis:', error);
        
        // Show error
        analysisResults.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> Failed to perform TensorFlow analysis. Please try again.
            </div>
        `;
        
        // Re-enable button
        const analyzeButton = document.getElementById('analyzeWithTensorFlowBtn');
        if (analyzeButton) {
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = 'Analyze with TensorFlow';
        }
    });
}

// Update visualization with TensorFlow analysis results
function updateTensorFlowAnalysis(data) {
    const analysisResults = document.getElementById('analysisResults');
    
    // Check if we have results
    if (data.error) {
        analysisResults.innerHTML = `
            <div class="alert alert-danger">
                <strong>Error:</strong> ${data.error}
            </div>
        `;
        return;
    }
    
    // Build results HTML
    let resultsHTML = '';
    
    // Add summary if available
    if (data.summary) {
        resultsHTML += `
            <div class="alert alert-info">
                ${data.summary.message}
            </div>
        `;
    }
    
    // Add embeddings results if available
    if (data.embeddings && !data.embeddings.error) {
        resultsHTML += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">Paper Embeddings</h5>
                </div>
                <div class="card-body">
                    <p>${data.embeddings.message}</p>
                    <div class="alert alert-success">
                        Successfully created high-dimensional embeddings for ${data.embeddings.paper_count} papers 
                        using TensorFlow Universal Sentence Encoder.
                    </div>
                </div>
            </div>
        `;
    }
    
    // Add trends results if available
    if (data.trends && !data.trends.error) {
        resultsHTML += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">Research Trends</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Time Distribution</h6>
                            <div id="yearDistributionChart" class="visualization-container"></div>
                        </div>
                        <div class="col-md-6">
                            <h6>Topic Distribution</h6>
                            <div id="topicDistributionChart" class="visualization-container"></div>
                        </div>
                    </div>
                    <div class="alert alert-success mt-3">
                        Analyzed trends across ${data.trends.total_papers} papers 
                        (${data.trends.papers_with_dates} with publication dates).
                    </div>
                </div>
            </div>
        `;
        
        // Initialize charts when DOM is ready
        setTimeout(() => {
            createYearDistributionChart(data.trends.year_distribution);
            createTopicDistributionChart(data.trends.topic_distribution);
        }, 100);
    }
    
    // Add impact prediction results if available
    if (data.impact && !data.impact.error) {
        resultsHTML += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">Citation Impact Prediction</h5>
                </div>
                <div class="card-body">
                    <p>${data.impact.message}</p>
                    <h6>Top Papers by Predicted Impact</h6>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Paper Title</th>
                                    <th>Predicted Impact</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.impact.top_papers.map(paper => `
                                    <tr>
                                        <td>${paper.title}</td>
                                        <td>
                                            <div class="progress">
                                                <div class="progress-bar bg-info" role="progressbar" 
                                                    style="width: ${Math.min(100, paper.predicted_impact * 5)}%;" 
                                                    aria-valuenow="${paper.predicted_impact}" 
                                                    aria-valuemin="0" aria-valuemax="20">
                                                    ${paper.predicted_impact.toFixed(1)}
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Add similarities results if available
    if (data.similarities && !data.similarities.error) {
        resultsHTML += `
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">Paper Similarities</h5>
                </div>
                <div class="card-body">
                    <p>${data.similarities.message}</p>
                    <div class="row">
                        ${Object.entries(data.similarities.clusters).map(([clusterId, papers]) => `
                            <div class="col-md-6 mb-4">
                                <div class="card">
                                    <div class="card-header">
                                        <h6 class="mb-0">Cluster ${parseInt(clusterId) + 1}</h6>
                                        <small>Common terms: ${
                                            data.similarities.cluster_terms && 
                                            data.similarities.cluster_terms[clusterId] ? 
                                            data.similarities.cluster_terms[clusterId].join(', ') : 
                                            'None identified'
                                        }</small>
                                    </div>
                                    <ul class="list-group list-group-flush">
                                        ${papers.map(paper => `
                                            <li class="list-group-item">${paper.title}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Update analysis results container
    analysisResults.innerHTML = resultsHTML;
}

// Create year distribution chart
function createYearDistributionChart(yearData) {
    const chartContainer = document.getElementById('yearDistributionChart');
    if (!chartContainer || !yearData) return;
    
    // Prepare data
    const years = Object.keys(yearData).sort();
    const counts = years.map(year => yearData[year]);
    
    // Create chart
    const ctx = document.createElement('canvas');
    ctx.height = 250;
    chartContainer.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [{
                label: 'Papers per Year',
                data: counts,
                backgroundColor: 'rgba(13, 202, 240, 0.6)',
                borderColor: 'rgba(13, 202, 240, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Create topic distribution chart
function createTopicDistributionChart(topicData) {
    const chartContainer = document.getElementById('topicDistributionChart');
    if (!chartContainer || !topicData) return;
    
    // Prepare data
    const topics = Object.keys(topicData);
    const counts = topics.map(topic => topicData[topic]);
    
    // Create chart
    const ctx = document.createElement('canvas');
    ctx.height = 250;
    chartContainer.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: topics,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(13, 202, 240, 0.6)',
                    'rgba(13, 110, 253, 0.6)',
                    'rgba(102, 16, 242, 0.6)',
                    'rgba(214, 51, 132, 0.6)',
                    'rgba(253, 126, 20, 0.6)',
                    'rgba(255, 193, 7, 0.6)',
                    'rgba(25, 135, 84, 0.6)',
                    'rgba(220, 53, 69, 0.6)',
                    'rgba(108, 117, 125, 0.6)',
                    'rgba(32, 201, 151, 0.6)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 10
                    }
                }
            }
        }
    });
}