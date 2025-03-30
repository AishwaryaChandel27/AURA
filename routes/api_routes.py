"""
API routes for AURA Research Assistant
"""

import json
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify
from app import db
from models import ResearchProject, ResearchQuery, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage
from agents.tensorflow_agent import TensorFlowAgent
from services import openai_service

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize agents
tensorflow_agent = TensorFlowAgent()

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    projects = ResearchProject.query.order_by(ResearchProject.updated_at.desc()).all()
    return jsonify({
        'projects': [
            {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'paper_count': len(project.papers)
            } for project in projects
        ]
    })

@api_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.json
    
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    project = ResearchProject(
        title=title,
        description=description
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
        'updated_at': project.updated_at.isoformat()
    })

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project"""
    project = ResearchProject.query.get_or_404(project_id)
    
    return jsonify({
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
        'updated_at': project.updated_at.isoformat(),
        'paper_count': len(project.papers),
        'hypothesis_count': len(project.hypotheses)
    })

@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    project = ResearchProject.query.get_or_404(project_id)
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Project {project_id} deleted'
    })

@api_bp.route('/projects/<int:project_id>/papers', methods=['GET'])
def get_papers(project_id):
    """Get all papers for a project"""
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    return jsonify({
        'papers': [
            {
                'id': paper.id,
                'title': paper.title,
                'authors': paper.get_authors(),
                'abstract': paper.abstract,
                'url': paper.url,
                'pdf_url': paper.pdf_url,
                'published_date': paper.published_date.isoformat() if paper.published_date else None,
                'source': paper.source,
                'has_summary': bool(paper.summary)
            } for paper in papers
        ]
    })

@api_bp.route('/projects/<int:project_id>/papers', methods=['POST'])
def add_paper(project_id):
    """Add a paper to a project"""
    # Check if project exists
    project = ResearchProject.query.get_or_404(project_id)
    
    data = request.json
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # Create paper
    paper = Paper(
        title=title,
        abstract=data.get('abstract', '').strip(),
        url=data.get('url', '').strip(),
        pdf_url=data.get('pdf_url', '').strip(),
        source=data.get('source', 'manual'),
        external_id=data.get('external_id', ''),
        project_id=project_id
    )
    
    # Set published date if provided
    published_date = data.get('published_date')
    if published_date:
        try:
            if 'T' in published_date:
                paper.published_date = datetime.fromisoformat(published_date)
            else:
                paper.published_date = datetime.strptime(published_date, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Invalid date format: {published_date}")
    
    # Set authors if provided
    authors = data.get('authors', [])
    if authors:
        paper.set_authors(authors)
    
    # Save to database
    db.session.add(paper)
    db.session.commit()
    
    # Update project's updated_at timestamp
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'id': paper.id,
        'title': paper.title,
        'authors': paper.get_authors(),
        'abstract': paper.abstract,
        'url': paper.url,
        'pdf_url': paper.pdf_url,
        'published_date': paper.published_date.isoformat() if paper.published_date else None,
        'source': paper.source
    })

@api_bp.route('/projects/<int:project_id>/papers/<int:paper_id>', methods=['GET'])
def get_paper(project_id, paper_id):
    """Get a specific paper"""
    paper = Paper.query.filter_by(id=paper_id, project_id=project_id).first_or_404()
    
    paper_data = {
        'id': paper.id,
        'title': paper.title,
        'authors': paper.get_authors(),
        'abstract': paper.abstract,
        'url': paper.url,
        'pdf_url': paper.pdf_url,
        'published_date': paper.published_date.isoformat() if paper.published_date else None,
        'source': paper.source,
        'external_id': paper.external_id
    }
    
    # Add summary if available
    if paper.summary:
        paper_data['summary'] = {
            'summary_text': paper.summary.summary_text,
            'key_findings': paper.summary.get_key_findings(),
            'created_at': paper.summary.created_at.isoformat()
        }
    
    return jsonify(paper_data)

@api_bp.route('/projects/<int:project_id>/papers/<int:paper_id>/summarize', methods=['POST'])
def summarize_paper(project_id, paper_id):
    """Summarize a paper"""
    paper = Paper.query.filter_by(id=paper_id, project_id=project_id).first_or_404()
    
    # Check if paper already has a summary
    if paper.summary:
        return jsonify({
            'message': 'Paper already has a summary',
            'summary': {
                'summary_text': paper.summary.summary_text,
                'key_findings': paper.summary.get_key_findings()
            }
        })
    
    # Create paper dictionary for OpenAI service
    paper_dict = {
        'title': paper.title,
        'authors': paper.get_authors(),
        'abstract': paper.abstract
    }
    
    # Generate summary with OpenAI
    try:
        summary_data = openai_service.summarize_paper(paper_dict)
        
        # Create summary object
        summary = PaperSummary(
            summary_text=summary_data.get('summary', ''),
            paper_id=paper.id
        )
        
        # Set key findings
        key_findings = summary_data.get('key_findings', [])
        if key_findings:
            summary.set_key_findings(key_findings)
        
        # Save to database
        db.session.add(summary)
        db.session.commit()
        
        return jsonify({
            'message': 'Paper summarized successfully',
            'summary': {
                'summary_text': summary.summary_text,
                'key_findings': summary.get_key_findings()
            }
        })
    except Exception as e:
        logger.error(f"Error summarizing paper: {e}")
        return jsonify({
            'error': f'Error summarizing paper: {str(e)}'
        }), 500

@api_bp.route('/projects/<int:project_id>/tf-analysis', methods=['POST'])
def tensorflow_analysis(project_id):
    """Run TensorFlow analysis on project papers"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    if not papers:
        return jsonify({
            'error': 'No papers available for analysis'
        }), 400
    
    data = request.json or {}
    analysis_type = data.get('analysis_type', 'all')
    
    # Prepare papers for analysis
    paper_data = []
    for paper in papers:
        paper_dict = {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.get_authors(),
            'abstract': paper.abstract,
            'published_date': paper.published_date.isoformat() if paper.published_date else None,
            'source': paper.source
        }
        
        # Add summary if available
        if paper.summary:
            paper_dict['summary'] = {
                'summary_text': paper.summary.summary_text,
                'key_findings': paper.summary.get_key_findings()
            }
        
        paper_data.append(paper_dict)
    
    # Run TensorFlow analysis
    try:
        analysis_results = tensorflow_agent.analyze_papers_with_tf(paper_data, analysis_type)
        
        # Save analysis results to be accessible from window object in JavaScript
        window_data = {
            'project_id': project_id,
            'analysis_type': analysis_type,
            'paper_count': len(papers),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if 'topic_analysis' in analysis_results:
            window_data['topic_analysis'] = analysis_results['topic_analysis']
        
        if 'cluster_analysis' in analysis_results:
            window_data['cluster_analysis'] = analysis_results['cluster_analysis']
        
        if 'trend_analysis' in analysis_results:
            window_data['trend_analysis'] = analysis_results['trend_analysis']
        
        if 'visualization_data' in analysis_results:
            window_data['visualization_data'] = analysis_results['visualization_data']
        
        # Add response message
        analysis_results['message'] = f"TensorFlow analysis completed on {len(papers)} papers"
        
        return jsonify(analysis_results)
    except Exception as e:
        logger.error(f"Error running TensorFlow analysis: {e}")
        return jsonify({
            'error': f'Error running TensorFlow analysis: {str(e)}'
        }), 500

@api_bp.route('/projects/<int:project_id>/research-gaps', methods=['POST'])
def identify_research_gaps(project_id):
    """Identify research gaps in project papers"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    if not papers:
        return jsonify({
            'error': 'No papers available for analysis'
        }), 400
    
    # Prepare papers for analysis
    paper_data = []
    for paper in papers:
        paper_dict = {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.get_authors(),
            'abstract': paper.abstract,
            'published_date': paper.published_date.isoformat() if paper.published_date else None,
            'source': paper.source
        }
        
        # Add summary if available
        if paper.summary:
            paper_dict['summary'] = {
                'summary_text': paper.summary.summary_text,
                'key_findings': paper.summary.get_key_findings()
            }
        
        paper_data.append(paper_dict)
    
    # Identify research gaps
    try:
        gap_analysis = tensorflow_agent.identify_research_gaps(paper_data)
        
        # Save to chat history
        chat_message = ChatMessage(
            role='agent',
            content=json.dumps(gap_analysis),
            agent_type='tensorflow',
            project_id=project_id
        )
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify(gap_analysis)
    except Exception as e:
        logger.error(f"Error identifying research gaps: {e}")
        return jsonify({
            'error': f'Error identifying research gaps: {str(e)}'
        }), 500

@api_bp.route('/projects/<int:project_id>/chat', methods=['POST'])
def chat(project_id):
    """Chat with the research assistant"""
    project = ResearchProject.query.get_or_404(project_id)
    data = request.json
    
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Store user message
    user_message = ChatMessage(
        role='user',
        content=message,
        project_id=project_id
    )
    db.session.add(user_message)
    db.session.commit()
    
    # Analyze the query to determine the appropriate agent
    try:
        query_analysis = openai_service.analyze_query(message)
        tensorflow_relevance = query_analysis.get('tensorflow_relevance', '')
        relevance_score = query_analysis.get('relevance_score', 0)
        
        # Use TensorFlow agent if the query is relevant to TensorFlow
        agent_type = 'tensorflow' if relevance_score > 0.7 else 'general'
        
        # Generate response based on agent type
        if agent_type == 'tensorflow':
            papers = Paper.query.filter_by(project_id=project_id).all()
            paper_data = []
            for paper in papers:
                paper_dict = {
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract
                }
                paper_data.append(paper_dict)
            
            if 'hypothesis' in message.lower():
                # Generate a hypothesis
                response = tensorflow_agent.suggest_experimental_design(message)
                response_text = f"Here's a potential experiment design using TensorFlow:\n\n{response.get('experiment_title')}\n\n{response.get('tensorflow_approach')}\n\nModel architecture: {response.get('model_architecture')}"
            else:
                # General TensorFlow response
                response_text = f"I'll analyze this using TensorFlow. {tensorflow_relevance}"
        else:
            # General response using OpenAI
            response = openai_service.client.chat.completions.create(
                model=openai_service.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a research assistant that helps with research projects."},
                    {"role": "user", "content": message}
                ]
            )
            response_text = response.choices[0].message.content
        
        # Store agent response
        agent_message = ChatMessage(
            role='agent',
            content=response_text,
            agent_type=agent_type,
            project_id=project_id
        )
        db.session.add(agent_message)
        db.session.commit()
        
        return jsonify({
            'message': response_text,
            'agent_type': agent_type
        })
    except Exception as e:
        logger.error(f"Error generating chat response: {e}")
        
        # Store error message
        error_message = ChatMessage(
            role='system',
            content=f"Error generating response: {str(e)}",
            project_id=project_id
        )
        db.session.add(error_message)
        db.session.commit()
        
        return jsonify({
            'error': f'Error generating response: {str(e)}',
            'message': 'I encountered an error while processing your request. Please try again.',
            'agent_type': 'system'
        }), 500