"""
Semantic Scholar Service for AURA Research Assistant
"""

import logging
import json
import random
from typing import List, Dict, Any
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class SemanticScholarService:
    """
    Service for retrieving papers from Semantic Scholar
    """
    
    def __init__(self):
        """Initialize the SemanticScholarService"""
        logger.info("Initializing SemanticScholarService")
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers on Semantic Scholar
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            # For demo purposes, return sample papers that match the query
            # In a production environment, this would use the actual Semantic Scholar API
            sample_papers = self._generate_sample_papers(query, max_results)
            
            return sample_papers
            
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []
    
    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific Semantic Scholar paper
        
        Args:
            paper_id (str): The Semantic Scholar ID of the paper
            
        Returns:
            dict: Paper details
        """
        try:
            # For demo purposes, return a sample paper
            # In a production environment, this would use the actual Semantic Scholar API
            return {
                "title": f"Sample Paper with ID {paper_id}",
                "authors": self._generate_sample_authors(3),
                "abstract": "This is a sample abstract for a paper retrieved from Semantic Scholar.",
                "url": f"https://www.semanticscholar.org/paper/{paper_id}",
                "published_date": "2024-02-20",
                "source": "semantic_scholar",
                "external_id": paper_id,
                "citation_count": random.randint(5, 100),
                "reference_count": random.randint(10, 50)
            }
            
        except Exception as e:
            logger.error(f"Error getting paper details from Semantic Scholar: {e}")
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
        domains = ["healthcare", "finance", "education", "robotics", 
                   "climate", "transportation", "entertainment", "security"]
        
        ml_concepts = ["neural networks", "transformers", "reinforcement learning", 
                       "computer vision", "natural language processing", "deep learning"]
        
        # Find relevant domain and concept from query
        relevant_domain = None
        for domain in domains:
            if domain.lower() in query.lower():
                relevant_domain = domain
                break
        
        if not relevant_domain:
            relevant_domain = random.choice(domains)
        
        relevant_concept = None
        for concept in ml_concepts:
            if concept.lower() in query.lower():
                relevant_concept = concept
                break
        
        if not relevant_concept:
            relevant_concept = random.choice(ml_concepts)
        
        papers = []
        for i in range(max_results):
            # Generate a unique paper ID
            paper_id = f"ss-{random.randint(1000000, 9999999)}"
            
            # Vary titles based on query, domain, and concept
            title_options = [
                f"{relevant_concept.title()} for {relevant_domain.title()}: A Systematic Review",
                f"Survey of {query.title()} Applications in {relevant_domain.title()}",
                f"TensorFlow-based {relevant_concept.title()} Models for {relevant_domain.title()} Applications",
                f"Comparative Analysis of {relevant_concept.title()} Approaches in {relevant_domain.title()}",
                f"Towards Explainable {relevant_concept.title()} for {relevant_domain.title()} Research"
            ]
            
            title = title_options[i % len(title_options)]
            
            # Generate an abstract
            abstract = f"This paper provides a comprehensive review of {relevant_concept} applications " \
                      f"in {relevant_domain}. We analyze recent advances in using TensorFlow for " \
                      f"{query.lower()} and identify key research trends. Our analysis shows that " \
                      f"{relevant_concept} techniques can significantly improve performance in " \
                      f"{relevant_domain} applications, with potential for further optimizations."
            
            # Generate a realistic published date (within the last 3 years)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            year = random.choice([2022, 2023, 2024])
            published_date = f"{year}-{month:02d}-{day:02d}"
            
            # Add some Semantic Scholar specific metrics
            citation_count = random.randint(0, 150)
            reference_count = random.randint(15, 60)
            
            papers.append({
                "title": title,
                "authors": self._generate_sample_authors(random.randint(2, 5)),
                "abstract": abstract,
                "url": f"https://www.semanticscholar.org/paper/{paper_id}",
                "published_date": published_date,
                "source": "semantic_scholar",
                "external_id": paper_id,
                "citation_count": citation_count,
                "reference_count": reference_count,
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
        first_names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", 
                       "Hana", "Ivan", "Julia", "Kevin", "Linda", "Michael", "Nina", 
                       "Oscar", "Patricia", "Quincy", "Rachel", "Samuel", "Tina", 
                       "Uma", "Victor", "Wendy", "Xavier", "Yelena", "Zachary"]
        
        last_names = ["Anderson", "Brown", "Clark", "Davis", "Evans", "Foster", "Garcia", 
                      "Harris", "Ingram", "Johnson", "Khan", "Lee", "Miller", "Nguyen", 
                      "Okonkwo", "Patel", "Quinn", "Robinson", "Smith", "Thompson", "Ueda", 
                      "Vasquez", "Wilson", "Xu", "Young", "Zhang"]
        
        authors = []
        for _ in range(num_authors):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            authors.append({"name": f"{first_name} {last_name}"})
        
        return authors