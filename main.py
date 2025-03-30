from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime

# Import app and db from our app.py
from app import app, db, create_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize app
app = create_app()

# Import models after db initialization
from models import ResearchProject, ResearchQuery, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage

# Import agent controller
from agents.agent_controller import AgentController

# Initialize agent controller
agent_controller = AgentController()

# Routes
@app.route('/')
def index():
    """Render the main page"""
    projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/research/<int:project_id>')
def research(project_id):
    """Render the research project page"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).all()
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
    return render_template('research.html', project=project, papers=papers, hypotheses=hypotheses)

@app.route('/api/projects', methods=['GET', 'POST'])
def api_projects():
    """API endpoint for projects"""
    if request.method == 'GET':
        projects = ResearchProject.query.order_by(ResearchProject.created_at.desc()).all()
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in projects])
    
    elif request.method == 'POST':
        data = request.json
        project = ResearchProject(
            title=data['title'],
            description=data.get('description', '')
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'created_at': project.created_at.isoformat() if project.created_at else None
        }), 201

@app.route('/api/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
def api_project(project_id):
    """API endpoint for a specific project"""
    project = ResearchProject.query.get_or_404(project_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'created_at': project.created_at.isoformat() if project.created_at else None
        })
    
    elif request.method == 'PUT':
        data = request.json
        project.title = data.get('title', project.title)
        project.description = data.get('description', project.description)
        project.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None
        })
    
    elif request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return '', 204

@app.route('/api/projects/<int:project_id>/query', methods=['POST'])
def api_research_query(project_id):
    """API endpoint for submitting a research query"""
    project = ResearchProject.query.get_or_404(project_id)
    data = request.json
    query_text = data['query']
    
    # Process the research query with the agent controller
    results = agent_controller.process_research_question(project_id, query_text)
    
    return jsonify(results)

@app.route('/api/projects/<int:project_id>/chat', methods=['POST'])
def api_chat(project_id):
    """API endpoint for chat interactions"""
    project = ResearchProject.query.get_or_404(project_id)
    data = request.json
    query_text = data['message']
    
    # Process the chat query with the agent controller
    response = agent_controller.handle_chat_query(project_id, query_text)
    
    return jsonify(response)

@app.route('/api/projects/<int:project_id>/papers', methods=['GET'])
def api_papers(project_id):
    """API endpoint for papers in a project"""
    project = ResearchProject.query.get_or_404(project_id)
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'authors': p.get_authors(),
        'abstract': p.abstract,
        'url': p.url,
        'source': p.source,
        'published_date': p.published_date.isoformat() if p.published_date else None
    } for p in papers])

@app.route('/api/projects/<int:project_id>/hypotheses', methods=['GET'])
def api_hypotheses(project_id):
    """API endpoint for hypotheses in a project"""
    project = ResearchProject.query.get_or_404(project_id)
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
    
    return jsonify([{
        'id': h.id,
        'hypothesis_text': h.hypothesis_text,
        'reasoning': h.reasoning,
        'confidence_score': h.confidence_score
    } for h in hypotheses])

@app.route('/api/projects/<int:project_id>/experiments', methods=['GET'])
def api_experiments(project_id):
    """API endpoint for experiments in a project"""
    project = ResearchProject.query.get_or_404(project_id)
    
    # Get all hypotheses for this project
    hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
    hypothesis_ids = [h.id for h in hypotheses]
    
    # Get experiments for these hypotheses
    experiments = ExperimentDesign.query.filter(ExperimentDesign.hypothesis_id.in_(hypothesis_ids)).all()
    
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'methodology': e.methodology,
        'variables': e.get_variables(),
        'controls': e.controls,
        'expected_outcomes': e.expected_outcomes,
        'hypothesis_id': e.hypothesis_id
    } for e in experiments])

@app.route('/api/projects/<int:project_id>/tf-analysis', methods=['POST'])
def api_tensorflow_analysis(project_id):
    """API endpoint for TensorFlow analysis of papers"""
    project = ResearchProject.query.get_or_404(project_id)
    data = request.json
    analysis_type = data.get('analysis_type', 'all')
    
    # Get papers for this project
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    if not papers:
        return jsonify({'error': 'No papers found for analysis. Please search for papers first.'}), 400
    
    # Convert papers to dictionary format
    paper_dicts = []
    for paper in papers:
        paper_dict = {
            'id': paper.id,
            'title': paper.title,
            'abstract': paper.abstract,
            'authors': paper.get_authors(),
            'source': paper.source,
            'external_id': paper.external_id
        }
        
        # Add metadata if available
        if paper.get_metadata():
            paper_dict['metadata'] = paper.get_metadata()
        
        # Add published date if available
        if paper.published_date:
            paper_dict['published_date'] = paper.published_date
        
        # Add summary if available
        if paper.summary:
            paper_dict['summary'] = paper.summary.summary_text
            paper_dict['key_findings'] = paper.summary.get_key_findings()
        
        paper_dicts.append(paper_dict)
    
    # Perform TensorFlow analysis
    results = agent_controller.tensorflow_agent.analyze_papers_with_tf(paper_dicts, analysis_type)
    
    return jsonify(results)

@app.route('/api/projects/<int:project_id>/tf-research-gaps', methods=['GET'])
def api_research_gaps(project_id):
    """API endpoint for identifying research gaps using TensorFlow"""
    project = ResearchProject.query.get_or_404(project_id)
    
    # Get papers for this project
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    if not papers:
        return jsonify({'error': 'No papers found for analysis. Please search for papers first.'}), 400
    
    # Convert papers to dictionary format
    paper_dicts = []
    for paper in papers:
        paper_dict = {
            'id': paper.id,
            'title': paper.title,
            'abstract': paper.abstract,
            'authors': paper.get_authors(),
            'source': paper.source,
            'external_id': paper.external_id
        }
        
        # Add published date if available
        if paper.published_date:
            paper_dict['published_date'] = paper.published_date
        
        # Add summary if available
        if paper.summary:
            paper_dict['summary'] = paper.summary.summary_text
        
        paper_dicts.append(paper_dict)
    
    # Identify research gaps
    results = agent_controller.tensorflow_agent.identify_research_gaps(paper_dicts)
    
    return jsonify(results)

@app.route('/api/projects/<int:project_id>/tf-classify', methods=['POST'])
def api_classify_papers(project_id):
    """API endpoint for classifying papers using TensorFlow"""
    project = ResearchProject.query.get_or_404(project_id)
    data = request.json
    categories = data.get('categories')
    
    # Get papers for this project
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    if not papers:
        return jsonify({'error': 'No papers found for classification. Please search for papers first.'}), 400
    
    # Convert papers to dictionary format
    paper_dicts = []
    for paper in papers:
        paper_dict = {
            'id': paper.id,
            'title': paper.title,
            'abstract': paper.abstract,
            'source': paper.source
        }
        
        paper_dicts.append(paper_dict)
    
    # Classify papers
    results = agent_controller.tensorflow_agent.classify_research_papers(paper_dicts, categories)
    
    return jsonify(results)

@app.route('/api/projects/<int:project_id>/tf-impact', methods=['POST'])
def api_research_impact(project_id):
    """API endpoint for evaluating research impact using TensorFlow"""
    project = ResearchProject.query.get_or_404(project_id)
    data = request.json
    research_field = data.get('research_field', project.title)
    
    # Get papers for this project
    papers = Paper.query.filter_by(project_id=project_id).all()
    
    if not papers:
        return jsonify({'error': 'No papers found for impact analysis. Please search for papers first.'}), 400
    
    # Convert papers to dictionary format
    paper_dicts = []
    for paper in papers:
        paper_dict = {
            'id': paper.id,
            'title': paper.title,
            'abstract': paper.abstract,
            'authors': paper.get_authors(),
            'source': paper.source
        }
        
        # Add published date if available
        if paper.published_date:
            paper_dict['published_date'] = paper.published_date
        
        paper_dicts.append(paper_dict)
    
    # Evaluate research impact
    results = agent_controller.tensorflow_agent.evaluate_research_impact(research_field, paper_dicts)
    
    return jsonify(results)

if __name__ == "__main__":
    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)