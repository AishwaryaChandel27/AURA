"""
Summarization Agent for AURA Research Assistant
Agent responsible for summarizing research papers
"""

import logging
from typing import Dict, List, Any

from services.openai_service import OpenAIService

# Set up logging
logger = logging.getLogger(__name__)

class SummarizationAgent:
    """
    Agent responsible for summarizing research papers
    """
    
    def __init__(self):
        """Initialize the SummarizationAgent"""
        self.openai_service = OpenAIService()
    
    def summarize_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary for a research paper
        
        Args:
            paper (dict): Paper information including title, authors, and abstract
            
        Returns:
            dict: Summary and key findings
        """
        try:
            # Extract paper details
            title = paper.get('title', 'Untitled Paper')
            authors = paper.get('authors', [])
            abstract = paper.get('abstract', '')
            
            # Format author information
            if authors:
                if isinstance(authors[0], dict):
                    author_names = [a.get('name', '') for a in authors]
                    author_text = ', '.join(author_names)
                else:
                    author_text = ', '.join(authors)
            else:
                author_text = 'Unknown'
            
            # Create a text to summarize
            text_to_summarize = f"Title: {title}\nAuthors: {author_text}\n\nAbstract: {abstract}"
            
            # Get summary from OpenAI
            summary = self.openai_service.summarize_text(text_to_summarize)
            
            # Extract key points
            key_points = self.extract_key_points(summary)
            
            return {
                'title': title,
                'authors': author_text,
                'summary': summary,
                'key_findings': key_points
            }
        
        except Exception as e:
            logger.error(f"Error summarizing paper: {e}")
            return {
                'title': paper.get('title', 'Untitled Paper'),
                'authors': 'Error retrieving authors',
                'summary': f"Error generating summary: {str(e)}",
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
        try:
            # Use OpenAI service to extract key points
            key_points = self.openai_service.extract_key_points(text)
            
            # Ensure key_points is a list
            if isinstance(key_points, list):
                return key_points
            else:
                # If it's not a list, try to extract list items from text
                # This is a fallback in case the OpenAI response format is unexpected
                lines = text.split('\n')
                points = []
                
                for line in lines:
                    line = line.strip()
                    # Look for numbered or bulleted items
                    if line and (line[0].isdigit() or line[0] in ['•', '-', '*']):
                        # Remove the bullet or number
                        clean_line = line.lstrip('0123456789.-*• \t')
                        if clean_line:
                            points.append(clean_line)
                
                return points if points else [text[:100] + '...']
        
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return ["Error extracting key points."]