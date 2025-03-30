/**
 * Main JavaScript functionality for AURA Research Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle flash messages autohide
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert-dismissible');
        flashMessages.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Handle TensorFlow analysis form submission
    const tfAnalysisForm = document.getElementById('tensorflowAnalysisForm');
    if (tfAnalysisForm) {
        tfAnalysisForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const analysisType = document.getElementById('analysisType').value;
            const paperIds = Array.from(
                document.querySelectorAll('#paperSelection input[type="checkbox"]:checked')
            ).map(cb => cb.value);
            
            if (!analysisType) {
                alert('Please select an analysis type');
                return;
            }
            
            // Show loading indicator
            document.getElementById('analysisResults').innerHTML = '<div class="text-center my-5"><div class="spinner-border text-info" role="status"></div><p class="mt-2">Processing analysis with TensorFlow...</p></div>';
            
            // Submit analysis request
            fetch(`/api/projects/${projectId}/tensorflow/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    analysis_type: analysisType,
                    paper_ids: paperIds
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Analysis request failed');
                }
                return response.json();
            })
            .then(data => {
                displayAnalysisResults(data);
            })
            .catch(error => {
                console.error('Error performing analysis:', error);
                document.getElementById('analysisResults').innerHTML = `
                    <div class="alert alert-danger">
                        <h4 class="alert-heading">Analysis Failed</h4>
                        <p>There was an error performing the analysis. Please try again.</p>
                    </div>
                `;
            });
        });
    }
});

/**
 * Display TensorFlow analysis results
 * 
 * @param {Object} results - Analysis results from the server
 */
function displayAnalysisResults(results) {
    const resultsContainer = document.getElementById('analysisResults');
    
    if (!results || results.error) {
        resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <h4 class="alert-heading">Analysis Failed</h4>
                <p>${results.error || 'An unknown error occurred'}</p>
            </div>
        `;
        return;
    }
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // Create results card
    const card = document.createElement('div');
    card.className = 'card tensorflow-card';
    
    // Create card header
    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';
    cardHeader.innerHTML = `<h5 class="mb-0">TensorFlow Analysis Results: ${results.analysis_type}</h5>`;
    card.appendChild(cardHeader);
    
    // Create card body
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    
    // Add appropriate visualization based on analysis type
    switch (results.analysis_type) {
        case 'clustering':
            cardBody.innerHTML = '<div id="clusterVisualization" class="visualization-container"></div>';
            card.appendChild(cardBody);
            resultsContainer.appendChild(card);
            createClusterVisualization(results.clusters, document.getElementById('clusterVisualization'));
            break;
            
        case 'topic_modeling':
            let topicsHTML = '<div class="row">';
            results.topics.forEach((topic, index) => {
                topicsHTML += `
                    <div class="col-md-4 mb-3">
                        <div class="card h-100">
                            <div class="card-header">
                                <h6 class="mb-0">Topic ${index + 1}</h6>
                            </div>
                            <div class="card-body">
                                <p class="card-text small">${topic.keywords.join(', ')}</p>
                                <div class="progress mt-2">
                                    <div class="progress-bar bg-info" role="progressbar" style="width: ${topic.weight * 100}%" 
                                        aria-valuenow="${topic.weight * 100}" aria-valuemin="0" aria-valuemax="100">
                                        ${Math.round(topic.weight * 100)}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            topicsHTML += '</div>';
            cardBody.innerHTML = topicsHTML;
            card.appendChild(cardBody);
            resultsContainer.appendChild(card);
            break;
            
        case 'similarity':
            cardBody.innerHTML = '<div id="similarityVisualization" class="visualization-container"></div>';
            card.appendChild(cardBody);
            resultsContainer.appendChild(card);
            createSimilarityNetwork(results.similar_pairs, document.getElementById('similarityVisualization'));
            break;
            
        case 'trend_analysis':
            cardBody.innerHTML = '<div id="trendChart" class="visualization-container"></div>';
            card.appendChild(cardBody);
            resultsContainer.appendChild(card);
            createTrendChart(results.trends, document.getElementById('trendChart'));
            break;
            
        default:
            cardBody.innerHTML = `<pre class="bg-dark p-3 rounded">${JSON.stringify(results, null, 2)}</pre>`;
            card.appendChild(cardBody);
            resultsContainer.appendChild(card);
    }
}