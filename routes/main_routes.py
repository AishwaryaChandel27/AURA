from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models import ResearchProject, ResearchQuery, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage
from app import db
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with list of research projects"""
    projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@main_bp.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new research project"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Project title is required', 'danger')
            return redirect(url_for('main.new_project'))
        
        project = ResearchProject(
            title=title,
            description=description
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully', 'success')
        return redirect(url_for('main.project', project_id=project.id))
    
    return render_template('index.html', show_new_project=True)

@main_bp.route('/project/<int:project_id>')
def project(project_id):
    """View a research project"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).order_by(Paper.id.desc()).all()
    queries = ResearchQuery.query.filter_by(project_id=project_id).order_by(ResearchQuery.id.desc()).all()
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).order_by(Hypothesis.id.desc()).all()
    
    # Get chat messages
    chat_messages = ChatMessage.query.filter_by(
        project_id=project_id
    ).order_by(ChatMessage.id.asc()).all()
    
    # Format chat messages for display
    formatted_messages = []
    for msg in chat_messages:
        if msg.role == 'agent':
            try:
                content = json.loads(msg.content)
                message_text = content.get('message', '')
            except:
                message_text = msg.content
        else:
            message_text = msg.content
            
        formatted_messages.append({
            'role': msg.role,
            'content': message_text,
            'agent_type': msg.agent_type,
            'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return render_template(
        'research.html',
        project=project,
        papers=papers,
        queries=queries,
        hypotheses=hypotheses,
        chat_messages=formatted_messages
    )

@main_bp.route('/project/<int:project_id>/papers')
def papers(project_id):
    """View papers for a research project"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).order_by(Paper.id.desc()).all()
    
    return render_template('results.html', project=project, papers=papers, active_tab='papers')

@main_bp.route('/project/<int:project_id>/hypotheses')
def hypotheses(project_id):
    """View hypotheses for a research project"""
    project = ResearchProject.query.get_or_404(project_id)
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).order_by(Hypothesis.id.desc()).all()
    
    return render_template('results.html', project=project, hypotheses=hypotheses, active_tab='hypotheses')

@main_bp.route('/project/<int:project_id>/experiments')
def experiments(project_id):
    """View experiments for a research project"""
    project = ResearchProject.query.get_or_404(project_id)
    experiments = ExperimentDesign.query.join(Hypothesis).filter(
        Hypothesis.project_id == project_id
    ).order_by(ExperimentDesign.id.desc()).all()
    
    return render_template('results.html', project=project, experiments=experiments, active_tab='experiments')

@main_bp.route('/paper/<int:paper_id>')
def paper_details(paper_id):
    """View details of a specific paper"""
    paper = Paper.query.get_or_404(paper_id)
    
    # Convert database objects to dictionaries for template
    paper_dict = {
        'id': paper.id,
        'title': paper.title,
        'authors': paper.get_authors(),
        'abstract': paper.abstract,
        'url': paper.url,
        'pdf_url': paper.pdf_url,
        'published_date': paper.published_date,
        'source': paper.source,
        'external_id': paper.external_id,
        'metadata': paper.get_metadata()
    }
    
    # Get summary if available
    summary_dict = None
    if paper.summary:
        summary_dict = {
            'text': paper.summary.summary_text,
            'key_findings': paper.summary.get_key_findings(),
            'created_at': paper.summary.created_at
        }
    
    # Get project
    project = ResearchProject.query.get(paper.project_id)
    
    return render_template(
        'results.html',
        project=project,
        paper=paper_dict,
        summary=summary_dict,
        active_tab='paper_details'
    )

@main_bp.route('/hypothesis/<int:hypothesis_id>')
def hypothesis_details(hypothesis_id):
    """View details of a specific hypothesis"""
    hypothesis = Hypothesis.query.get_or_404(hypothesis_id)
    
    # Convert database objects to dictionaries for template
    hypothesis_dict = {
        'id': hypothesis.id,
        'text': hypothesis.hypothesis_text,
        'reasoning': hypothesis.reasoning,
        'confidence_score': hypothesis.confidence_score,
        'supporting_evidence': hypothesis.get_supporting_evidence() if hasattr(hypothesis, 'get_supporting_evidence') else {},
        'created_at': hypothesis.created_at
    }
    
    # Get related experiments
    experiments = ExperimentDesign.query.filter_by(hypothesis_id=hypothesis.id).all()
    experiment_dicts = []
    
    for exp in experiments:
        experiment_dicts.append({
            'id': exp.id,
            'title': exp.title,
            'methodology': exp.methodology,
            'variables': exp.get_variables() if hasattr(exp, 'get_variables') else {},
            'controls': exp.controls,
            'expected_outcomes': exp.expected_outcomes,
            'limitations': exp.limitations,
            'created_at': exp.created_at
        })
    
    # Get project
    project = ResearchProject.query.get(hypothesis.project_id)
    
    return render_template(
        'results.html',
        project=project,
        hypothesis=hypothesis_dict,
        experiments=experiment_dicts,
        active_tab='hypothesis_details'
    )

@main_bp.route('/experiment/<int:experiment_id>')
def experiment_details(experiment_id):
    """View details of a specific experiment design"""
    experiment = ExperimentDesign.query.get_or_404(experiment_id)
    
    # Convert database objects to dictionaries for template
    experiment_dict = {
        'id': experiment.id,
        'title': experiment.title,
        'methodology': experiment.methodology,
        'variables': experiment.get_variables() if hasattr(experiment, 'get_variables') else {},
        'controls': experiment.controls,
        'expected_outcomes': experiment.expected_outcomes,
        'limitations': experiment.limitations,
        'created_at': experiment.created_at
    }
    
    # Get related hypothesis
    hypothesis = Hypothesis.query.get(experiment.hypothesis_id)
    hypothesis_dict = {
        'id': hypothesis.id,
        'text': hypothesis.hypothesis_text,
        'confidence_score': hypothesis.confidence_score
    }
    
    # Get project
    project = ResearchProject.query.get(hypothesis.project_id)
    
    return render_template(
        'results.html',
        project=project,
        experiment=experiment_dict,
        hypothesis=hypothesis_dict,
        active_tab='experiment_details'
    )
