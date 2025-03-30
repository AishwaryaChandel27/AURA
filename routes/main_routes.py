"""
Main routes for AURA Research Assistant
Handles web page rendering and form submissions
"""

import logging
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, abort
from sqlalchemy.exc import SQLAlchemyError

from models import ResearchProject, ResearchQuery, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage
from app import db

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Render the index page"""
    # Get all research projects
    projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
    return render_template("index.html", projects=projects)

@main_bp.route("/research/<int:project_id>")
def research(project_id):
    """Render the research page for a specific project"""
    # Get the project
    project = ResearchProject.query.get_or_404(project_id)
    
    # Get project data
    papers = Paper.query.filter_by(project_id=project_id).order_by(Paper.created_at.desc()).all()
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).order_by(Hypothesis.created_at.desc()).all()
    
    # Get chat messages
    chat_messages = ChatMessage.query.filter_by(project_id=project_id).order_by(ChatMessage.created_at).all()
    
    return render_template(
        "research.html", 
        project=project, 
        papers=papers, 
        hypotheses=hypotheses, 
        chat_messages=chat_messages
    )

@main_bp.route("/results/<int:project_id>")
def results(project_id):
    """Render the results page for a specific project"""
    # Get the project
    project = ResearchProject.query.get_or_404(project_id)
    
    # Get project data
    papers = Paper.query.filter_by(project_id=project_id).all()
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
    
    # Get experiments for each hypothesis
    for hypothesis in hypotheses:
        hypothesis.experiment_list = ExperimentDesign.query.filter_by(hypothesis_id=hypothesis.id).all()
    
    return render_template(
        "results.html", 
        project=project, 
        papers=papers, 
        hypotheses=hypotheses
    )