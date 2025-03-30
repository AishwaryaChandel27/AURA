"""
API routes for AURA Research Assistant
Handles AJAX requests and returns JSON responses
"""

import json
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import SQLAlchemyError

from models import db, ResearchProject, ResearchQuery, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage
from agents.agent_controller import AgentController
from services.openai_service import generate_hypothesis, design_experiment, summarize_paper

# Configure logging
logger = logging.getLogger(__name__)

# Initialize agent controller
agent_controller = AgentController()

# Create blueprint
api_bp = Blueprint("api", __name__)

# Project endpoints
@api_bp.route("/projects", methods=["POST"])
def create_project():
    """Create a new research project"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get("title"):
            return jsonify({"error": "Project title is required"}), 400
        
        # Create new project
        project = ResearchProject(
            title=data.get("title"),
            description=data.get("description", "")
        )
        
        # Save to database
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "created_at": project.created_at.isoformat()
        }), 201
    
    except SQLAlchemyError as e:
        logger.error(f"Database error creating project: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error creating project"}), 500
    
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({"error": "Error creating project"}), 500

@api_bp.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a research project"""
    try:
        project = ResearchProject.query.get_or_404(project_id)
        
        # Delete the project
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({"message": "Project deleted successfully"}), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting project: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error deleting project"}), 500
    
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        return jsonify({"error": "Error deleting project"}), 500

# Paper search and management
@api_bp.route("/projects/<int:project_id>/search", methods=["POST"])
def search_papers(project_id):
    """Search for papers"""
    try:
        data = request.json
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # Get the project
        project = ResearchProject.query.get_or_404(project_id)
        
        # Create a research query record
        research_query = ResearchQuery(
            query_text=query,
            project_id=project_id
        )
        db.session.add(research_query)
        db.session.commit()
        
        # Use agent controller to search for papers
        results = agent_controller.process_research_query(project_id, query)
        
        return jsonify(results), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error during paper search: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error during paper search"}), 500
    
    except Exception as e:
        logger.error(f"Error searching for papers: {e}")
        return jsonify({"error": "Error searching for papers"}), 500

@api_bp.route("/projects/<int:project_id>/papers", methods=["POST"])
def add_paper(project_id):
    """Add a paper to a project"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get("title"):
            return jsonify({"error": "Paper title is required"}), 400
        
        # Check if the project exists
        project = ResearchProject.query.get_or_404(project_id)
        
        # Create new paper
        paper = Paper(
            title=data.get("title"),
            abstract=data.get("abstract", ""),
            url=data.get("url", ""),
            pdf_url=data.get("pdf_url", ""),
            source=data.get("source", "manual"),
            external_id=data.get("id", ""),
            project_id=project_id
        )
        
        # Handle authors
        if data.get("authors"):
            paper.set_authors(data["authors"])
        
        # Handle metadata
        if data.get("metadata"):
            paper.set_metadata(data["metadata"])
        
        # Handle published date
        if data.get("published_date"):
            try:
                paper.published_date = datetime.fromisoformat(data["published_date"])
            except (ValueError, TypeError):
                # If we can't parse the date, ignore it
                pass
        
        # Save to database
        db.session.add(paper)
        db.session.commit()
        
        return jsonify({
            "id": paper.id,
            "title": paper.title,
            "message": "Paper added successfully"
        }), 201
    
    except SQLAlchemyError as e:
        logger.error(f"Database error adding paper: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error adding paper"}), 500
    
    except Exception as e:
        logger.error(f"Error adding paper: {e}")
        return jsonify({"error": "Error adding paper"}), 500

@api_bp.route("/papers/<int:paper_id>/summarize", methods=["POST"])
def summarize_paper_api(paper_id):
    """Summarize a paper"""
    try:
        # Get the paper
        paper = Paper.query.get_or_404(paper_id)
        
        # Check if we already have a summary
        if paper.summary:
            return jsonify({
                "message": "Paper already has a summary",
                "summary": paper.summary.summary_text,
                "key_findings": paper.summary.get_key_findings() if paper.summary.key_findings else []
            }), 200
        
        # Generate summary using OpenAI
        summary_data = summarize_paper(paper.title, paper.abstract)
        
        # Create summary record
        summary = PaperSummary(
            summary_text=summary_data.get("summary", ""),
            paper_id=paper.id
        )
        
        # Set key findings
        if summary_data.get("key_findings"):
            summary.set_key_findings(summary_data["key_findings"])
        
        # Save to database
        db.session.add(summary)
        db.session.commit()
        
        return jsonify({
            "message": "Paper summarized successfully",
            "summary": summary.summary_text,
            "key_findings": summary.get_key_findings()
        }), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error summarizing paper: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error summarizing paper"}), 500
    
    except Exception as e:
        logger.error(f"Error summarizing paper: {e}")
        return jsonify({"error": "Error summarizing paper"}), 500

# Hypothesis endpoints
@api_bp.route("/projects/<int:project_id>/hypotheses", methods=["POST"])
def generate_hypothesis_api(project_id):
    """Generate a hypothesis for a project"""
    try:
        data = request.json
        research_question = data.get("research_question", "")
        
        if not research_question:
            return jsonify({"error": "Research question is required"}), 400
        
        # Get the project
        project = ResearchProject.query.get_or_404(project_id)
        
        # Get project papers
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        # Prepare papers for API
        paper_data = []
        for paper in papers:
            paper_dict = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract
            }
            
            if paper.summary:
                paper_dict["summary"] = {
                    "summary_text": paper.summary.summary_text,
                    "key_findings": paper.summary.get_key_findings()
                }
            
            paper_data.append(paper_dict)
        
        # Generate hypothesis using agent controller
        hypothesis_data = agent_controller.generate_hypothesis(research_question, paper_data)
        
        # Create hypothesis record
        hypothesis = Hypothesis(
            hypothesis_text=hypothesis_data.get("hypothesis_text", ""),
            reasoning=hypothesis_data.get("reasoning", ""),
            confidence_score=hypothesis_data.get("confidence_score", 0.0),
            project_id=project_id
        )
        
        # Set supporting evidence
        if hypothesis_data.get("supporting_evidence"):
            hypothesis.set_supporting_evidence(hypothesis_data["supporting_evidence"])
        
        # Save to database
        db.session.add(hypothesis)
        db.session.commit()
        
        return jsonify({
            "message": "Hypothesis generated successfully",
            "id": hypothesis.id,
            "hypothesis": hypothesis.hypothesis_text,
            "confidence": hypothesis.confidence_score
        }), 201
    
    except SQLAlchemyError as e:
        logger.error(f"Database error generating hypothesis: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error generating hypothesis"}), 500
    
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return jsonify({"error": "Error generating hypothesis"}), 500

# Experiment design endpoint
@api_bp.route("/hypotheses/<int:hypothesis_id>/experiments", methods=["POST"])
def design_experiment_api(hypothesis_id):
    """Design an experiment for a hypothesis"""
    try:
        # Get the hypothesis
        hypothesis = Hypothesis.query.get_or_404(hypothesis_id)
        
        # Use OpenAI to design the experiment
        experiment_data = design_experiment(hypothesis.hypothesis_text)
        
        # Create experiment record
        experiment = ExperimentDesign(
            title=experiment_data.get("experiment_title", f"Experiment for Hypothesis {hypothesis_id}"),
            methodology=experiment_data.get("methodology", ""),
            controls=experiment_data.get("controls", ""),
            expected_outcomes=experiment_data.get("expected_outcomes", ""),
            limitations=experiment_data.get("limitations", ""),
            hypothesis_id=hypothesis_id
        )
        
        # Set variables
        if experiment_data.get("variables"):
            experiment.set_variables(experiment_data["variables"])
        
        # Save to database
        db.session.add(experiment)
        db.session.commit()
        
        return jsonify({
            "message": "Experiment designed successfully",
            "id": experiment.id,
            "title": experiment.title
        }), 201
    
    except SQLAlchemyError as e:
        logger.error(f"Database error designing experiment: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error designing experiment"}), 500
    
    except Exception as e:
        logger.error(f"Error designing experiment: {e}")
        return jsonify({"error": "Error designing experiment"}), 500

# TensorFlow analysis endpoint
@api_bp.route("/projects/<int:project_id>/analyze", methods=["POST"])
def analyze_project(project_id):
    """Analyze project papers with TensorFlow"""
    try:
        data = request.json
        analysis_type = data.get("analysis_type", "all")
        
        # Get the project
        project = ResearchProject.query.get_or_404(project_id)
        
        # Get project papers
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        # Prepare papers for API
        paper_data = []
        for paper in papers:
            paper_dict = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "published_date": paper.published_date.isoformat() if paper.published_date else None
            }
            
            if paper.summary:
                paper_dict["summary"] = {
                    "summary_text": paper.summary.summary_text,
                    "key_findings": paper.summary.get_key_findings()
                }
            
            paper_data.append(paper_dict)
        
        # Perform TensorFlow analysis using the agent
        analysis_result = agent_controller.tensorflow_agent.analyze_papers_with_tf(paper_data, analysis_type)
        
        return jsonify(analysis_result), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error during analysis: {e}")
        return jsonify({"error": "Database error during analysis"}), 500
    
    except Exception as e:
        logger.error(f"Error analyzing project: {e}")
        return jsonify({"error": f"Error analyzing project: {str(e)}"}), 500

# Research gap identification endpoint
@api_bp.route("/projects/<int:project_id>/gaps", methods=["POST"])
def identify_gaps(project_id):
    """Identify research gaps for a project"""
    try:
        # Get the project
        project = ResearchProject.query.get_or_404(project_id)
        
        # Get project papers
        papers = Paper.query.filter_by(project_id=project_id).all()
        
        # Prepare papers for API
        paper_data = []
        for paper in papers:
            paper_dict = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "published_date": paper.published_date.isoformat() if paper.published_date else None
            }
            
            if paper.summary:
                paper_dict["summary"] = {
                    "summary_text": paper.summary.summary_text,
                    "key_findings": paper.summary.get_key_findings()
                }
            
            paper_data.append(paper_dict)
        
        # Identify research gaps using the TensorFlow agent
        gaps_result = agent_controller.tensorflow_agent.identify_research_gaps(paper_data)
        
        return jsonify(gaps_result), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error identifying gaps: {e}")
        return jsonify({"error": "Database error identifying gaps"}), 500
    
    except Exception as e:
        logger.error(f"Error identifying research gaps: {e}")
        return jsonify({"error": f"Error identifying research gaps: {str(e)}"}), 500

# Chat endpoint
@api_bp.route("/projects/<int:project_id>/chat", methods=["POST"])
def chat(project_id):
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get("message", "")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get the project
        project = ResearchProject.query.get_or_404(project_id)
        
        # Save user message
        user_message = ChatMessage(
            role="user",
            content=message,
            project_id=project_id
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Process message with agent controller
        response = agent_controller.handle_chat_query(project_id, message)
        
        # Save agent response
        agent_message = ChatMessage(
            role="agent",
            content=response.get("content", "I don't have a response for that."),
            agent_type=response.get("agent_type", "general"),
            project_id=project_id
        )
        db.session.add(agent_message)
        db.session.commit()
        
        return jsonify({
            "role": "agent",
            "content": agent_message.content,
            "agent_type": agent_message.agent_type,
            "created_at": agent_message.created_at.isoformat()
        }), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error during chat: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error during chat"}), 500
    
    except Exception as e:
        logger.error(f"Error handling chat: {e}")
        return jsonify({"error": "Error handling chat message"}), 500

# Export endpoint
@api_bp.route("/projects/<int:project_id>/export", methods=["GET"])
def export_project(project_id):
    """Export a project as JSON"""
    try:
        # Get the project
        project = ResearchProject.query.get_or_404(project_id)
        
        # Get all project data
        papers = Paper.query.filter_by(project_id=project_id).all()
        hypotheses = Hypothesis.query.filter_by(project_id=project_id).all()
        queries = ResearchQuery.query.filter_by(project_id=project_id).all()
        
        # Prepare export data
        export_data = {
            "project": {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            },
            "papers": [],
            "hypotheses": [],
            "queries": []
        }
        
        # Add papers
        for paper in papers:
            paper_dict = {
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "url": paper.url,
                "pdf_url": paper.pdf_url,
                "source": paper.source,
                "external_id": paper.external_id,
                "created_at": paper.created_at.isoformat(),
                "authors": paper.get_authors(),
                "metadata": paper.get_metadata(),
                "published_date": paper.published_date.isoformat() if paper.published_date else None
            }
            
            # Add summary if available
            if paper.summary:
                paper_dict["summary"] = {
                    "summary_text": paper.summary.summary_text,
                    "key_findings": paper.summary.get_key_findings(),
                    "created_at": paper.summary.created_at.isoformat()
                }
            
            export_data["papers"].append(paper_dict)
        
        # Add hypotheses
        for hypothesis in hypotheses:
            hypothesis_dict = {
                "id": hypothesis.id,
                "hypothesis_text": hypothesis.hypothesis_text,
                "reasoning": hypothesis.reasoning,
                "confidence_score": hypothesis.confidence_score,
                "supporting_evidence": hypothesis.get_supporting_evidence(),
                "created_at": hypothesis.created_at.isoformat(),
                "experiments": []
            }
            
            # Add experiments
            experiments = ExperimentDesign.query.filter_by(hypothesis_id=hypothesis.id).all()
            for experiment in experiments:
                experiment_dict = {
                    "id": experiment.id,
                    "title": experiment.title,
                    "methodology": experiment.methodology,
                    "variables": experiment.get_variables(),
                    "controls": experiment.controls,
                    "expected_outcomes": experiment.expected_outcomes,
                    "limitations": experiment.limitations,
                    "created_at": experiment.created_at.isoformat()
                }
                hypothesis_dict["experiments"].append(experiment_dict)
            
            export_data["hypotheses"].append(hypothesis_dict)
        
        # Add queries
        for query in queries:
            query_dict = {
                "id": query.id,
                "query_text": query.query_text,
                "created_at": query.created_at.isoformat()
            }
            export_data["queries"].append(query_dict)
        
        return jsonify(export_data), 200
    
    except SQLAlchemyError as e:
        logger.error(f"Database error exporting project: {e}")
        return jsonify({"error": "Database error exporting project"}), 500
    
    except Exception as e:
        logger.error(f"Error exporting project: {e}")
        return jsonify({"error": "Error exporting project"}), 500