import logging
from flask import Blueprint, request, jsonify
from models import ResearchProject, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage
from app import db
from agents.agent_controller import AgentController

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Initialize agent controller
agent_controller = AgentController()

@api_bp.route('/search', methods=['POST'])
def search_papers():
    """API endpoint to search for papers"""
    try:
        data = request.json
        project_id = data.get('project_id')
        query = data.get('query')
        
        if not project_id or not query:
            return jsonify({'error': 'Project ID and query are required'}), 400
        
        # Check if project exists
        project = ResearchProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Process the query through the agent controller
        result = agent_controller.process_research_question(project_id, query)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in search_papers API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions"""
    try:
        data = request.json
        project_id = data.get('project_id')
        message = data.get('message')
        
        if not project_id or not message:
            return jsonify({'error': 'Project ID and message are required'}), 400
        
        # Check if project exists
        project = ResearchProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Handle the chat query
        response = agent_controller.handle_chat_query(project_id, message)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/summarize/<int:paper_id>', methods=['POST'])
def summarize_paper(paper_id):
    """API endpoint to summarize a specific paper"""
    try:
        # Check if paper exists
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Check if summary already exists
        existing_summary = PaperSummary.query.filter_by(paper_id=paper_id).first()
        if existing_summary:
            return jsonify({
                'summary': existing_summary.summary_text,
                'key_findings': existing_summary.get_key_findings()
            })
        
        # Convert paper to dictionary for summarization agent
        paper_dict = {
            'title': paper.title,
            'abstract': paper.abstract,
            'external_id': paper.external_id,
            'source': paper.source
        }
        
        # Generate summary
        summarization_agent = agent_controller.summarization_agent
        summary_result = summarization_agent.summarize_paper(paper_dict)
        
        # Store summary in database
        if 'error' not in summary_result:
            summary = PaperSummary(
                summary_text=summary_result.get('summary', ''),
                paper_id=paper.id
            )
            
            # Store key findings if available
            if 'key_findings' in summary_result:
                summary.set_key_findings(summary_result['key_findings'])
            
            db.session.add(summary)
            db.session.commit()
        
        return jsonify(summary_result)
        
    except Exception as e:
        logger.error(f"Error in summarize_paper API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/generate-hypothesis/<int:project_id>', methods=['POST'])
def generate_hypothesis(project_id):
    """API endpoint to generate a hypothesis for a project"""
    try:
        data = request.json
        research_question = data.get('research_question')
        
        if not research_question:
            return jsonify({'error': 'Research question is required'}), 400
        
        # Check if project exists
        project = ResearchProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get papers for the project
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        if not papers:
            return jsonify({'error': 'No papers found in this project'}), 400
        
        # Convert papers to dictionaries
        paper_dicts = []
        for paper in papers:
            paper_dict = {
                'title': paper.title,
                'abstract': paper.abstract,
                'source': paper.source,
                'external_id': paper.external_id
            }
            
            # Add summary if available
            if paper.summary:
                paper_dict['summary'] = paper.summary.summary_text
            
            paper_dicts.append(paper_dict)
        
        # Generate hypothesis
        hypothesis_agent = agent_controller.hypothesis_agent
        hypothesis_result = hypothesis_agent.generate_hypotheses(paper_dicts, research_question)
        
        # Store hypotheses in database
        if 'error' not in hypothesis_result and 'hypotheses' in hypothesis_result:
            for hyp_data in hypothesis_result['hypotheses']:
                hypothesis = Hypothesis(
                    hypothesis_text=hyp_data.get('hypothesis', ''),
                    reasoning=hyp_data.get('reasoning', ''),
                    confidence_score=hyp_data.get('confidence', 0.5),
                    project_id=project_id
                )
                
                if 'supporting_evidence' in hyp_data:
                    hypothesis.set_supporting_evidence(hyp_data['supporting_evidence'])
                
                db.session.add(hypothesis)
            
            db.session.commit()
        
        return jsonify(hypothesis_result)
        
    except Exception as e:
        logger.error(f"Error in generate_hypothesis API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/design-experiment/<int:hypothesis_id>', methods=['POST'])
def design_experiment(hypothesis_id):
    """API endpoint to design an experiment for a hypothesis"""
    try:
        # Check if hypothesis exists
        hypothesis = Hypothesis.query.get(hypothesis_id)
        if not hypothesis:
            return jsonify({'error': 'Hypothesis not found'}), 404
        
        # Get project papers for reference
        project_id = hypothesis.project_id
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        # Convert papers to dictionaries
        paper_dicts = []
        for paper in papers:
            paper_dict = {
                'title': paper.title,
                'abstract': paper.abstract
            }
            
            # Add summary if available
            if paper.summary:
                paper_dict['summary'] = paper.summary.summary_text
            
            paper_dicts.append(paper_dict)
        
        # Design experiment
        experiment_agent = agent_controller.experiment_agent
        experiment_result = experiment_agent.design_experiment(hypothesis.hypothesis_text, paper_dicts)
        
        # Store experiment in database
        if 'error' not in experiment_result:
            experiment = ExperimentDesign(
                title=experiment_result.get('title', 'Experiment Design'),
                methodology=experiment_result.get('methodology', ''),
                controls=experiment_result.get('controls', ''),
                expected_outcomes=experiment_result.get('expected_outcomes', ''),
                limitations=experiment_result.get('limitations', ''),
                hypothesis_id=hypothesis.id
            )
            
            if 'variables' in experiment_result:
                experiment.set_variables(experiment_result['variables'])
            
            db.session.add(experiment)
            db.session.commit()
        
        return jsonify(experiment_result)
        
    except Exception as e:
        logger.error(f"Error in design_experiment API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze-papers/<int:project_id>', methods=['POST'])
def analyze_papers(project_id):
    """API endpoint to analyze papers in a project"""
    try:
        # Check if project exists
        project = ResearchProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get papers for the project
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        if not papers:
            return jsonify({'error': 'No papers found in this project'}), 400
        
        # Convert papers to dictionaries
        paper_dicts = []
        for paper in papers:
            paper_dict = {
                'title': paper.title,
                'source': paper.source,
                'external_id': paper.external_id
            }
            
            # Add summary if available
            if paper.summary:
                paper_dict['summary'] = paper.summary.summary_text
            
            paper_dicts.append(paper_dict)
        
        # Analyze papers
        summarization_agent = agent_controller.summarization_agent
        analysis_result = summarization_agent.analyze_papers(paper_dicts)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"Error in analyze_papers API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/export/<int:project_id>', methods=['GET'])
def export_project(project_id):
    """API endpoint to export project data"""
    try:
        # Check if project exists
        project = ResearchProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get all project data
        papers = Paper.query.filter_by(project_id=project_id).all()
        hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
        
        # Format paper data
        paper_data = []
        for paper in papers:
            paper_dict = {
                'id': paper.id,
                'title': paper.title,
                'authors': paper.get_authors(),
                'abstract': paper.abstract,
                'url': paper.url,
                'pdf_url': paper.pdf_url,
                'source': paper.source,
                'external_id': paper.external_id
            }
            
            # Add summary if available
            if paper.summary:
                paper_dict['summary'] = {
                    'text': paper.summary.summary_text,
                    'key_findings': paper.summary.get_key_findings()
                }
            
            paper_data.append(paper_dict)
        
        # Format hypothesis data
        hypothesis_data = []
        for hypothesis in hypotheses:
            hyp_dict = {
                'id': hypothesis.id,
                'text': hypothesis.hypothesis_text,
                'reasoning': hypothesis.reasoning,
                'confidence_score': hypothesis.confidence_score,
                'supporting_evidence': hypothesis.get_supporting_evidence() if hasattr(hypothesis, 'get_supporting_evidence') else {}
            }
            
            # Get related experiments
            experiments = ExperimentDesign.query.filter_by(hypothesis_id=hypothesis.id).all()
            experiment_list = []
            
            for exp in experiments:
                exp_dict = {
                    'id': exp.id,
                    'title': exp.title,
                    'methodology': exp.methodology,
                    'variables': exp.get_variables() if hasattr(exp, 'get_variables') else {},
                    'controls': exp.controls,
                    'expected_outcomes': exp.expected_outcomes,
                    'limitations': exp.limitations
                }
                
                experiment_list.append(exp_dict)
            
            hyp_dict['experiments'] = experiment_list
            hypothesis_data.append(hyp_dict)
        
        # Compile project data
        project_data = {
            'project': {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'created_at': project.created_at.isoformat()
            },
            'papers': paper_data,
            'hypotheses': hypothesis_data
        }
        
        return jsonify(project_data)
        
    except Exception as e:
        logger.error(f"Error in export_project API: {str(e)}")
        return jsonify({'error': str(e)}), 500
