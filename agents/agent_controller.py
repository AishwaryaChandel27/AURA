"""
Agent Controller for AURA Research Assistant
Coordinates the agent system and routes user queries to the appropriate agents
"""

import logging
import random
from models import db, ResearchProject, Paper, Hypothesis, ExperimentDesign

# Set up logging
logger = logging.getLogger(__name__)

class AgentController:
    """
    Controller for coordinating multiple agents for research tasks
    """
    
    def __init__(self):
        """Initialize AgentController with all required agents"""
        logger.info("Initializing AgentController")
        
        # Import lazily to avoid circular dependencies
        from agents.tensorflow_agent import TensorFlowAgent
        
        # Initialize agents
        self.tensorflow_agent = TensorFlowAgent()
    
    def process_research_query(self, project_id, query_text):
        """
        Process a research question through the agent workflow
        
        Args:
            project_id (int): ID of the research project
            query_text (str): The research question or query
            
        Returns:
            dict: Results of the research process
        """
        logger.info(f"Processing research query for project {project_id}: {query_text}")
        
        # Classify query type
        query_type, agent_type = self._classify_query(query_text)
        
        # Process based on query type
        if query_type == "tensorflow_analysis":
            # Get papers for the project
            papers = Paper.query.filter_by(project_id=project_id).all()
            
            # Convert to format expected by TensorFlow agent
            paper_dicts = []
            for paper in papers:
                paper_dict = {
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'authors': paper.get_authors() if hasattr(paper, 'get_authors') else []
                }
                
                # Add summary if available
                if paper.summary:
                    paper_dict['summary'] = paper.summary.summary_text
                    paper_dict['key_findings'] = paper.summary.get_key_findings() if hasattr(paper.summary, 'get_key_findings') else []
                
                paper_dicts.append(paper_dict)
            
            # Run TensorFlow analysis
            results = self.tensorflow_agent.analyze_papers_with_tf(paper_dicts)
            
            # Return with agent info
            return {
                'message': results.get('message', 'TensorFlow analysis completed'),
                'agent_type': 'tensorflow',
                'analysis_results': results
            }
        
        elif query_type == "research_gaps":
            # Get papers for the project
            papers = Paper.query.filter_by(project_id=project_id).all()
            
            # Convert to format expected by TensorFlow agent
            paper_dicts = []
            for paper in papers:
                paper_dict = {
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'authors': paper.get_authors() if hasattr(paper, 'get_authors') else []
                }
                
                # Add summary if available
                if paper.summary:
                    paper_dict['summary'] = paper.summary.summary_text
                    paper_dict['key_findings'] = paper.summary.get_key_findings() if hasattr(paper.summary, 'get_key_findings') else []
                
                paper_dicts.append(paper_dict)
            
            # Identify research gaps
            results = self.tensorflow_agent.identify_research_gaps(paper_dicts)
            
            # Format response
            message = "Research gap analysis completed. "
            if results.get('potential_gaps'):
                message += f"Found {len(results['potential_gaps'])} potential research gaps."
            else:
                message += "No clear research gaps identified."
            
            # Return with agent info
            return {
                'message': message,
                'agent_type': 'tensorflow',
                'gap_analysis': results
            }
        
        else:
            # General response for other query types
            return {
                'message': f"I've received your query: '{query_text}'. To analyze research papers, try asking about TensorFlow analysis or research gaps.",
                'agent_type': 'general',
                'query_type': query_type
            }
    
    def handle_chat_query(self, project_id, query_text):
        """
        Handle a chat query by routing to the appropriate agent
        
        Args:
            project_id (int): ID of the research project
            query_text (str): The user's chat query
            
        Returns:
            dict: Response from the agent
        """
        logger.info(f"Handling chat query for project {project_id}: {query_text}")
        
        # Classify query type
        query_type, agent_type = self._classify_query(query_text)
        
        # Respond based on agent type
        if agent_type == "tensorflow":
            # For TensorFlow-related queries
            response = {
                'message': f"I'll analyze that using TensorFlow! '{query_text}'. To run a full analysis, use the TensorFlow Analysis button.",
                'agent_type': 'tensorflow',
                'query_type': query_type
            }
        
        elif agent_type == "paper":
            # For paper-related queries
            response = {
                'message': f"I can help with paper analysis. To add papers to your project, use the 'Add Paper' button or search for papers using the search bar.",
                'agent_type': 'paper',
                'query_type': query_type
            }
        
        elif agent_type == "hypothesis":
            # For hypothesis-related queries
            response = {
                'message': f"I can generate research hypotheses based on the papers in your project. Try adding some papers first, then run a TensorFlow analysis to get insights.",
                'agent_type': 'hypothesis',
                'query_type': query_type
            }
        
        else:
            # General response
            response = {
                'message': f"I'm AURA, your AI research assistant. I can help with paper analysis, TensorFlow-based insights, and research gap identification. What would you like to explore?",
                'agent_type': 'general',
                'query_type': query_type
            }
        
        return response
    
    def _classify_query(self, query_text):
        """
        Classify the type of query to route to the appropriate agent
        
        Args:
            query_text (str): The user's query text
            
        Returns:
            tuple: Query type and agent type
        """
        # Simple keyword-based classification
        query_text_lower = query_text.lower()
        
        # TensorFlow-related queries
        if any(kw in query_text_lower for kw in ['tensorflow', 'machine learning', 'deep learning', 'analyze', 'analysis']):
            return "tensorflow_analysis", "tensorflow"
        
        # Research gap queries
        elif any(kw in query_text_lower for kw in ['gap', 'missing', 'opportunity', 'future research']):
            return "research_gaps", "tensorflow"
        
        # Paper-related queries
        elif any(kw in query_text_lower for kw in ['paper', 'article', 'publication', 'read', 'download']):
            return "paper_info", "paper"
        
        # Hypothesis-related queries
        elif any(kw in query_text_lower for kw in ['hypothesis', 'theory', 'idea', 'propose']):
            return "hypothesis", "hypothesis"
        
        # Default to general query
        return "general", "general"