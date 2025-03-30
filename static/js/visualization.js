/**
 * Visualization functions for AURA Research Assistant
 */

/**
 * Create a trend chart showing research paper publication trends
 * 
 * @param {Array} trendData - Array of objects with year and count properties
 * @param {HTMLElement} container - Container element for the chart
 */
function createTrendChart(trendData, container) {
    // Clear existing chart
    container.innerHTML = '';
    
    if (!trendData || trendData.length === 0) {
        container.innerHTML = '<div class="alert alert-secondary">No trend data available</div>';
        return;
    }
    
    // Create canvas for Chart.js
    const canvas = document.createElement('canvas');
    canvas.id = 'trendChart';
    container.appendChild(canvas);
    
    // Prepare data for Chart.js
    const years = trendData.map(item => item.year);
    const counts = trendData.map(item => item.count);
    
    // Create chart
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Papers Published',
                data: counts,
                borderColor: '#5bc0de',
                backgroundColor: 'rgba(91, 192, 222, 0.2)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Research Publication Trends'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Papers'
                    }
                }
            }
        }
    });
}

/**
 * Create a cluster visualization
 * 
 * @param {Array} clusters - Cluster data
 * @param {HTMLElement} container - Container element for the visualization
 */
function createClusterVisualization(clusters, container) {
    // This is a placeholder for a more advanced visualization
    // In a real implementation, this would use TensorFlow.js or D3.js
    
    // Clear existing content
    container.innerHTML = '';
    
    if (!clusters || clusters.length === 0) {
        container.innerHTML = '<div class="alert alert-secondary">No cluster data available</div>';
        return;
    }
    
    // Create a simple visual representation
    const visualContainer = document.createElement('div');
    visualContainer.className = 'cluster-visualization';
    visualContainer.style.display = 'flex';
    visualContainer.style.justifyContent = 'center';
    visualContainer.style.flexWrap = 'wrap';
    visualContainer.style.gap = '20px';
    visualContainer.style.marginTop = '20px';
    
    // Create cluster nodes
    clusters.forEach((cluster, index) => {
        const clusterNode = document.createElement('div');
        clusterNode.className = 'cluster-node';
        clusterNode.style.width = '180px';
        clusterNode.style.height = '180px';
        clusterNode.style.borderRadius = '50%';
        clusterNode.style.backgroundColor = `rgba(91, 192, 222, ${0.3 + (index * 0.2)})`;
        clusterNode.style.display = 'flex';
        clusterNode.style.flexDirection = 'column';
        clusterNode.style.justifyContent = 'center';
        clusterNode.style.alignItems = 'center';
        clusterNode.style.padding = '10px';
        clusterNode.style.textAlign = 'center';
        clusterNode.style.boxShadow = '0 0 15px rgba(0, 0, 0, 0.2)';
        
        const title = document.createElement('div');
        title.className = 'fw-bold mb-1';
        title.textContent = `Cluster ${index + 1}`;
        
        const paperCount = document.createElement('div');
        paperCount.className = 'small';
        paperCount.textContent = `${cluster.paper_count} papers`;
        
        const keywordsEl = document.createElement('div');
        keywordsEl.className = 'mt-2 very-small text-center';
        keywordsEl.textContent = cluster.keywords?.slice(0, 3).join(', ') || 'No keywords';
        
        clusterNode.appendChild(title);
        clusterNode.appendChild(paperCount);
        clusterNode.appendChild(keywordsEl);
        
        // Add hover effect
        clusterNode.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.2s';
            this.style.cursor = 'pointer';
        });
        
        clusterNode.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        visualContainer.appendChild(clusterNode);
    });
    
    container.appendChild(visualContainer);
}

/**
 * Create a similarity network visualization
 * 
 * @param {Array} similarPairs - Similar paper pairs
 * @param {HTMLElement} container - Container element for the visualization
 */
function createSimilarityNetwork(similarPairs, container) {
    // Placeholder for a more advanced network visualization
    // In a real implementation, this would use a network visualization library
    
    // Clear existing content
    container.innerHTML = '';
    
    if (!similarPairs || similarPairs.length === 0) {
        container.innerHTML = '<div class="alert alert-secondary">No similarity data available</div>';
        return;
    }
    
    // Display the similarity data in a table format
    const table = document.createElement('table');
    table.className = 'table table-dark table-hover';
    
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Paper 1</th>
            <th>Paper 2</th>
            <th>Similarity</th>
        </tr>
    `;
    
    const tbody = document.createElement('tbody');
    similarPairs.forEach(pair => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${pair.paper1}</td>
            <td>${pair.paper2}</td>
            <td>${Math.round(pair.similarity_score * 100)}%</td>
        `;
        tbody.appendChild(row);
    });
    
    table.appendChild(thead);
    table.appendChild(tbody);
    container.appendChild(table);
}