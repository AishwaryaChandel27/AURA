/**
 * Visualization JavaScript for AURA Research Assistant
 */

// Scope visualization functions globally to make them accessible from templates
window.renderVisualization = function(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Visualization container not found:', containerId);
        return;
    }
    
    // Clear container
    container.innerHTML = '';
    
    // Check if data is available
    if (!data || !data.papers || data.papers.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><p class="text-muted">No data available for visualization</p></div>';
        return;
    }
    
    // Create tabbed interface for different visualizations
    const tabsHtml = `
        <ul class="nav nav-tabs mb-3" id="vizTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="network-tab" data-bs-toggle="tab" data-bs-target="#network-viz" type="button" role="tab">Network</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="trends-tab" data-bs-toggle="tab" data-bs-target="#trends-viz" type="button" role="tab">Trends</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="topics-tab" data-bs-toggle="tab" data-bs-target="#topics-viz" type="button" role="tab">Topics</button>
            </li>
        </ul>
        <div class="tab-content" id="vizTabContent">
            <div class="tab-pane fade show active" id="network-viz" role="tabpanel">
                <canvas id="network-chart" height="350"></canvas>
            </div>
            <div class="tab-pane fade" id="trends-viz" role="tabpanel">
                <canvas id="trend-chart" height="350"></canvas>
            </div>
            <div class="tab-pane fade" id="topics-viz" role="tabpanel">
                <canvas id="topic-chart" height="350"></canvas>
            </div>
        </div>
    `;
    container.innerHTML = tabsHtml;
    
    // Render network visualization
    renderNetworkGraph('network-chart', data);
    
    // Render trends visualization
    renderTrendChart('trend-chart', data);
    
    // Render topics visualization
    renderTopicChart('topic-chart', data);
};

function renderNetworkGraph(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Check if we have network data
    if (!data.network || !data.network.nodes || data.network.nodes.length === 0) {
        canvas.style.display = 'none';
        canvas.parentNode.innerHTML = '<div class="text-center py-5"><p class="text-muted">No network data available</p></div>';
        return;
    }
    
    // Prepare data for network graph
    const nodes = data.network.nodes.map(node => ({
        x: node.x * canvas.width,
        y: node.y * canvas.height,
        r: 10,
        label: node.label,
        cluster: node.cluster || 0
    }));
    
    const links = (data.network.links || []).map(link => {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);
        return { source, target, value: link.value || 1 };
    }).filter(link => link.source && link.target);
    
    // Create a scatter plot to represent the network
    const clusterColors = [
        'rgba(54, 162, 235, 0.8)',  // blue
        'rgba(255, 99, 132, 0.8)',  // red
        'rgba(75, 192, 192, 0.8)',  // green
        'rgba(255, 159, 64, 0.8)',  // orange
        'rgba(153, 102, 255, 0.8)', // purple
        'rgba(255, 205, 86, 0.8)'   // yellow
    ];
    
    const datasets = [];
    
    // Group nodes by cluster
    const clusterMap = nodes.reduce((acc, node) => {
        const cluster = node.cluster || 0;
        if (!acc[cluster]) acc[cluster] = [];
        acc[cluster].push(node);
        return acc;
    }, {});
    
    // Create a dataset for each cluster
    Object.keys(clusterMap).forEach((clusterId, index) => {
        const clusterNodes = clusterMap[clusterId];
        datasets.push({
            label: `Cluster ${clusterId}`,
            data: clusterNodes.map(node => ({
                x: node.x,
                y: node.y,
                r: node.r,
                node_id: node.id,
                label: node.label
            })),
            backgroundColor: clusterColors[index % clusterColors.length],
            borderColor: 'rgba(255, 255, 255, 0.5)',
            borderWidth: 1
        });
    });
    
    // Create the chart
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: false,
                    min: 0,
                    max: canvas.width
                },
                y: {
                    display: false,
                    min: 0,
                    max: canvas.height
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const data = context.raw;
                            return data.label || 'Paper';
                        }
                    }
                }
            }
        }
    });
}

function renderTrendChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Check if we have trend data
    if (!data.trends || !data.trends.publications || data.trends.publications.length === 0) {
        canvas.style.display = 'none';
        canvas.parentNode.innerHTML = '<div class="text-center py-5"><p class="text-muted">No trend data available</p></div>';
        return;
    }
    
    // Sort publications by year
    const publications = [...data.trends.publications].sort((a, b) => a.year - b.year);
    
    // Prepare data for trend chart
    const labels = publications.map(pub => pub.year.toString());
    
    const datasets = [
        {
            label: 'Publications',
            data: publications.map(pub => pub.count),
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 2,
            fill: true
        }
    ];
    
    // Add topic trends if available
    if (data.trends.topics && data.trends.topics.length > 0) {
        data.trends.topics.forEach((topic, index) => {
            const colors = [
                'rgba(255, 99, 132, 1)',  // red
                'rgba(75, 192, 192, 1)',  // green
                'rgba(255, 159, 64, 1)',  // orange
                'rgba(153, 102, 255, 1)', // purple
                'rgba(255, 205, 86, 1)'   // yellow
            ];
            
            // Find the topic data points that match our years
            const topicData = {};
            topic.data.forEach(d => {
                topicData[d.year] = d.score;
            });
            
            // Map to our labels, with null for missing years
            const dataPoints = labels.map(year => topicData[parseInt(year)] || null);
            
            datasets.push({
                label: topic.topic,
                data: dataPoints,
                borderColor: colors[index % colors.length],
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                yAxisID: 'y1'
            });
        });
    }
    
    // Create the chart
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
                        text: 'Publication Count'
                    }
                },
                y1: {
                    display: datasets.length > 1,
                    position: 'right',
                    beginAtZero: true,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Topic Relevance'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

function renderTopicChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Check if we have topic data
    if (!data.topics || data.topics.length === 0) {
        canvas.style.display = 'none';
        canvas.parentNode.innerHTML = '<div class="text-center py-5"><p class="text-muted">No topic data available</p></div>';
        return;
    }
    
    // Prepare data for topic chart
    const topicLabels = data.topics.map(topic => topic.description || `Topic ${topic.id}`);
    const topicData = data.topics.map(topic => topic.papers ? topic.papers.length : 0);
    
    // Create chart colors
    const backgroundColors = [
        'rgba(54, 162, 235, 0.8)',  // blue
        'rgba(255, 99, 132, 0.8)',  // red
        'rgba(75, 192, 192, 0.8)',  // green
        'rgba(255, 159, 64, 0.8)',  // orange
        'rgba(153, 102, 255, 0.8)', // purple
        'rgba(255, 205, 86, 0.8)'   // yellow
    ];
    
    // Create the chart
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: topicLabels,
            datasets: [{
                label: 'Papers per Topic',
                data: topicData,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}`;
                        }
                    }
                }
            }
        }
    });
}