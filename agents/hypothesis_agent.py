"""
Hypothesis Agent for AURA Research Assistant
Agent responsible for generating research hypotheses
"""

import logging
from typing import Dict, List, Any, Optional

from services.openai_service import OpenAIService

# Set up logging
logger = logging.getLogger(__name__)

class HypothesisAgent:
    """
    Agent responsible for generating research hypotheses
    """
    
    def __init__(self):
        """Initialize the HypothesisAgent"""
        self.openai_service = OpenAIService()
    
    def generate_hypothesis(self, research_question: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a research hypothesis based on a research question and paper summaries
        
        Args:
            research_question (str): The research question
            papers (list): List of paper data
            
        Returns:
            dict: Generated hypothesis, reasoning, and confidence score
        """
        try:
            # Extract paper information
            paper_info = []
            for i, paper in enumerate(papers):
                paper_info.append({
                    'index': i,
                    'title': paper.get('title', ''),
                    'abstract': paper.get('abstract', '')
                })
            
            # Use the OpenAI service to generate a hypothesis
            hypothesis_data = self.openai_service.generate_hypothesis(research_question, paper_info)
            
            # Create supporting evidence
            supporting_evidence = {}
            if 'supporting_papers' in hypothesis_data:
                supporting_papers = hypothesis_data['supporting_papers']
                for paper_id, evidence in supporting_papers.items():
                    if isinstance(paper_id, str) and paper_id.isdigit():
                        paper_idx = int(paper_id)
                        if 0 <= paper_idx < len(papers):
                            supporting_evidence[paper_id] = {
                                'title': papers[paper_idx].get('title', ''),
                                'evidence': evidence
                            }
            
            return {
                'hypothesis': hypothesis_data.get('hypothesis', ''),
                'reasoning': hypothesis_data.get('reasoning', ''),
                'confidence_score': hypothesis_data.get('confidence_score', 0.0),
                'supporting_evidence': supporting_evidence
            }
        
        except Exception as e:
            logger.error(f"Error generating hypothesis: {e}")
            return {
                'hypothesis': f"Error generating hypothesis: {str(e)}",
                'reasoning': 'An error occurred during hypothesis generation.',
                'confidence_score': 0.0,
                'supporting_evidence': {}
            }
    
    def evaluate_hypothesis(self, hypothesis: Dict[str, Any], papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a hypothesis based on available papers
        
        Args:
            hypothesis (dict): The hypothesis to evaluate
            papers (list): List of paper data
            
        Returns:
            dict: Evaluation results
        """
        try:
            # Extract paper information
            paper_info = []
            for i, paper in enumerate(papers):
                paper_info.append({
                    'index': i,
                    'title': paper.get('title', ''),
                    'abstract': paper.get('abstract', '')
                })
            
            # Create evaluation prompt
            hypothesis_text = hypothesis.get('hypothesis', '')
            
            # Use the OpenAI service to evaluate the hypothesis
            evaluation = self.openai_service.evaluate_hypothesis(hypothesis_text, paper_info)
            
            return {
                'strength': evaluation.get('strength', 0.0),
                'weaknesses': evaluation.get('weaknesses', []),
                'alternative_hypotheses': evaluation.get('alternative_hypotheses', []),
                'suggestions': evaluation.get('suggestions', [])
            }
        
        except Exception as e:
            logger.error(f"Error evaluating hypothesis: {e}")
            return {
                'strength': 0.0,
                'weaknesses': [f"Error during evaluation: {str(e)}"],
                'alternative_hypotheses': [],
                'suggestions': ['Review the hypothesis and try again.']
            }