"""
Main routes for AURA Research Assistant
"""

import json
import logging
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import ResearchProject, ResearchQuery, Paper, Hypothesis, ChatMessage
from agents.agent_controller import AgentController

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize agent controller
agent_controller = AgentController()

@main_bp.route('/')
def index():
    """Render the main page"""
    try:
        # Get all research projects
        projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
        return render_template('index.html', projects=projects)
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return render_template('index.html', projects=[])

@main_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create a new research project"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description', '')
            
            if not title:
                flash('Project title is required', 'error')
                return redirect(url_for('main.new_project'))
            
            project = ResearchProject(title=title, description=description)
            db.session.add(project)
            db.session.commit()
            
            flash('Project created successfully', 'success')
            return redirect(url_for('main.view_project', project_id=project.id))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating project: {e}")
            flash('Error creating project', 'error')
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            flash('Error creating project', 'error')
    
    return render_template('new_project.html')

@main_bp.route('/projects/<int:project_id>')
def view_project(project_id):
    """View a research project"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        papers = Paper.query.filter_by(project_id=project_id).all()
        hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
        
        return render_template('research.html', 
                              project=project, 
                              papers=papers, 
                              hypotheses=hypotheses)
    
    except Exception as e:
        logger.error(f"Error viewing project {project_id}: {e}")
        flash('Error loading project', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/projects/<int:project_id>/query', methods=['POST'])
def submit_query(project_id):
    """Submit a research query"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        query_text = request.form.get('query_text')
        
        if not query_text:
            flash('Query text is required', 'error')
            return redirect(url_for('main.view_project', project_id=project_id))
        
        # Save the query
        query = ResearchQuery(query_text=query_text, project_id=project_id)
        db.session.add(query)
        db.session.commit()
        
        # Process the query with the agent controller
        results = agent_controller.process_research_query(project_id, query_text)
        
        # Redirect to results page
        return redirect(url_for('main.view_project', project_id=project_id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error submitting query: {e}")
        flash('Error processing query', 'error')
    except Exception as e:
        logger.error(f"Error submitting query: {e}")
        flash('Error processing query', 'error')
    
    return redirect(url_for('main.view_project', project_id=project_id))

@main_bp.route('/projects/<int:project_id>/chat', methods=['POST'])
def chat_query(project_id):
    """Submit a chat query"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        query_text = request.form.get('message')
        
        if not query_text:
            return jsonify({'error': 'Message is required'})
        
        # Save the chat message
        message = ChatMessage(
            role='user',
            content=query_text,
            project_id=project_id
        )
        db.session.add(message)
        db.session.commit()
        
        # Process the chat query with the agent controller
        response = agent_controller.handle_chat_query(project_id, query_text)
        
        # Save the agent response
        agent_message = ChatMessage(
            role='agent',
            content=response.get('response', 'Sorry, I could not process your request.'),
            agent_type=response.get('agent_type', 'general'),
            project_id=project_id
        )
        db.session.add(agent_message)
        db.session.commit()
        
        return jsonify({
            'response': agent_message.content,
            'agent_type': agent_message.agent_type,
            'timestamp': agent_message.created_at.isoformat()
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in chat: {e}")
        return jsonify({'error': 'Database error processing your message'})
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': 'Error processing your message'})

@main_bp.route('/projects/<int:project_id>/tensorflow-analysis', methods=['POST'])
def tensorflow_analysis(project_id):
    """Run TensorFlow analysis on papers"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        analysis_type = request.form.get('analysis_type', 'clustering')
        
        # Get all papers for the project
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        if not papers:
            flash('No papers available for analysis', 'error')
            return redirect(url_for('main.view_project', project_id=project_id))
        
        # Convert papers to list of dictionaries
        paper_dicts = []
        for paper in papers:
            paper_dict = {
                'id': paper.id,
                'title': paper.title,
                'abstract': paper.abstract,
                'authors': paper.get_authors() if hasattr(paper, 'get_authors') else [],
                'published_date': paper.published_date.isoformat() if paper.published_date else None
            }
            paper_dicts.append(paper_dict)
        
        # Run TensorFlow analysis
        results = agent_controller.analyze_with_tensorflow(project_id, analysis_type, paper_dicts)
        
        # Return results as JSON for the front-end to render
        return jsonify(results)
    
    except SQLAlchemyError as e:
        logger.error(f"Database error in TensorFlow analysis: {e}")
        return jsonify({'error': 'Database error in analysis'})
    except Exception as e:
        logger.error(f"Error in TensorFlow analysis: {e}")
        return jsonify({'error': f'Error in analysis: {str(e)}'})

@main_bp.route('/projects/<int:project_id>/hypothesis', methods=['POST'])
def generate_hypothesis(project_id):
    """Generate a hypothesis based on research papers"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        research_question = request.form.get('research_question')
        
        if not research_question:
            flash('Research question is required', 'error')
            return redirect(url_for('main.view_project', project_id=project_id))
        
        # Get all papers for the project
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        if not papers:
            flash('No papers available for hypothesis generation', 'error')
            return redirect(url_for('main.view_project', project_id=project_id))
        
        # Convert papers to list of dictionaries
        paper_dicts = []
        for paper in papers:
            paper_dict = {
                'id': paper.id,
                'title': paper.title,
                'abstract': paper.abstract,
                'authors': paper.get_authors() if hasattr(paper, 'get_authors') else []
            }
            paper_dicts.append(paper_dict)
        
        # Generate hypothesis
        hypothesis_data = agent_controller.generate_hypothesis(research_question, paper_dicts)
        
        # Create new hypothesis in database
        hypothesis = Hypothesis(
            hypothesis_text=hypothesis_data.get('hypothesis', ''),
            reasoning=hypothesis_data.get('reasoning', ''),
            confidence_score=hypothesis_data.get('confidence_score', 0.0),
            project_id=project_id
        )
        
        # Set supporting evidence if available
        if 'supporting_evidence' in hypothesis_data:
            hypothesis.set_supporting_evidence(hypothesis_data['supporting_evidence'])
        
        db.session.add(hypothesis)
        db.session.commit()
        
        flash('Hypothesis generated successfully', 'success')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error generating hypothesis: {e}")
        flash('Database error generating hypothesis', 'error')
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        flash(f'Error generating hypothesis: {str(e)}', 'error')
    
    return redirect(url_for('main.view_project', project_id=project_id))

@main_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete a research project"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        
        flash('Project deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting project {project_id}: {e}")
        flash('Error deleting project', 'error')
    
    return redirect(url_for('main.index'))

@main_bp.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')