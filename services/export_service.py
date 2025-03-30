"""
Export Service for AURA Research Assistant
Handles exporting of research projects, papers, and results
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from models import ResearchProject, Paper, Hypothesis, ExperimentDesign

# Configure logging
logger = logging.getLogger(__name__)

def export_project_data(project_id: int) -> Dict[str, Any]:
    """
    Export a project and all its data as a JSON-serializable dictionary
    
    Args:
        project_id (int): ID of the project to export
        
    Returns:
        dict: Project data
    """
    logger.info(f"Exporting project {project_id}")
    
    try:
        # Get project
        from app import db
        project = db.session.query(ResearchProject).get(project_id)
        
        if not project:
            logger.error(f"Project {project_id} not found")
            return {'error': 'Project not found'}
        
        # Build project data
        project_data = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'papers': [],
            'hypotheses': []
        }
        
        # Add papers
        for paper in project.papers:
            paper_data = {
                'id': paper.id,
                'title': paper.title,
                'authors': paper.get_authors(),
                'abstract': paper.abstract,
                'url': paper.url,
                'pdf_url': paper.pdf_url,
                'source': paper.source,
                'external_id': paper.external_id,
                'created_at': paper.created_at.isoformat()
            }
            
            # Add published date if available
            if paper.published_date:
                paper_data['published_date'] = paper.published_date.isoformat()
            
            # Add summary if available
            if paper.summary:
                paper_data['summary'] = {
                    'id': paper.summary.id,
                    'summary_text': paper.summary.summary_text,
                    'key_findings': paper.summary.get_key_findings(),
                    'created_at': paper.summary.created_at.isoformat()
                }
            
            project_data['papers'].append(paper_data)
        
        # Add hypotheses
        for hypothesis in project.hypotheses:
            hypothesis_data = {
                'id': hypothesis.id,
                'hypothesis_text': hypothesis.hypothesis_text,
                'reasoning': hypothesis.reasoning,
                'confidence_score': hypothesis.confidence_score,
                'supporting_evidence': hypothesis.get_supporting_evidence(),
                'created_at': hypothesis.created_at.isoformat(),
                'experiments': []
            }
            
            # Add experiments
            for experiment in hypothesis.experiments:
                experiment_data = {
                    'id': experiment.id,
                    'title': experiment.title,
                    'methodology': experiment.methodology,
                    'variables': experiment.get_variables(),
                    'controls': experiment.controls,
                    'expected_outcomes': experiment.expected_outcomes,
                    'limitations': experiment.limitations,
                    'created_at': experiment.created_at.isoformat()
                }
                hypothesis_data['experiments'].append(experiment_data)
            
            project_data['hypotheses'].append(hypothesis_data)
        
        return project_data
    
    except Exception as e:
        logger.error(f"Error exporting project: {e}")
        return {'error': f'Error exporting project: {str(e)}'}

def format_export_for_markdown(project_data: Dict[str, Any]) -> str:
    """
    Format exported project data as a Markdown document
    
    Args:
        project_data (dict): Project data from export_project_data
        
    Returns:
        str: Markdown document
    """
    if 'error' in project_data:
        return f"# Export Error\n\n{project_data['error']}"
    
    # Start with project header
    markdown = f"# {project_data['title']}\n\n"
    
    # Add project description
    if project_data.get('description'):
        markdown += f"{project_data['description']}\n\n"
    
    # Add date information
    markdown += f"*Created: {project_data.get('created_at', 'Unknown')}*  \n"
    markdown += f"*Last Updated: {project_data.get('updated_at', 'Unknown')}*\n\n"
    
    # Add papers section
    markdown += "## Research Papers\n\n"
    
    if project_data.get('papers'):
        for i, paper in enumerate(project_data['papers']):
            markdown += f"### {i+1}. {paper['title']}\n\n"
            
            # Add authors
            if paper.get('authors'):
                markdown += f"**Authors:** {', '.join(paper['authors'])}\n\n"
            
            # Add abstract
            if paper.get('abstract'):
                markdown += f"**Abstract:**  \n{paper['abstract']}\n\n"
            
            # Add summary if available
            if paper.get('summary'):
                markdown += f"**Summary:**  \n{paper['summary']['summary_text']}\n\n"
                
                # Add key findings
                if paper['summary'].get('key_findings'):
                    markdown += "**Key Findings:**\n\n"
                    for finding in paper['summary']['key_findings']:
                        markdown += f"- {finding}\n"
                    markdown += "\n"
            
            # Add source and URLs
            markdown += f"**Source:** {paper.get('source', 'Unknown')}\n\n"
            if paper.get('url'):
                markdown += f"**URL:** [{paper['url']}]({paper['url']})\n\n"
            
            # Add separator between papers
            markdown += "---\n\n"
    else:
        markdown += "*No papers have been added to this project.*\n\n"
    
    # Add hypotheses section
    markdown += "## Research Hypotheses\n\n"
    
    if project_data.get('hypotheses'):
        for i, hypothesis in enumerate(project_data['hypotheses']):
            markdown += f"### Hypothesis {i+1}\n\n"
            markdown += f"**Statement:**  \n{hypothesis['hypothesis_text']}\n\n"
            
            # Add reasoning
            if hypothesis.get('reasoning'):
                markdown += f"**Reasoning:**  \n{hypothesis['reasoning']}\n\n"
            
            # Add confidence score
            if hypothesis.get('confidence_score') is not None:
                confidence_percent = round(hypothesis['confidence_score'] * 100)
                markdown += f"**Confidence Score:** {confidence_percent}%\n\n"
            
            # Add supporting evidence
            if hypothesis.get('supporting_evidence'):
                markdown += "**Supporting Evidence:**\n\n"
                for source, evidence in hypothesis['supporting_evidence'].items():
                    markdown += f"- **{source}:** {evidence}\n"
                markdown += "\n"
            
            # Add experiments
            if hypothesis.get('experiments'):
                markdown += "#### Experiments\n\n"
                for j, experiment in enumerate(hypothesis['experiments']):
                    markdown += f"##### Experiment {j+1}: {experiment['title']}\n\n"
                    
                    # Add methodology
                    if experiment.get('methodology'):
                        markdown += f"**Methodology:**  \n{experiment['methodology']}\n\n"
                    
                    # Add variables
                    if experiment.get('variables'):
                        markdown += "**Variables:**\n\n"
                        
                        # Independent variables
                        if experiment['variables'].get('independent'):
                            markdown += "*Independent Variables:*\n\n"
                            for var in experiment['variables']['independent']:
                                markdown += f"- {var}\n"
                            markdown += "\n"
                        
                        # Dependent variables
                        if experiment['variables'].get('dependent'):
                            markdown += "*Dependent Variables:*\n\n"
                            for var in experiment['variables']['dependent']:
                                markdown += f"- {var}\n"
                            markdown += "\n"
                    
                    # Add controls
                    if experiment.get('controls'):
                        markdown += f"**Controls:**  \n{experiment['controls']}\n\n"
                    
                    # Add expected outcomes
                    if experiment.get('expected_outcomes'):
                        markdown += f"**Expected Outcomes:**  \n{experiment['expected_outcomes']}\n\n"
                    
                    # Add limitations
                    if experiment.get('limitations'):
                        markdown += f"**Limitations:**  \n{experiment['limitations']}\n\n"
            
            # Add separator between hypotheses
            markdown += "---\n\n"
    else:
        markdown += "*No hypotheses have been generated for this project.*\n\n"
    
    # Add footer
    markdown += "## Export Information\n\n"
    markdown += f"This research project was exported from AURA Research Assistant on {datetime.now().strftime('%Y-%m-%d')}.\n\n"
    markdown += "AURA is an AI-powered autonomous research assistant that uses TensorFlow for advanced analysis.\n"
    
    return markdown