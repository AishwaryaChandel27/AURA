"""
Main routes for AURA Research Assistant
"""

import logging

from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from models import ResearchProject, Paper, Hypothesis, ExperimentDesign

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page / project list"""
    projects = ResearchProject.query.order_by(ResearchProject.updated_at.desc()).all()
    return render_template('index.html', projects=projects)

@main_bp.route('/research/<int:project_id>')
def research(project_id):
    """Research page for a specific project"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).all()
    return render_template('research.html', project=project, papers=papers)

@main_bp.route('/results/<int:project_id>')
def results(project_id):
    """Results page for a specific project"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).all()
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
    experiments = ExperimentDesign.query.join(Hypothesis).filter(Hypothesis.project_id == project_id).all()
    
    return render_template('results.html', 
                           project=project, 
                           papers=papers, 
                           hypotheses=hypotheses, 
                           experiments=experiments)