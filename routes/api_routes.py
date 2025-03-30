"""
API routes for AURA Research Assistant
"""

import json
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import ResearchProject, ResearchQuery, Paper, Hypothesis, ChatMessage
from agents.agent_controller import AgentController
from services.export_service import ExportService

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
agent_controller = AgentController()
export_service = ExportService()

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all research projects"""
    try:
        projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
        
        # Convert to JSON-serializable format
        result = []
        for project in projects:
            result.append({
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None,
                'url': url_for('main.view_project', project_id=project.id)
            })
        
        return jsonify({'projects': result})
    
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return jsonify({'error': 'Error retrieving projects'}), 500

@api_bp.route('/projects/<int:project_id>/papers', methods=['GET'])
def get_papers(project_id):
    """Get papers for a project"""
    try:
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        # Convert to JSON-serializable format
        result = []
        for paper in papers:
            result.append({
                'id': paper.id,
                'title': paper.title,
                'authors': paper.get_authors() if hasattr(paper, 'get_authors') else [],
                'abstract': paper.abstract,
                'url': paper.url,
                'pdf_url': paper.pdf_url,
                'published_date': paper.published_date.isoformat() if paper.published_date else None,
                'source': paper.source
            })
        
        return jsonify({'papers': result})
    
    except Exception as e:
        logger.error(f"Error getting papers for project {project_id}: {e}")
        return jsonify({'error': 'Error retrieving papers'}), 500

@api_bp.route('/projects/<int:project_id>/chat', methods=['GET'])
def get_chat_messages(project_id):
    """Get chat messages for a project"""
    try:
        messages = ChatMessage.query.filter_by(project_id=project_id).order_by(ChatMessage.created_at).all()
        
        # Convert to JSON-serializable format
        result = []
        for message in messages:
            result.append({
                'id': message.id,
                'role': message.role,
                'content': message.content,
                'agent_type': message.agent_type,
                'created_at': message.created_at.isoformat() if message.created_at else None
            })
        
        return jsonify({'messages': result})
    
    except Exception as e:
        logger.error(f"Error getting chat messages for project {project_id}: {e}")
        return jsonify({'error': 'Error retrieving chat messages'}), 500

@api_bp.route('/projects/<int:project_id>/hypotheses', methods=['GET'])
def get_hypotheses(project_id):
    """Get hypotheses for a project"""
    try:
        hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
        
        # Convert to JSON-serializable format
        result = []
        for hypothesis in hypotheses:
            result.append({
                'id': hypothesis.id,
                'hypothesis_text': hypothesis.hypothesis_text,
                'reasoning': hypothesis.reasoning,
                'confidence_score': hypothesis.confidence_score,
                'supporting_evidence': hypothesis.get_supporting_evidence() if hasattr(hypothesis, 'get_supporting_evidence') else {},
                'created_at': hypothesis.created_at.isoformat() if hypothesis.created_at else None
            })
        
        return jsonify({'hypotheses': result})
    
    except Exception as e:
        logger.error(f"Error getting hypotheses for project {project_id}: {e}")
        return jsonify({'error': 'Error retrieving hypotheses'}), 500

@api_bp.route('/projects/<int:project_id>/export', methods=['GET'])
def export_project(project_id):
    """Export project data"""
    try:
        format_type = request.args.get('format', 'json')
        
        # Get project data
        project = ResearchProject.query.get_or_404(project_id)
        papers = Paper.query.filter_by(project_id=project_id).all()
        hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
        
        # Export data
        export_data = export_service.export_project(project, papers, hypotheses, format_type)
        
        return jsonify(export_data)
    
    except Exception as e:
        logger.error(f"Error exporting project {project_id}: {e}")
        return jsonify({'error': 'Error exporting project data'}), 500

@api_bp.route('/tensorflow/analyze', methods=['POST'])
def tensorflow_analyze():
    """Analyze data with TensorFlow"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        papers = data.get('papers', [])
        analysis_type = data.get('analysis_type', 'clustering')
        project_id = data.get('project_id')
        
        if not papers:
            return jsonify({'error': 'No papers provided for analysis'}), 400
        
        # Run TensorFlow analysis
        results = agent_controller.analyze_with_tensorflow(project_id, analysis_type, papers)
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error in TensorFlow analysis API: {e}")
        return jsonify({'error': f'Error in analysis: {str(e)}'}), 500