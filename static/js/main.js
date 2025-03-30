/**
 * AURA Research Assistant - Main JavaScript
 * 
 * Handles client-side functionality for the AURA Research Assistant.
 */

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Common DOM elements
    const searchForm = document.getElementById('searchForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const paperResults = document.getElementById('paperResults');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analysisContainer = document.getElementById('analysisContainer');
    const generateHypothesisBtn = document.getElementById('generateHypothesisBtn');
    const hypothesisContainer = document.getElementById('hypothesisContainer');
    const designExperimentBtn = document.getElementById('designExperimentBtn');
    const experimentContainer = document.getElementById('experimentContainer');
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    
    // Store selected papers for analysis
    let selectedPapers = [];
    let currentHypothesis = '';
    
    // Initialize event listeners
    initEventListeners();
    
    /**
     * Initialize all event listeners
     */
    function initEventListeners() {
        // Search form submission
        if (searchForm) {
            searchForm.addEventListener('submit', handleSearchSubmit);
        }
        
        // Analyze button click
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', handleAnalyzeClick);
        }
        
        // Generate hypothesis button click
        if (generateHypothesisBtn) {
            generateHypothesisBtn.addEventListener('click', handleGenerateHypothesis);
        }
        
        // Design experiment button click
        if (designExperimentBtn) {
            designExperimentBtn.addEventListener('click', handleDesignExperiment);
        }
        
        // Chat form submission
        if (chatForm) {
            chatForm.addEventListener('submit', handleChatSubmit);
        }
    }
    
    /**
     * Handle search form submission
     */
    function handleSearchSubmit(e) {
        e.preventDefault();
        
        // Get form data
        const query = document.getElementById('searchQuery').value;
        const sourceArxiv = document.getElementById('sourceArxiv').checked;
        const sourceSemanticScholar = document.getElementById('sourceSemanticScholar').checked;
        
        // Validate
        if (!query) {
            showError('Please enter a search query');
            return;
        }
        
        // Build sources array
        const sources = [];
        if (sourceArxiv) sources.push('arxiv');
        if (sourceSemanticScholar) sources.push('semantic_scholar');
        
        if (sources.length === 0) {
            showError('Please select at least one source');
            return;
        }
        
        // Show loading state
        paperResults.innerHTML = `
            <div class="col-12 text-center text-white">
                <div class="spinner-border text-info" role="status"></div>
                <p class="mt-2">Searching for papers...</p>
            </div>
        `;
        resultsContainer.classList.remove('d-none');
        
        // For demo purposes, generate mock papers
        // In a production environment, this would be an API call
        setTimeout(() => {
            displaySamplePapers(query);
        }, 1500);
        
        // In production, this would be an actual API call:
        /*
        fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                sources: sources,
                max_results: 10
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            displayPapers(data.papers);
        })
        .catch(error => {
            showError('Error searching papers: ' + error.message);
        });
        */
    }
    
    /**
     * Handle analyze button click
     */
    function handleAnalyzeClick() {
        // Show loading state
        analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        analyzeBtn.disabled = true;
        
        // For demo, use mock analysis
        setTimeout(() => {
            analysisContainer.classList.remove('d-none');
            displaySampleAnalysis();
            
            // Reset button
            analyzeBtn.innerHTML = 'Analyze with TensorFlow';
            analyzeBtn.disabled = false;
            
            // Scroll to section
            analysisContainer.scrollIntoView({ behavior: 'smooth' });
        }, 2000);
        
        // In production, this would be an actual API call:
        /*
        fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                papers: selectedPapers
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                analyzeBtn.innerHTML = 'Analyze with TensorFlow';
                analyzeBtn.disabled = false;
                return;
            }
            
            displayAnalysisResults(data);
            analysisContainer.classList.remove('d-none');
            
            // Reset button
            analyzeBtn.innerHTML = 'Analyze with TensorFlow';
            analyzeBtn.disabled = false;
            
            // Scroll to section
            analysisContainer.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            showError('Error analyzing papers: ' + error.message);
            analyzeBtn.innerHTML = 'Analyze with TensorFlow';
            analyzeBtn.disabled = false;
        });
        */
    }
    
    /**
     * Handle generate hypothesis button click
     */
    function handleGenerateHypothesis() {
        // Get search query as the research question
        const researchQuestion = document.getElementById('searchQuery').value;
        
        if (!researchQuestion) {
            showError('Please enter a research question');
            return;
        }
        
        // Show loading state
        generateHypothesisBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
        generateHypothesisBtn.disabled = true;
        
        // For demo, use mock hypothesis
        setTimeout(() => {
            hypothesisContainer.classList.remove('d-none');
            displaySampleHypothesis(researchQuestion);
            
            // Reset button
            generateHypothesisBtn.innerHTML = 'Generate Hypothesis';
            generateHypothesisBtn.disabled = false;
            
            // Scroll to section
            hypothesisContainer.scrollIntoView({ behavior: 'smooth' });
        }, 2000);
        
        // In production, this would be an actual API call:
        /*
        fetch('/api/generate_hypothesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                research_question: researchQuestion,
                papers: selectedPapers
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                generateHypothesisBtn.innerHTML = 'Generate Hypothesis';
                generateHypothesisBtn.disabled = false;
                return;
            }
            
            displayHypothesis(data);
            hypothesisContainer.classList.remove('d-none');
            
            // Store current hypothesis
            currentHypothesis = data.hypothesis_text;
            
            // Reset button
            generateHypothesisBtn.innerHTML = 'Generate Hypothesis';
            generateHypothesisBtn.disabled = false;
            
            // Scroll to section
            hypothesisContainer.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            showError('Error generating hypothesis: ' + error.message);
            generateHypothesisBtn.innerHTML = 'Generate Hypothesis';
            generateHypothesisBtn.disabled = false;
        });
        */
    }
    
    /**
     * Handle design experiment button click
     */
    function handleDesignExperiment() {
        const hypothesisText = document.getElementById('hypothesisText').textContent;
        
        if (!hypothesisText) {
            showError('No hypothesis available. Please generate a hypothesis first.');
            return;
        }
        
        // Show loading state
        designExperimentBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Designing...';
        designExperimentBtn.disabled = true;
        
        // For demo, use mock experiment
        setTimeout(() => {
            experimentContainer.classList.remove('d-none');
            displaySampleExperiment();
            
            // Reset button
            designExperimentBtn.innerHTML = 'Design Experiment';
            designExperimentBtn.disabled = false;
            
            // Scroll to section
            experimentContainer.scrollIntoView({ behavior: 'smooth' });
        }, 2000);
        
        // In production, this would be an actual API call:
        /*
        fetch('/api/design_experiment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                hypothesis: hypothesisText,
                papers: selectedPapers
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                designExperimentBtn.innerHTML = 'Design Experiment';
                designExperimentBtn.disabled = false;
                return;
            }
            
            displayExperiment(data);
            experimentContainer.classList.remove('d-none');
            
            // Reset button
            designExperimentBtn.innerHTML = 'Design Experiment';
            designExperimentBtn.disabled = false;
            
            // Scroll to section
            experimentContainer.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            showError('Error designing experiment: ' + error.message);
            designExperimentBtn.innerHTML = 'Design Experiment';
            designExperimentBtn.disabled = false;
        });
        */
    }
    
    /**
     * Handle chat form submission
     */
    function handleChatSubmit(e) {
        e.preventDefault();
        
        // Get user message
        const userMessageInput = document.getElementById('userMessage');
        const userMessage = userMessageInput.value.trim();
        
        if (!userMessage) {
            return;
        }
        
        // Add user message to chat
        addChatMessage('You', userMessage, 'user-message');
        
        // Clear input
        userMessageInput.value = '';
        
        // For demo, generate a mock response
        setTimeout(() => {
            let responseText = '';
            
            // Smart response based on keywords
            if (userMessage.toLowerCase().includes('tensorflow') || 
                userMessage.toLowerCase().includes('deep learning') || 
                userMessage.toLowerCase().includes('neural')) {
                responseText = "TensorFlow is an open-source machine learning framework developed by Google. AURA uses TensorFlow for analyzing research papers, topic modeling, and generating insights from academic literature. It's particularly useful for tasks like clustering related papers, identifying research trends, and finding connections between different studies.";
            } else if (userMessage.toLowerCase().includes('paper') || 
                       userMessage.toLowerCase().includes('research') || 
                       userMessage.toLowerCase().includes('article')) {
                responseText = "I can help you find relevant papers from sources like arXiv and Semantic Scholar. Just type your research topic or question in the search form above, and I'll retrieve the most relevant papers for you to analyze.";
            } else if (userMessage.toLowerCase().includes('hypothesis')) {
                responseText = "After analyzing a set of papers, I can generate research hypotheses based on the findings. These hypotheses consider patterns, gaps, and potential discoveries in the existing research. Each hypothesis includes supporting reasoning and a confidence score.";
            } else if (userMessage.toLowerCase().includes('experiment')) {
                responseText = "Once a hypothesis is generated, I can design an experiment to test it. This includes methodology, variables to measure, controls, expected outcomes, and potential limitations. The experiment design is based on best practices from similar research in the field.";
            } else {
                responseText = "I'm your AI research assistant. I can help you search for papers, analyze them with TensorFlow, generate hypotheses, and design experiments. What specific aspect of your research would you like help with?";
            }
            
            addChatMessage('AURA Assistant', responseText, 'agent-message');
        }, 1000);
        
        // In production, this would be an actual API call:
        /*
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userMessage,
                project_id: getCurrentProjectId() // Function to get current project ID if available
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addChatMessage('System', `Error: ${data.error}`, 'system-message');
                return;
            }
            
            addChatMessage('AURA Assistant', data.response, 'agent-message');
        })
        .catch(error => {
            addChatMessage('System', `Error: ${error.message}`, 'system-message');
        });
        */
    }
    
    // ---- Helper Functions ----
    
    /**
     * Display sample papers (for demo purposes)
     */
    function displaySamplePapers(query) {
        // Generate sample papers based on query
        const papers = [
            {
                title: `Advanced ${query.split(' ')[0]} Research with TensorFlow`,
                authors: "Zhang et al.",
                abstract: `This paper presents a comprehensive study of ${query} using deep learning approaches with TensorFlow. We demonstrate state-of-the-art results on benchmark datasets.`,
                year: "2024",
                source: "arxiv",
                url: "#",
                id: "sample1"
            },
            {
                title: `A Survey of ${query} Methods`,
                authors: "Johnson, Smith & Wong",
                abstract: `We review recent advances in ${query} and categorize current approaches based on their methodologies and performance characteristics.`,
                year: "2023",
                source: "semantic_scholar",
                url: "#",
                id: "sample2"
            },
            {
                title: `Efficient Models for ${query}: A TensorFlow Approach`,
                authors: "Garcia & Kim",
                abstract: `This work introduces optimized TensorFlow implementations for ${query} tasks that reduce computational requirements while maintaining accuracy.`,
                year: "2023",
                source: "arxiv",
                url: "#",
                id: "sample3"
            },
            {
                title: `${query} Analysis with Neural Networks`,
                authors: "Patel et al.",
                abstract: `We propose a novel neural architecture for analyzing ${query} that outperforms conventional methods on multiple evaluation metrics.`,
                year: "2022",
                source: "semantic_scholar",
                url: "#",
                id: "sample4"
            }
        ];
        
        // Store papers for later use
        selectedPapers = papers;
        
        // Display papers
        let html = '';
        papers.forEach(paper => {
            html += `
            <div class="col-md-6 mb-4">
                <div class="card paper-card">
                    <div class="card-body">
                        <h5 class="card-title">${paper.title}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">${paper.authors}</h6>
                        <p class="card-text">${paper.abstract}</p>
                        <div class="paper-meta d-flex justify-content-between">
                            <span>Published: ${paper.year} | Source: ${paper.source}</span>
                            <button class="btn btn-sm btn-outline-info view-paper" data-id="${paper.id}">View Details</button>
                        </div>
                    </div>
                </div>
            </div>
            `;
        });
        
        paperResults.innerHTML = html;
        
        // Add event listeners to view paper buttons
        document.querySelectorAll('.view-paper').forEach(button => {
            button.addEventListener('click', function() {
                const paperId = this.getAttribute('data-id');
                // In a production app, this would open paper details
                alert(`Viewing paper details for ID: ${paperId}`);
            });
        });
    }
    
    /**
     * Display sample analysis results (for demo purposes)
     */
    function displaySampleAnalysis() {
        // Generate sample topics
        const topics = [
            { name: "Neural Networks", weight: 0.89 },
            { name: "TensorFlow Implementation", weight: 0.76 },
            { name: "Deep Learning Optimization", weight: 0.72 },
            { name: "Performance Evaluation", weight: 0.68 }
        ];
        
        // Generate sample trends
        const trends = [
            { name: "Transformer Architecture", growth: 0.85, year: 2020 },
            { name: "TensorFlow for Edge Devices", growth: 0.72, year: 2021 },
            { name: "Federated Learning", growth: 0.65, year: 2022 }
        ];
        
        // Display topics
        let topicsHtml = '';
        topics.forEach(topic => {
            topicsHtml += `
            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                ${topic.name}
                <span class="badge bg-info rounded-pill">${topic.weight.toFixed(2)}</span>
            </li>
            `;
        });
        
        document.getElementById('topicsList').innerHTML = topicsHtml;
        
        // Display trends
        let trendsHtml = '';
        trends.forEach(trend => {
            trendsHtml += `
            <li class="list-group-item d-flex justify-content-between align-items-center bg-transparent">
                ${trend.name} (since ${trend.year})
                <span class="badge bg-info rounded-pill">+${(trend.growth * 100).toFixed(0)}%</span>
            </li>
            `;
        });
        
        document.getElementById('trendsList').innerHTML = trendsHtml;
    }
    
    /**
     * Display sample hypothesis (for demo purposes)
     */
    function displaySampleHypothesis(researchQuestion) {
        const words = researchQuestion.split(' ').filter(w => w.length > 3);
        const keyword = words.length > 0 ? words[Math.floor(Math.random() * words.length)] : 'neural networks';
        
        const hypothesisText = `A hybrid ${keyword} architecture that combines attention mechanisms with convolutional layers will improve performance on low-resource datasets by at least 15% compared to standard architectures.`;
        
        const reasoningText = `Analysis of recent papers shows that attention mechanisms excel at capturing long-range dependencies, while convolutional layers are efficient at extracting local features. The combination addresses the limitations of each approach individually. Furthermore, several papers indicate that hybrid architectures show greater efficiency in low-resource scenarios, suggesting a promising direction for improving performance with limited training data.`;
        
        document.getElementById('hypothesisText').textContent = hypothesisText;
        document.getElementById('hypothesisReasoning').textContent = reasoningText;
        document.getElementById('confidenceScore').textContent = `Confidence: 0.83`;
        
        // Store current hypothesis
        currentHypothesis = hypothesisText;
    }
    
    /**
     * Display sample experiment design (for demo purposes)
     */
    function displaySampleExperiment() {
        document.getElementById('experimentTitle').textContent = `Evaluating Hybrid Architecture Performance on Low-Resource Datasets`;
        
        document.getElementById('experimentMethodology').textContent = `We will implement the proposed hybrid architecture combining attention mechanisms with convolutional layers using TensorFlow. The model will be evaluated on three low-resource datasets with varying characteristics: a small image classification dataset, a limited NLP corpus, and a specialized domain dataset. Performance will be compared against baseline models using standard architectures.`;
        
        // Independent variables
        const independentVars = [
            "Architecture type (hybrid vs. standard)",
            "Attention mechanism configuration (variants: self-attention, cross-attention)",
            "Dataset size (10%, 25%, 50% of full dataset)",
            "Training hyperparameters (learning rate, batch size)"
        ];
        
        // Dependent variables
        const dependentVars = [
            "Model accuracy",
            "Convergence rate",
            "Computational efficiency",
            "Performance degradation with reduced dataset size"
        ];
        
        // Display variables
        let indVarsHtml = '';
        independentVars.forEach(v => {
            indVarsHtml += `<li>${v}</li>`;
        });
        document.getElementById('independentVars').innerHTML = indVarsHtml;
        
        let depVarsHtml = '';
        dependentVars.forEach(v => {
            depVarsHtml += `<li>${v}</li>`;
        });
        document.getElementById('dependentVars').innerHTML = depVarsHtml;
        
        // Expected outcomes and limitations
        document.getElementById('expectedOutcomes').textContent = `We expect the hybrid architecture to show at least 15% improvement in accuracy on low-resource datasets compared to standard architectures. The attention component should help maintain performance even with reduced training data, while the convolutional component should improve computational efficiency. The greatest improvements are expected on datasets with both local and global feature dependencies.`;
        
        document.getElementById('limitations').textContent = `Potential limitations include increased model complexity that may require additional tuning, possible overfitting on very small datasets, and domain-specific variations in performance. The experiment will need to carefully control for these factors and include appropriate regularization strategies.`;
    }
    
    /**
     * Add a message to the chat container
     */
    function addChatMessage(sender, message, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${className}`;
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Show an error message
     */
    function showError(message) {
        console.error(message);
        alert(message);
    }
});