"""
arXiv Service for AURA Research Assistant
"""

import logging
import json
from typing import List, Dict, Any
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class ArxivService:
    """
    Service for retrieving papers from arXiv
    """
    
    def __init__(self):
        """Initialize the ArxivService"""
        logger.info("Initializing ArxivService")
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers on arXiv
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            # For demo purposes, return sample papers that match the query
            # In a production environment, this would use the actual arXiv API
            sample_papers = self._generate_sample_papers(query, max_results)
            
            return sample_papers
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []
    
    def get_paper_details(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific arXiv paper
        
        Args:
            arxiv_id (str): The arXiv ID of the paper
            
        Returns:
            dict: Paper details
        """
        try:
            # For demo purposes, return a sample paper
            # In a production environment, this would use the actual arXiv API
            return {
                "title": f"Sample Paper with ID {arxiv_id}",
                "authors": self._generate_sample_authors(3),
                "abstract": "This is a sample abstract for a paper retrieved from arXiv.",
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "published_date": "2024-03-15",
                "source": "arxiv",
                "external_id": arxiv_id
            }
            
        except Exception as e:
            logger.error(f"Error getting paper details from arXiv: {e}")
            return {}
    
    def _generate_sample_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Generate sample papers for demo purposes
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        topics = ["neural networks", "deep learning", "machine learning", 
                 "artificial intelligence", "computer vision", "natural language processing"]
        
        # Find the most relevant topic from the query
        relevant_topic = None
        for topic in topics:
            if topic.lower() in query.lower():
                relevant_topic = topic
                break
        
        if not relevant_topic:
            relevant_topic = "machine learning"  # Default topic
        
        papers = []
        for i in range(max_results):
            # Generate a sample paper with more realistic details
            paper_id = f"2403.{10000 + i:05d}"
            
            # Vary titles based on the query
            title_options = [
                f"Advances in {relevant_topic.title()} for {query.title()}",
                f"A Novel Approach to {query.title()} using {relevant_topic.title()}",
                f"{relevant_topic.title()}: Applications in {query.title()}",
                f"TensorFlow Implementations for {query.title()} Research",
                f"Improving {query.title()} with Deep Learning Techniques"
            ]
            
            title = title_options[i % len(title_options)]
            
            # Generate abstract with query and relevant topic
            abstract = f"This paper presents research on {query} using {relevant_topic} techniques. " \
                      f"We propose a novel approach that combines TensorFlow with specialized algorithms " \
                      f"to improve performance in {query.lower()} tasks. Our experimental results show " \
                      f"significant improvements over baseline methods in terms of accuracy and efficiency."
            
            # Generate a realistic published date (within the last 2 years)
            import random
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            year = random.choice([2023, 2024])
            published_date = f"{year}-{month:02d}-{day:02d}"
            
            papers.append({
                "title": title,
                "authors": self._generate_sample_authors(random.randint(2, 4)),
                "abstract": abstract,
                "url": f"https://arxiv.org/abs/{paper_id}",
                "pdf_url": f"https://arxiv.org/pdf/{paper_id}.pdf",
                "published_date": published_date,
                "source": "arxiv",
                "external_id": paper_id,
                "year": str(year)
            })
        
        return papers
    
    def _generate_sample_authors(self, num_authors: int) -> List[Dict[str, str]]:
        """
        Generate sample authors
        
        Args:
            num_authors (int): Number of authors to generate
            
        Returns:
            list: List of author dictionaries
        """
        first_names = ["Aisha", "Biyu", "Carlos", "Deepa", "Elena", "Fatima", "Gabriel", 
                       "Hiroshi", "Isabella", "Jun", "Kiran", "Layla", "Ming", "Nguyen", 
                       "Olga", "Priya", "Qiang", "Ravi", "Sonia", "Tao", "Umar", "Victoria", 
                       "Wei", "Xin", "Yasmin", "Zhen"]
        
        last_names = ["Ahmed", "Baryshnikov", "Chen", "Das", "Einarsson", "Feng", "Garcia", 
                      "Hansson", "Ivanova", "Jensen", "Kumar", "Li", "Martinez", "Nakamura", 
                      "Oliveira", "Park", "Qian", "Rodriguez", "Singh", "Tanaka", "Ueda", 
                      "Villanueva", "Wang", "Xu", "Yamamoto", "Zhang"]
        
        import random
        
        authors = []
        for _ in range(num_authors):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            authors.append({"name": f"{first_name} {last_name}"})
        
        return authors