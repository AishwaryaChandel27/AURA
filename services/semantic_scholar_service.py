"""
Semantic Scholar Service for AURA Research Assistant
Handles interactions with the Semantic Scholar API
"""

import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

class SemanticScholarService:
    """
    Service for Semantic Scholar API interactions
    Provides methods to search and retrieve papers from Semantic Scholar
    
    Note: In a real implementation, this would use the Semantic Scholar API
    For this prototype, it generates sample data
    """
    
    def __init__(self):
        """Initialize SemanticScholarService"""
        logger.info("Initializing SemanticScholarService")
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for papers on Semantic Scholar
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            logger.info(f"Searching Semantic Scholar for '{query}', max_results={max_results}")
            
            # Mock data for prototype
            return self._generate_sample_papers(query, max_results)
            
            # In a real implementation, this would use the Semantic Scholar API
            # Example:
            # import requests
            # url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={max_results}"
            # response = requests.get(url)
            # results = response.json().get('data', [])
            # return self._parse_semantic_scholar_results(results)
        
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []
    
    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """
        Get a specific paper from Semantic Scholar
        
        Args:
            paper_id (str): Semantic Scholar paper ID
            
        Returns:
            dict: Paper details
        """
        try:
            logger.info(f"Retrieving paper {paper_id} from Semantic Scholar")
            
            # Mock data for prototype
            return {
                'title': f"Sample Semantic Scholar Paper {paper_id}",
                'authors': self._generate_sample_authors(random.randint(1, 4)),
                'abstract': "This is a sample abstract for a paper from Semantic Scholar.",
                'url': f"https://www.semanticscholar.org/paper/{paper_id}",
                'pdf_url': f"https://www.semanticscholar.org/paper/{paper_id}.pdf",
                'published_date': datetime.now().isoformat(),
                'source': 'semantic_scholar',
                'external_id': paper_id
            }
            
            # In a real implementation, this would use the Semantic Scholar API
            # Example:
            # import requests
            # url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
            # response = requests.get(url)
            # return self._parse_semantic_scholar_paper(response.json())
        
        except Exception as e:
            logger.error(f"Error retrieving paper from Semantic Scholar: {e}")
            return {}
    
    def _generate_sample_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Generate sample papers for testing
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of papers to generate
            
        Returns:
            list: List of paper dictionaries
        """
        papers = []
        
        # Create sample paper titles and authors based on the query
        query_terms = query.split() if query else ["research"]
        base_titles = [
            "Machine Learning Approach to {term}: A Comprehensive Study",
            "Deep Neural Networks for {term} Classification and Analysis",
            "TensorFlow Framework for {term} Processing",
            "Comparative Analysis of {term} Models with Deep Learning",
            "Artificial Intelligence in {term}: Current Trends and Future Directions",
            "A Review of Recent Advances in {term} Research",
            "Transfer Learning for {term} Applications",
            "Self-Supervised Learning in {term} Domain",
            "Graph Neural Networks for {term} Problems",
            "Attention Mechanisms in {term} Models"
        ]
        
        # Generate random base dates within the last 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        # Generate sample papers
        for i in range(min(max_results, len(base_titles))):
            term = random.choice(query_terms)
            
            # Create a random publication date
            days_diff = (end_date - start_date).days
            random_days = random.randint(0, days_diff)
            pub_date = start_date + timedelta(days=random_days)
            
            # Generate Semantic Scholar ID format (random alphanumeric)
            id_chars = "0123456789abcdef"
            scholar_id = ''.join(random.choice(id_chars) for _ in range(16))
            
            # Create a random paper
            paper = {
                'title': base_titles[i].format(term=term.capitalize()),
                'authors': self._generate_sample_authors(random.randint(1, 5)),
                'abstract': self._generate_sample_abstract(term),
                'url': f"https://www.semanticscholar.org/paper/{scholar_id}",
                'pdf_url': f"https://www.semanticscholar.org/paper/{scholar_id}.pdf",
                'published_date': pub_date.isoformat(),
                'source': 'semantic_scholar',
                'external_id': scholar_id
            }
            
            papers.append(paper)
        
        return papers
    
    def _generate_sample_authors(self, num_authors: int) -> List[Dict[str, str]]:
        """
        Generate sample authors
        
        Args:
            num_authors (int): Number of authors to generate
            
        Returns:
            list: List of author dictionaries
        """
        first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa", "Wei", 
                      "Ying", "Raj", "Priya", "Carlos", "Maria", "Hiroshi", "Yuki"]
        last_names = ["Smith", "Johnson", "Chen", "Wang", "Patel", "Singh", "Garcia", "Rodriguez", 
                     "Tanaka", "Suzuki", "Kim", "Park", "Nguyen", "Tran", "Mueller", "Schmidt"]
        affiliations = ["Stanford University", "MIT", "UC Berkeley", "Harvard University", 
                       "Google Research", "Microsoft Research", "DeepMind", "OpenAI"]
        
        authors = []
        used_names = set()  # To avoid duplicates
        
        for i in range(num_authors):
            # Generate unique name
            while True:
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                full_name = f"{first_name} {last_name}"
                
                if full_name not in used_names:
                    used_names.add(full_name)
                    break
            
            # Generate random affiliation
            affiliation = random.choice(affiliations)
            
            authors.append({
                'name': full_name,
                'affiliation': affiliation
            })
        
        return authors
    
    def _generate_sample_abstract(self, term: str) -> str:
        """
        Generate a sample abstract based on a search term
        
        Args:
            term (str): Search term
            
        Returns:
            str: Generated abstract
        """
        # Set of templates for different parts of the abstract
        intros = [
            f"In this paper, we address the challenges of {term} using machine learning techniques.",
            f"We present a novel approach to {term} based on deep neural networks.",
            f"This work explores the application of artificial intelligence to {term} problems."
        ]
        
        methods = [
            f"Our methodology combines TensorFlow with specialized {term} processing algorithms.",
            f"We develop a hybrid architecture that integrates multiple neural networks for {term} analysis.",
            f"The proposed framework applies transfer learning to improve {term} performance metrics."
        ]
        
        experiments = [
            f"We evaluate our approach on benchmark {term} datasets and compare with state-of-the-art methods.",
            f"Experimental results demonstrate significant improvements in {term} accuracy and efficiency.",
            f"Our system outperforms existing {term} solutions across multiple evaluation metrics."
        ]
        
        conclusions = [
            f"This research contributes to the growing field of AI-powered {term} systems.",
            f"Our findings have important implications for future {term} research and applications.",
            f"We conclude that deep learning offers promising solutions for {term} challenges."
        ]
        
        # Randomly select one sentence from each category
        abstract = " ".join([
            random.choice(intros),
            random.choice(methods),
            random.choice(experiments),
            random.choice(conclusions)
        ])
        
        return abstract
    
    def _parse_semantic_scholar_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse Semantic Scholar results into standardized format
        
        Args:
            results (list): List of result objects from Semantic Scholar API
            
        Returns:
            list: List of standardized paper dictionaries
        """
        # This is a stub implementation
        # In a real implementation, this would parse actual Semantic Scholar API results
        papers = []
        
        for result in results:
            paper = {
                'title': result.get('title', ''),
                'authors': [{'name': a.get('name', ''), 'affiliation': a.get('affiliations', [''])[0]} 
                           for a in result.get('authors', [])],
                'abstract': result.get('abstract', ''),
                'url': result.get('url', ''),
                'pdf_url': result.get('pdfUrl', ''),
                'published_date': result.get('year', ''),
                'source': 'semantic_scholar',
                'external_id': result.get('paperId', '')
            }
            
            papers.append(paper)
        
        return papers