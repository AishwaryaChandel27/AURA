"""
Main routes for AURA Research Assistant
"""

import logging
import json
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import ResearchProject, ResearchQuery, Paper, Hypothesis, ExperimentDesign, ChatMessage
from services import OpenAIService, ArxivService, SemanticScholarService, TensorFlowService

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize services
openai_service = OpenAIService()
arxiv_service = ArxivService()
semantic_scholar_service = SemanticScholarService()
tensorflow_service = TensorFlowService()

@main_bp.route('/')
def index():
    """Render the index page"""
    try:
        # Get projects for display
        projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
        return render_template('index.html', projects=projects)
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return render_template('index.html', projects=[], error=str(e))

@main_bp.route('/api/search', methods=['POST'])
def search_papers():
    """Search for papers via API"""
    try:
        data = request.json
        query = data.get('query', '')
        sources = data.get('sources', ['arxiv', 'semantic_scholar'])
        max_results = data.get('max_results', 10)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        results = []
        
        # Search arXiv if specified
        if 'arxiv' in sources:
            arxiv_results = arxiv_service.search_papers(query, max_results=max_results//2)
            results.extend(arxiv_results)
        
        # Search Semantic Scholar if specified
        if 'semantic_scholar' in sources:
            ss_results = semantic_scholar_service.search_papers(query, max_results=max_results//2)
            results.extend(ss_results)
        
        return jsonify({"papers": results})
    
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/analyze', methods=['POST'])
def analyze_papers():
    """Analyze papers with TensorFlow"""
    try:
        data = request.json
        papers = data.get('papers', [])
        
        if not papers:
            return jsonify({"error": "Papers data is required"}), 400
        
        # Analyze papers using TensorFlow service
        analysis_results = tensorflow_service.analyze_papers(papers)
        
        return jsonify(analysis_results)
    
    except Exception as e:
        logger.error(f"Error analyzing papers: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/generate_hypothesis', methods=['POST'])
def generate_hypothesis():
    """Generate research hypothesis"""
    try:
        data = request.json
        research_question = data.get('research_question', '')
        papers = data.get('papers', [])
        
        if not research_question or not papers:
            return jsonify({"error": "Research question and papers are required"}), 400
        
        # Generate hypothesis using OpenAI service
        hypothesis = openai_service.generate_hypothesis(research_question, papers)
        
        return jsonify(hypothesis)
    
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/design_experiment', methods=['POST'])
def design_experiment():
    """Design experiment for hypothesis"""
    try:
        data = request.json
        hypothesis = data.get('hypothesis', '')
        papers = data.get('papers', [])
        
        if not hypothesis:
            return jsonify({"error": "Hypothesis is required"}), 400
        
        # Design experiment using OpenAI service
        experiment = openai_service.design_experiment(hypothesis, papers)
        
        return jsonify(experiment)
    
    except Exception as e:
        logger.error(f"Error designing experiment: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI assistant"""
    try:
        data = request.json
        message = data.get('message', '')
        project_id = data.get('project_id')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Process message with OpenAI service
        response = openai_service.generate_text(message)
        
        # If project ID is provided, store chat history
        if project_id:
            try:
                # Store user message
                user_message = ChatMessage(
                    role="user",
                    content=message,
                    project_id=project_id
                )
                db.session.add(user_message)
                
                # Store assistant response
                assistant_message = ChatMessage(
                    role="agent",
                    content=response,
                    agent_type="openai",
                    project_id=project_id
                )
                db.session.add(assistant_message)
                db.session.commit()
            
            except SQLAlchemyError as e:
                logger.error(f"Error storing chat messages: {e}")
                db.session.rollback()
        
        return jsonify({"response": response})
    
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({"error": str(e)}), 500