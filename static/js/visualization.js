/**
 * Visualization functions for AURA Research Assistant
 * Uses Chart.js for data visualization
 */

/**
 * Render visualizations based on TensorFlow analysis data
 */
function renderVisualization(visualizationData) {
    if (!visualizationData) {
        console.error('No visualization data provided');
        return;
    }
    
    // Get visualization container
    const container = document.getElementById('visualizationContainer') || document.getElementById('tfAnalysisResults');
    if (!container) {
        console.error('Visualization container not found');
        return;
    }
    
    // Clear container
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    
    // Add visualization title
    const title = document.createElement('h4');
    title.className = 'mb-4';
    title.textContent = 'TensorFlow Analysis Visualizations';
    container.appendChild(title);
    
    // Create row for visualizations
    const row = document.createElement('div');
    row.className = 'row';
    container.appendChild(row);
    
    // Topic visualization
    if (visualizationData.topics) {
        createTopicVisualization(visualizationData.topics, row);
    }
    
    // Cluster visualization
    if (visualizationData.clusters) {
        createClusterVisualization(visualizationData.clusters, row);
    }
    
    // Trend visualization
    if (visualizationData.trends) {
        createTrendVisualization(visualizationData.trends, row);
    }
}

/**
 * Create topic visualization
 */
function createTopicVisualization(topicData, container) {
    // Create column
    const col = document.createElement('div');
    col.className = 'col-md-6 mb-4';
    container.appendChild(col);
    
    // Create card
    const card = document.createElement('div');
    card.className = 'card h-100';
    col.appendChild(card);
    
    // Create card header
    const header = document.createElement('div');
    header.className = 'card-header bg-info text-white';
    header.innerHTML = '<h5 class="mb-0">Topic Distribution</h5>';
    card.appendChild(header);
    
    // Create card body
    const body = document.createElement('div');
    body.className = 'card-body';
    card.appendChild(body);
    
    // Create canvas for chart
    const canvas = document.createElement('canvas');
    canvas.id = 'topicChart';
    body.appendChild(canvas);
    
    // Extract data for chart
    const labels = topicData.map(topic => `Topic ${topic.id}`);
    const data = topicData.map(topic => topic.weight);
    const backgroundColors = generateColors(topicData.length);
    
    // Create chart
    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const topic = topicData[context.dataIndex];
                            return `${context.label}: ${context.parsed.toFixed(2)}% - ${topic.keywords.join(', ')}`;
                        }
                    }
                }
            }
        }
    });
    
    // Add topic keywords
    const keywords = document.createElement('div');
    keywords.className = 'mt-3';
    keywords.innerHTML = '<h6>Key Topics:</h6><ul class="list-group list-group-flush">';
    
    topicData.forEach(topic => {
        keywords.innerHTML += `
            <li class="list-group-item bg-transparent">
                <strong>Topic ${topic.id}:</strong> ${topic.keywords.join(', ')}
            </li>
        `;
    });
    
    keywords.innerHTML += '</ul>';
    body.appendChild(keywords);
}

/**
 * Create cluster visualization
 */
function createClusterVisualization(clusterData, container) {
    // Create column
    const col = document.createElement('div');
    col.className = 'col-md-6 mb-4';
    container.appendChild(col);
    
    // Create card
    const card = document.createElement('div');
    card.className = 'card h-100';
    col.appendChild(card);
    
    // Create card header
    const header = document.createElement('div');
    header.className = 'card-header bg-info text-white';
    header.innerHTML = '<h5 class="mb-0">Paper Clusters</h5>';
    card.appendChild(header);
    
    // Create card body
    const body = document.createElement('div');
    body.className = 'card-body';
    card.appendChild(body);
    
    // Create canvas for chart
    const canvas = document.createElement('canvas');
    canvas.id = 'clusterChart';
    body.appendChild(canvas);
    
    // Extract data for chart
    const datasets = [];
    const backgroundColors = generateColors(clusterData.length);
    
    clusterData.forEach((cluster, index) => {
        const data = cluster.papers.map(paper => ({
            x: paper.x,
            y: paper.y,
            r: 10, // bubble size
            paper_id: paper.paper_id,
            title: paper.title
        }));
        
        datasets.push({
            label: `Cluster ${index + 1}`,
            data: data,
            backgroundColor: backgroundColors[index],
            borderWidth: 1
        });
    });
    
    // Create chart
    new Chart(canvas, {
        type: 'bubble',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.raw.title;
                        }
                    }
                }
            }
        }
    });
    
    // Add cluster descriptions
    const descriptions = document.createElement('div');
    descriptions.className = 'mt-3';
    descriptions.innerHTML = '<h6>Cluster Information:</h6><ul class="list-group list-group-flush">';
    
    clusterData.forEach((cluster, index) => {
        descriptions.innerHTML += `
            <li class="list-group-item bg-transparent">
                <strong>Cluster ${index + 1}:</strong> ${cluster.description || `Contains ${cluster.papers.length} papers`}
            </li>
        `;
    });
    
    descriptions.innerHTML += '</ul>';
    body.appendChild(descriptions);
}

/**
 * Create trend visualization
 */
function createTrendVisualization(trendData, container) {
    // Create column
    const col = document.createElement('div');
    col.className = 'col-md-12 mb-4';
    container.appendChild(col);
    
    // Create card
    const card = document.createElement('div');
    card.className = 'card h-100';
    col.appendChild(card);
    
    // Create card header
    const header = document.createElement('div');
    header.className = 'card-header bg-info text-white';
    header.innerHTML = '<h5 class="mb-0">Research Trends Over Time</h5>';
    card.appendChild(header);
    
    // Create card body
    const body = document.createElement('div');
    body.className = 'card-body';
    card.appendChild(body);
    
    // Create canvas for chart
    const canvas = document.createElement('canvas');
    canvas.id = 'trendChart';
    body.appendChild(canvas);
    
    // Extract data for chart
    const labels = trendData.labels;
    const datasets = trendData.trends.map((trend, index) => {
        return {
            label: trend.name,
            data: trend.values,
            borderColor: generateColors(1)[0],
            backgroundColor: 'transparent',
            tension: 0.4
        };
    });
    
    // Create chart
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time Period'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Add trend insights
    if (trendData.insights && trendData.insights.length > 0) {
        const insights = document.createElement('div');
        insights.className = 'mt-3';
        insights.innerHTML = '<h6>Trend Insights:</h6><ul>';
        
        trendData.insights.forEach(insight => {
            insights.innerHTML += `<li>${insight}</li>`;
        });
        
        insights.innerHTML += '</ul>';
        body.appendChild(insights);
    }
}

/**
 * Generate colors for visualizations
 */
function generateColors(count) {
    const colors = [
        'rgba(54, 162, 235, 0.7)',   // blue
        'rgba(255, 99, 132, 0.7)',   // red
        'rgba(75, 192, 192, 0.7)',   // green
        'rgba(255, 159, 64, 0.7)',   // orange
        'rgba(153, 102, 255, 0.7)',  // purple
        'rgba(255, 205, 86, 0.7)',   // yellow
        'rgba(201, 203, 207, 0.7)'   // grey
    ];
    
    // If more colors are needed than available, generate them
    if (count > colors.length) {
        for (let i = colors.length; i < count; i++) {
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
        }
    }
    
    return colors.slice(0, count);
}