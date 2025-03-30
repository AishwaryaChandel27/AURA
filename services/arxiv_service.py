"""
arXiv Service for AURA Research Assistant
Handles interactions with the arXiv API
"""

import logging
import random
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# Set up logging
logger = logging.getLogger(__name__)

class ArxivService:
    """
    Service for arXiv API interactions
    Provides methods to search and retrieve papers from arXiv
    
    Note: In a real implementation, this would use the arXiv API
    For this prototype, it generates sample data
    """
    
    def __init__(self):
        """Initialize ArxivService"""
        logger.info("Initializing ArxivService")
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for papers on arXiv
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            logger.info(f"Searching arXiv for '{query}', max_results={max_results}")
            
            # Mock data for prototype
            return self._generate_sample_papers(query, max_results)
            
            # In a real implementation, this would use the arXiv API
            # Example:
            # import arxiv
            # search = arxiv.Search(query=query, max_results=max_results)
            # results = list(search.results())
            # return self._parse_arxiv_results(results)
        
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []
    
    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """
        Get a specific paper from arXiv
        
        Args:
            paper_id (str): arXiv paper ID
            
        Returns:
            dict: Paper details
        """
        try:
            logger.info(f"Retrieving paper {paper_id} from arXiv")
            
            # Mock data for prototype
            return {
                'title': f"Sample Paper {paper_id}",
                'authors': self._generate_sample_authors(random.randint(1, 4)),
                'abstract': "This is a sample abstract for a paper from arXiv.",
                'url': f"https://arxiv.org/abs/{paper_id}",
                'pdf_url': f"https://arxiv.org/pdf/{paper_id}.pdf",
                'published_date': datetime.now().isoformat(),
                'source': 'arxiv',
                'external_id': paper_id
            }
            
            # In a real implementation, this would use the arXiv API
            # Example:
            # import arxiv
            # paper = next(arxiv.Search(id_list=[paper_id]).results())
            # return self._parse_arxiv_paper(paper)
        
        except Exception as e:
            logger.error(f"Error retrieving paper from arXiv: {e}")
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
            "Advances in {term} Research Using TensorFlow",
            "A Survey of {term} Methods with Deep Learning",
            "Towards Efficient {term} Models: A TensorFlow Approach",
            "{term} Analysis and Applications with Neural Networks",
            "Deep Learning for {term}: State of the Art",
            "Neural Network Approaches to {term} Classification",
            "TensorFlow Implementation for {term} Recognition",
            "Multi-Modal Learning for {term} Tasks",
            "Benchmark Datasets for {term} in Machine Learning",
            "Supervised Learning Techniques for {term} Prediction"
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
            
            # Generate arXiv ID format: YYMM.NNNNN
            year_month = pub_date.strftime("%y%m")
            id_number = random.randint(10000, 99999)
            arxiv_id = f"{year_month}.{id_number}"
            
            # Create a random paper
            paper = {
                'title': base_titles[i].format(term=term.capitalize()),
                'authors': self._generate_sample_authors(random.randint(1, 4)),
                'abstract': self._generate_sample_abstract(term),
                'url': f"https://arxiv.org/abs/{arxiv_id}",
                'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                'published_date': pub_date.isoformat(),
                'source': 'arxiv',
                'external_id': arxiv_id
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
        affiliations = ["University of Science", "Tech Institute", "Research University", 
                       "National Laboratory", "AI Research Center", "Data Science Institute"]
        
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
            if i > 0:  # Add some variation in affiliations
                affiliation += f" {random.choice(['Department of Computer Science', 'School of AI', 'Machine Learning Lab'])}"
            
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
            f"This paper presents a novel approach to {term} using deep learning techniques.",
            f"We propose a new method for addressing challenges in {term} research using TensorFlow.",
            f"In this work, we investigate the application of neural networks to {term} problems."
        ]
        
        methods = [
            f"Our methodology employs a convolutional neural network architecture to process {term} data.",
            f"We develop a TensorFlow-based framework for analyzing {term} patterns and trends.",
            f"The proposed approach leverages recurrent neural networks to model sequential aspects of {term}."
        ]
        
        experiments = [
            f"Experiments on benchmark {term} datasets demonstrate the effectiveness of our approach.",
            f"We evaluate our method on a diverse set of {term} tasks and compare with state-of-the-art techniques.",
            f"Our empirical analysis shows significant improvements over existing methods in {term} performance metrics."
        ]
        
        conclusions = [
            f"The results highlight the potential of deep learning for advancing {term} research.",
            f"Our findings contribute to the growing body of work on applying TensorFlow to {term} applications.",
            f"This work opens new directions for future research on {term} using machine learning techniques."
        ]
        
        # Randomly select one sentence from each category
        abstract = " ".join([
            random.choice(intros),
            random.choice(methods),
            random.choice(experiments),
            random.choice(conclusions)
        ])
        
        return abstract
    
    def _parse_arxiv_paper(self, paper) -> Dict[str, Any]:
        """
        Parse arXiv paper into standardized format
        
        Args:
            paper: arXiv paper object
            
        Returns:
            dict: Standardized paper dictionary
        """
        # This is a stub implementation
        # In a real implementation, this would parse actual arXiv API results
        return {
            'title': paper.title,
            'authors': [{'name': author.name, 'affiliation': author.affiliation} for author in paper.authors],
            'abstract': paper.summary,
            'url': paper.entry_id,
            'pdf_url': paper.pdf_url,
            'published_date': paper.published.isoformat() if hasattr(paper, 'published') else None,
            'source': 'arxiv',
            'external_id': self._extract_arxiv_id(paper.entry_id)
        }
    
    def _extract_arxiv_id(self, url: str) -> str:
        """
        Extract arXiv ID from URL
        
        Args:
            url (str): arXiv URL
            
        Returns:
            str: arXiv ID
        """
        if 'arxiv.org/abs/' in url:
            return url.split('arxiv.org/abs/')[-1]
        return url