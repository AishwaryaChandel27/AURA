"""
Summarization Agent for AURA Research Assistant
Agent responsible for summarizing research papers
"""

import logging
from typing import Dict, List, Any, Optional

# Import services
from services import openai_service

# Configure logging
logger = logging.getLogger(__name__)

class SummarizationAgent:
    """
    Agent responsible for summarizing research papers
    """
    
    def __init__(self):
        """Initialize the SummarizationAgent"""
        logger.info("Initializing SummarizationAgent")
        self.initialized = True
    
    def summarize_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary for a research paper
        
        Args:
            paper (dict): Paper information including title, authors, and abstract
            
        Returns:
            dict: Summary and key findings
        """
        logger.info(f"Summarizing paper: {paper.get('title', 'Unknown title')}")
        
        try:
            # Use OpenAI service to summarize
            summary_result = openai_service.summarize_paper(paper)
            
            return summary_result
        except Exception as e:
            logger.error(f"Error summarizing paper: {e}")
            return {
                'summary': f"Error generating summary for '{paper.get('title', 'unknown paper')}'.",
                'key_findings': []
            }
    
    def extract_key_points(self, text: str) -> List[str]:
        """
        Extract key points from a text
        
        Args:
            text (str): Text to extract key points from
            
        Returns:
            list: List of key points
        """
        logger.info("Extracting key points from text")
        
        try:
            # For a real implementation, this would use NLP techniques
            # or call an AI service to extract key points
            # For this demo, we'll just return a simple example
            
            # Split the text into sentences
            sentences = text.split('.')
            
            # Take the first few sentences as key points
            key_points = []
            for sentence in sentences[:3]:
                if len(sentence.strip()) > 10:  # Avoid very short sentences
                    key_points.append(sentence.strip() + '.')
            
            return key_points
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []