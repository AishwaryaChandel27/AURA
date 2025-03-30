"""
Data Retrieval Agent for AURA Research Assistant
Agent responsible for retrieving academic papers from various sources
"""

import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from services.arxiv_service import ArxivService
from services.semantic_scholar_service import SemanticScholarService

# Set up logging
logger = logging.getLogger(__name__)

class DataRetrievalAgent:
    """
    Agent responsible for retrieving research papers from various sources
    """
    
    def __init__(self):
        """Initialize the DataRetrievalAgent"""
        self.arxiv_service = ArxivService()
        self.semantic_scholar_service = SemanticScholarService()
    
    def search_papers(self, query: str, max_results: int = 10, sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for papers from various sources
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            sources (list, optional): List of sources to search (e.g., 'arxiv', 'semantic_scholar')
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            # Default sources if none provided
            if sources is None:
                sources = ['arxiv', 'semantic_scholar']
            
            # Temporary using mock data for development/testing
            papers = self._generate_sample_papers(query, max_results or 10)
            
            # Append source information
            for paper in papers:
                paper['source'] = random.choice(sources)
            
            return papers
        
        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            return []
    
    def retrieve_paper_details(self, paper_id: str, source: str) -> Dict[str, Any]:
        """
        Retrieve detailed information for a specific paper
        
        Args:
            paper_id (str): The ID of the paper
            source (str): The source of the paper (e.g., 'arxiv', 'semantic_scholar')
            
        Returns:
            dict: Paper details
        """
        try:
            if source == 'arxiv':
                return self.arxiv_service.get_paper(paper_id)
            elif source == 'semantic_scholar':
                return self.semantic_scholar_service.get_paper(paper_id)
            else:
                return {}
        
        except Exception as e:
            logger.error(f"Error retrieving paper details: {e}")
            return {}
    
    def _generate_sample_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Generate sample papers for testing (will be replaced with actual API calls)
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        papers = []
        
        # Create sample paper titles and authors based on the query
        query_terms = query.split()
        base_titles = [
            "Advances in {term} Research",
            "A Survey of {term} Methods",
            "Towards Efficient {term} Models",
            "{term} Analysis and Applications",
            "Deep Learning for {term}",
            "Neural Network Approaches to {term}",
            "Reinforcement Learning in {term} Domains",
            "Multi-Agent Systems for {term}",
            "Benchmark Datasets for {term}",
            "Supervised Learning Techniques for {term}"
        ]
        
        # Generate random base dates within the last 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        # Generate sample papers
        for i in range(min(max_results, len(base_titles))):
            term = random.choice(query_terms) if query_terms else "Research"
            
            # Create a random publication date
            days_diff = (end_date - start_date).days
            random_days = random.randint(0, days_diff)
            pub_date = start_date + timedelta(days=random_days)
            
            # Create a random paper
            paper = {
                'title': base_titles[i].format(term=term.capitalize()),
                'authors': self._generate_sample_authors(random.randint(1, 4)),
                'abstract': f"This paper presents a novel approach to {term}. "
                           f"We propose a new method for addressing challenges in {term} research. "
                           f"Our experiments show significant improvements over existing methods.",
                'url': f"https://example.org/papers/{i+1}",
                'pdf_url': f"https://example.org/papers/{i+1}/pdf",
                'published_date': pub_date.isoformat(),
                'external_id': f"paper_{i+1}"
            }
            
            papers.append(paper)
        
        return papers
    
    def _generate_sample_authors(self, num_authors: int) -> List[Dict[str, str]]:
        """Generate sample authors"""
        first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa"]
        last_names = ["Smith", "Johnson", "Brown", "Taylor", "Miller", "Wilson", "Moore", "Anderson"]
        
        authors = []
        for i in range(num_authors):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            authors.append({
                'name': f"{first_name} {last_name}",
                'affiliation': f"University of Research {i+1}"
            })
        
        return authors