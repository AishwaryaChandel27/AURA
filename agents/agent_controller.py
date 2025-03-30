"""
Agent Controller for AURA Research Assistant
Coordinates the agent system and routes user queries to the appropriate agents
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.data_retrieval_agent import DataRetrievalAgent
from agents.summarization_agent import SummarizationAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.experiment_agent import ExperimentAgent
from agents.tensorflow_agent import TensorFlowAgent
from services.openai_service import OpenAIService

# Set up logging
logger = logging.getLogger(__name__)

class AgentController:
    """
    Controller for coordinating multiple agents for research tasks
    """
    
    def __init__(self):
        """Initialize AgentController with all required agents"""
        self.data_agent = DataRetrievalAgent()
        self.summarization_agent = SummarizationAgent()
        self.hypothesis_agent = HypothesisAgent()
        self.experiment_agent = ExperimentAgent()
        self.tensorflow_agent = TensorFlowAgent()
        self.openai_service = OpenAIService()
    
    def process_research_query(self, project_id: int, query_text: str) -> Dict[str, Any]:
        """
        Process a research question through the agent workflow
        
        Args:
            project_id (int): ID of the research project
            query_text (str): The research question or query
            
        Returns:
            dict: Results of the research process
        """
        try:
            logger.info(f"Processing research query for project {project_id}: {query_text}")
            
            # Step 1: Retrieve papers related to the query
            papers = self.data_agent.search_papers(query_text, max_results=10)
            
            # Step 2: Summarize papers (in a real app, might save these to the database)
            paper_summaries = []
            for paper in papers:
                paper_summary = self.summarization_agent.summarize_paper(paper)
                paper_summaries.append(paper_summary)
                
                # In a real app, would save paper to the database
                # paper_id = self.data_agent.add_paper_to_project(paper, project_id)
            
            # Step 3: Generate a hypothesis
            hypothesis = self.hypothesis_agent.generate_hypothesis(query_text, papers)
            
            # Step 4: Generate TensorFlow analysis (if appropriate)
            query_type = self._classify_query(query_text)
            if query_type.get('analysis_needed', False):
                analysis_results = self.tensorflow_agent.analyze_papers(papers, query_type.get('analysis_type'))
            else:
                analysis_results = {}
            
            return {
                'query': query_text,
                'papers': papers,
                'paper_summaries': paper_summaries,
                'hypothesis': hypothesis,
                'analysis_results': analysis_results
            }
        
        except Exception as e:
            logger.error(f"Error processing research query: {e}")
            return {
                'query': query_text,
                'error': f"Error processing query: {str(e)}"
            }
    
    def handle_chat_query(self, project_id: int, query_text: str) -> Dict[str, Any]:
        """
        Handle a chat query by routing to the appropriate agent
        
        Args:
            project_id (int): ID of the research project
            query_text (str): The user's chat query
            
        Returns:
            dict: Response from the agent
        """
        try:
            logger.info(f"Handling chat query for project {project_id}: {query_text}")
            
            # Classify the query to determine which agent should handle it
            query_info = self._classify_query(query_text)
            agent_type = query_info.get('agent_type', 'general')
            
            # Route to the appropriate agent
            if agent_type == 'data_retrieval':
                # Search for papers
                search_query = query_info.get('search_query', query_text)
                papers = self.data_agent.search_papers(search_query, max_results=5)
                
                # Format response
                response = f"I found {len(papers)} papers related to '{search_query}':\n\n"
                for i, paper in enumerate(papers[:5], 1):
                    response += f"{i}. {paper.get('title', 'Untitled')}\n"
                    authors = paper.get('authors', [])
                    if authors:
                        if isinstance(authors[0], dict):
                            author_names = [a.get('name', '') for a in authors]
                            response += f"   Authors: {', '.join(author_names[:3])}"
                            if len(author_names) > 3:
                                response += f" and {len(author_names) - 3} more"
                        else:
                            response += f"   Authors: {', '.join(authors[:3])}"
                            if len(authors) > 3:
                                response += f" and {len(authors) - 3} more"
                        response += "\n"
                    response += "\n"
                
                return {'agent_type': 'data_retrieval', 'response': response}
                
            elif agent_type == 'summarization':
                # Extract paper reference if available
                paper_ref = query_info.get('paper_reference')
                
                if paper_ref:
                    # In a real app, would retrieve paper from the database
                    # paper = self.data_agent.search_memory(project_id, paper_ref)
                    
                    # For now, search for papers and use the first one
                    papers = self.data_agent.search_papers(paper_ref, max_results=1)
                    if papers:
                        summary = self.summarization_agent.summarize_paper(papers[0])
                        response = f"Summary of '{papers[0].get('title', 'the paper')}':\n\n"
                        response += summary.get('summary', 'No summary available.')
                        return {'agent_type': 'summarization', 'response': response}
                    else:
                        return {'agent_type': 'summarization', 'response': f"I couldn't find a paper matching '{paper_ref}'."}
                else:
                    return {'agent_type': 'summarization', 'response': "Please specify which paper you'd like me to summarize."}
                
            elif agent_type == 'hypothesis':
                # Extract research question if available
                research_question = query_info.get('research_question', query_text)
                
                # In a real app, would retrieve papers from the database
                # papers = self.data_agent.search_memory(project_id, research_question)
                
                # For now, search for papers
                papers = self.data_agent.search_papers(research_question, max_results=5)
                
                if papers:
                    hypothesis = self.hypothesis_agent.generate_hypothesis(research_question, papers)
                    response = f"Based on the research question '{research_question}', here's a hypothesis:\n\n"
                    response += f"{hypothesis.get('hypothesis', 'No hypothesis generated.')}\n\n"
                    response += f"Reasoning: {hypothesis.get('reasoning', 'No reasoning available.')}\n"
                    response += f"Confidence: {hypothesis.get('confidence_score', 0.0):.2f}/1.0"
                    return {'agent_type': 'hypothesis', 'response': response}
                else:
                    return {'agent_type': 'hypothesis', 'response': f"I need some papers to generate a hypothesis. Please search for papers first."}
                
            elif agent_type == 'experiment':
                # Extract hypothesis if available
                hypothesis_text = query_info.get('hypothesis', query_text)
                
                # In a real app, would retrieve papers from the database
                # papers = self.data_agent.search_memory(project_id, hypothesis_text)
                
                # For now, search for papers
                papers = self.data_agent.search_papers(hypothesis_text, max_results=3)
                
                # Design an experiment
                experiment = self.experiment_agent.design_experiment(hypothesis_text, papers)
                
                response = f"Based on the hypothesis '{hypothesis_text}', here's an experiment design:\n\n"
                response += f"Title: {experiment.get('title', 'Untitled Experiment')}\n\n"
                response += f"Methodology: {experiment.get('methodology', 'No methodology specified.')}\n\n"
                
                variables = experiment.get('variables', {})
                response += "Variables:\n"
                response += f"- Independent: {', '.join(variables.get('independent', ['None specified']))}\n"
                response += f"- Dependent: {', '.join(variables.get('dependent', ['None specified']))}\n\n"
                
                response += f"Controls: {experiment.get('controls', 'No controls specified.')}\n\n"
                response += f"Expected Outcomes: {experiment.get('expected_outcomes', 'No expected outcomes specified.')}"
                
                return {'agent_type': 'experiment', 'response': response}
                
            elif agent_type == 'tensorflow':
                # Extract analysis type
                analysis_type = query_info.get('analysis_type', 'clustering')
                
                # In a real app, would retrieve papers from the database
                # papers = self.data_agent.search_memory(project_id, query_text)
                
                # For now, search for papers
                papers = self.data_agent.search_papers(query_text, max_results=8)
                
                # Analyze papers with TensorFlow
                results = self.tensorflow_agent.analyze_papers(papers, analysis_type)
                
                # Format response based on analysis type
                response = f"TensorFlow Analysis Results ({analysis_type}):\n\n"
                
                if 'error' in results:
                    response += f"Error: {results['error']}\n"
                else:
                    response += f"{results.get('summary', 'Analysis completed.')}\n\n"
                    
                    if analysis_type == 'clustering':
                        clusters = results.get('clusters', [])
                        for i, cluster in enumerate(clusters, 1):
                            response += f"Cluster {i} ({cluster.get('paper_count', 0)} papers):\n"
                            response += f"Keywords: {', '.join(cluster.get('keywords', []))}\n"
                            for j, paper in enumerate(cluster.get('papers', [])[:3], 1):
                                response += f"  {j}. {paper.get('title', 'Untitled')}\n"
                            if len(cluster.get('papers', [])) > 3:
                                response += f"  ... and {len(cluster.get('papers', [])) - 3} more papers\n"
                            response += "\n"
                    
                    elif analysis_type == 'topic_modeling':
                        topics = results.get('topics', [])
                        for i, topic in enumerate(topics, 1):
                            response += f"Topic {i} (weight: {topic.get('weight', 0.0):.2f}):\n"
                            response += f"Keywords: {', '.join(topic.get('keywords', []))}\n"
                            response += "Top papers:\n"
                            for j, paper in enumerate(topic.get('papers', [])[:3], 1):
                                response += f"  {j}. {paper.get('title', 'Untitled')} ({paper.get('weight', 0.0):.2f})\n"
                            if len(topic.get('papers', [])) > 3:
                                response += f"  ... and {len(topic.get('papers', [])) - 3} more papers\n"
                            response += "\n"
                    
                    elif analysis_type == 'similarity':
                        similar_pairs = results.get('similar_pairs', [])
                        for i, pair in enumerate(similar_pairs[:5], 1):
                            response += f"{i}. Similarity: {pair.get('similarity_score', 0.0):.2f}\n"
                            response += f"   Paper 1: {pair.get('paper1', 'Untitled')}\n"
                            response += f"   Paper 2: {pair.get('paper2', 'Untitled')}\n\n"
                    
                    elif analysis_type == 'trend_analysis':
                        trends = results.get('trends', [])
                        response += "Publication trends by year:\n"
                        for trend in trends:
                            response += f"  {trend.get('year', 'Unknown')}: {trend.get('count', 0)} papers\n"
                
                return {'agent_type': 'tensorflow', 'response': response}
            
            else:
                # General response using OpenAI
                prompt = f"The user asked: {query_text}\n\nRespond helpfully in the context of a research assistant."
                general_response = self.openai_service.generate_text(prompt)
                
                return {'agent_type': 'general', 'response': general_response}
        
        except Exception as e:
            logger.error(f"Error handling chat query: {e}")
            return {
                'agent_type': 'error',
                'response': f"I encountered an error while processing your query: {str(e)}"
            }
    
    def generate_hypothesis(self, research_question: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a hypothesis based on a research question and papers
        
        Args:
            research_question (str): The research question
            papers (list): List of papers
            
        Returns:
            dict: Generated hypothesis
        """
        try:
            return self.hypothesis_agent.generate_hypothesis(research_question, papers)
        except Exception as e:
            logger.error(f"Error generating hypothesis: {e}")
            return {
                'hypothesis': f"Error generating hypothesis: {str(e)}",
                'reasoning': 'An error occurred during hypothesis generation.',
                'confidence_score': 0.0
            }
    
    def analyze_with_tensorflow(self, project_id: int, analysis_type: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze papers with TensorFlow
        
        Args:
            project_id (int): ID of the research project
            analysis_type (str): Type of analysis to perform
            papers (list): List of papers to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            logger.info(f"Running TensorFlow analysis ({analysis_type}) for project {project_id}")
            return self.tensorflow_agent.analyze_papers(papers, analysis_type)
        except Exception as e:
            logger.error(f"Error in TensorFlow analysis: {e}")
            return {
                'error': f"Analysis failed: {str(e)}",
                'analysis_type': analysis_type
            }
    
    def _classify_query(self, query_text: str) -> Dict[str, Any]:
        """
        Classify the type of query to route to the appropriate agent
        
        Args:
            query_text (str): The user's query text
            
        Returns:
            dict: Query type and agent type
        """
        # Search for paper retrieval queries
        lower_query = query_text.lower()
        
        # Check if it's a data retrieval query
        if any(term in lower_query for term in ['find papers', 'search for', 'papers about', 'articles on']):
            # Extract the search query
            search_query = query_text
            for prefix in ['find papers', 'search for', 'papers about', 'articles on']:
                if prefix in lower_query:
                    search_query = query_text.split(prefix, 1)[1].strip()
                    break
            
            return {
                'agent_type': 'data_retrieval',
                'search_query': search_query
            }
        
        # Check if it's a summarization query
        elif any(term in lower_query for term in ['summarize', 'summary of', 'explain paper']):
            # Extract the paper reference
            paper_ref = query_text
            for prefix in ['summarize', 'summary of', 'explain paper']:
                if prefix in lower_query:
                    paper_ref = query_text.split(prefix, 1)[1].strip()
                    break
            
            return {
                'agent_type': 'summarization',
                'paper_reference': paper_ref
            }
        
        # Check if it's a hypothesis generation query
        elif any(term in lower_query for term in ['generate hypothesis', 'create hypothesis', 'hypothesis for']):
            # Extract the research question
            research_question = query_text
            for prefix in ['generate hypothesis', 'create hypothesis', 'hypothesis for']:
                if prefix in lower_query:
                    research_question = query_text.split(prefix, 1)[1].strip()
                    break
            
            return {
                'agent_type': 'hypothesis',
                'research_question': research_question
            }
        
        # Check if it's an experiment design query
        elif any(term in lower_query for term in ['design experiment', 'create experiment', 'experiment for']):
            # Extract the hypothesis
            hypothesis = query_text
            for prefix in ['design experiment', 'create experiment', 'experiment for']:
                if prefix in lower_query:
                    hypothesis = query_text.split(prefix, 1)[1].strip()
                    break
            
            return {
                'agent_type': 'experiment',
                'hypothesis': hypothesis
            }
        
        # Check if it's a TensorFlow analysis query
        elif any(term in lower_query for term in ['analyze with tensorflow', 'tensorflow analysis', 'cluster papers']):
            analysis_type = 'clustering'  # Default
            
            # Determine analysis type
            if 'topic' in lower_query or 'themes' in lower_query:
                analysis_type = 'topic_modeling'
            elif 'similar' in lower_query or 'similarity' in lower_query:
                analysis_type = 'similarity'
            elif 'trend' in lower_query or 'over time' in lower_query:
                analysis_type = 'trend_analysis'
            
            return {
                'agent_type': 'tensorflow',
                'analysis_type': analysis_type,
                'analysis_needed': True
            }
        
        # General query analysis
        else:
            # Analyze if the query might need TensorFlow analysis
            needs_analysis = any(term in lower_query for term in [
                'analyze', 'group', 'cluster', 'compare', 'trends', 'patterns', 'similarity'
            ])
            
            return {
                'agent_type': 'general',
                'analysis_needed': needs_analysis,
                'analysis_type': 'clustering' if needs_analysis else None
            }