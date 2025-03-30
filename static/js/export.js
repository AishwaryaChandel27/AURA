/**
 * Export functionality for AURA Research Assistant
 */

/**
 * Export project data as a downloadable file
 */
function exportResults() {
    // Get export options
    const includeHypotheses = document.getElementById('exportHypotheses').checked;
    const includeExperiments = document.getElementById('exportExperiments').checked;
    const includePaperSummaries = document.getElementById('exportPaperSummaries').checked;
    const includeTFAnalysis = document.getElementById('exportTensorFlowAnalysis').checked;
    const formatJSON = document.getElementById('exportFormatJSON').checked;
    
    // Validate at least one option is selected
    if (!includeHypotheses && !includeExperiments && !includePaperSummaries && !includeTFAnalysis) {
        alert('Please select at least one type of content to export');
        return;
    }
    
    // Show loading state on button
    const exportBtn = document.getElementById('exportBtn');
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exporting...';
    
    // Fetch data from server
    fetch(`/api/projects/${projectId}/export`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            include_hypotheses: includeHypotheses,
            include_experiments: includeExperiments,
            include_paper_summaries: includePaperSummaries,
            include_tf_analysis: includeTFAnalysis,
            format: formatJSON ? 'json' : 'markdown'
        })
    })
    .then(response => {
        if (formatJSON) {
            return response.json();
        } else {
            return response.text();
        }
    })
    .then(data => {
        // Reset button
        exportBtn.disabled = false;
        exportBtn.textContent = 'Export';
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Generate filename
        const timestamp = new Date().toISOString().replace(/[\-:\.]/g, '').substring(0, 15);
        const filename = `aura_export_${projectId}_${timestamp}.${formatJSON ? 'json' : 'md'}`;
        
        // Create a Blob and download
        const contentType = formatJSON ? 'application/json' : 'text/markdown';
        const content = formatJSON ? JSON.stringify(data, null, 2) : data;
        const blob = new Blob([content], { type: contentType });
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
        
        // Close modal
        const exportModal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
        exportModal.hide();
    })
    .catch(error => {
        console.error('Error exporting data:', error);
        
        // Reset button
        exportBtn.disabled = false;
        exportBtn.textContent = 'Export';
        
        alert('Error exporting data. Please try again.');
    });
}

/**
 * Format export data for display
 */
function formatExportData(data, format) {
    if (format === 'json') {
        return JSON.stringify(data, null, 2);
    } else {
        // Convert data to Markdown format
        let markdown = `# AURA Research Export\n\n`;
        markdown += `## Project: ${data.project.title}\n\n`;
        
        if (data.project.description) {
            markdown += `${data.project.description}\n\n`;
        }
        
        markdown += `Export Date: ${new Date().toLocaleString()}\n\n`;
        
        // Add hypotheses
        if (data.hypotheses && data.hypotheses.length > 0) {
            markdown += `## Hypotheses\n\n`;
            
            data.hypotheses.forEach(hypothesis => {
                markdown += `### ${hypothesis.id}. Hypothesis (${Math.round(hypothesis.confidence_score * 100)}% Confidence)\n\n`;
                markdown += `${hypothesis.hypothesis_text}\n\n`;
                
                if (hypothesis.reasoning) {
                    markdown += `**Reasoning:**\n\n${hypothesis.reasoning}\n\n`;
                }
                
                if (hypothesis.supporting_evidence) {
                    markdown += `**Supporting Evidence:**\n\n`;
                    for (const source in hypothesis.supporting_evidence) {
                        markdown += `- ${source}: ${hypothesis.supporting_evidence[source]}\n`;
                    }
                    markdown += `\n`;
                }
            });
        }
        
        // Add experiments
        if (data.experiments && data.experiments.length > 0) {
            markdown += `## Experiment Designs\n\n`;
            
            data.experiments.forEach(experiment => {
                markdown += `### ${experiment.title}\n\n`;
                
                if (experiment.methodology) {
                    markdown += `**Methodology:**\n\n${experiment.methodology}\n\n`;
                }
                
                if (experiment.variables) {
                    markdown += `**Variables:**\n\n`;
                    markdown += `- Independent: ${experiment.variables.independent.join(', ')}\n`;
                    markdown += `- Dependent: ${experiment.variables.dependent.join(', ')}\n\n`;
                }
                
                if (experiment.controls) {
                    markdown += `**Controls:**\n\n${experiment.controls}\n\n`;
                }
                
                if (experiment.expected_outcomes) {
                    markdown += `**Expected Outcomes:**\n\n${experiment.expected_outcomes}\n\n`;
                }
                
                if (experiment.limitations) {
                    markdown += `**Limitations:**\n\n${experiment.limitations}\n\n`;
                }
            });
        }
        
        // Add paper summaries
        if (data.paper_summaries && data.paper_summaries.length > 0) {
            markdown += `## Paper Summaries\n\n`;
            
            data.paper_summaries.forEach(paper => {
                markdown += `### ${paper.title}\n\n`;
                
                if (paper.authors) {
                    markdown += `**Authors:** ${paper.authors.join(', ')}\n\n`;
                }
                
                if (paper.published_date) {
                    markdown += `**Published:** ${new Date(paper.published_date).toLocaleDateString()}\n\n`;
                }
                
                if (paper.source) {
                    markdown += `**Source:** ${paper.source}\n\n`;
                }
                
                if (paper.summary) {
                    markdown += `**Summary:**\n\n${paper.summary.text}\n\n`;
                    
                    if (paper.summary.key_findings && paper.summary.key_findings.length > 0) {
                        markdown += `**Key Findings:**\n\n`;
                        paper.summary.key_findings.forEach(finding => {
                            markdown += `- ${finding}\n`;
                        });
                        markdown += `\n`;
                    }
                }
            });
        }
        
        // Add TensorFlow analysis
        if (data.tf_analysis) {
            markdown += `## TensorFlow Analysis\n\n`;
            
            if (data.tf_analysis.topic_analysis) {
                markdown += `### Topic Analysis\n\n`;
                
                if (data.tf_analysis.topic_analysis.description) {
                    markdown += `${data.tf_analysis.topic_analysis.description}\n\n`;
                }
                
                if (data.tf_analysis.topic_analysis.topics) {
                    data.tf_analysis.topic_analysis.topics.forEach(topic => {
                        markdown += `**Topic ${topic.id}:** ${topic.keywords.join(', ')}\n\n`;
                        if (topic.description) {
                            markdown += `${topic.description}\n\n`;
                        }
                    });
                }
            }
            
            if (data.tf_analysis.research_gaps) {
                markdown += `### Research Gaps\n\n`;
                
                data.tf_analysis.research_gaps.forEach(gap => {
                    markdown += `**Gap (${Math.round(gap.confidence * 100)}% Confidence):** ${gap.description}\n\n`;
                    
                    if (gap.suggestions && gap.suggestions.length > 0) {
                        markdown += `**Research Directions:**\n\n`;
                        gap.suggestions.forEach(suggestion => {
                            markdown += `- ${suggestion}\n`;
                        });
                        markdown += `\n`;
                    }
                });
            }
        }
        
        return markdown;
    }
}