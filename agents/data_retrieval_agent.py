"""
Data Retrieval Agent for AURA Research Assistant
Agent responsible for retrieving academic papers from various sources
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Import models (for database operations)
from app import db
from models import Paper, ResearchProject

# Configure logging
logger = logging.getLogger(__name__)

class DataRetrievalAgent:
    """
    Agent responsible for retrieving academic papers from various sources
    """
    
    def __init__(self):
        """Initialize the DataRetrievalAgent"""
        logger.info("Initializing DataRetrievalAgent")
        self.initialized = True
    
    def search_papers(self, query: str, max_results: Optional[int] = 10, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for papers across multiple sources
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return
            sources (list, optional): List of sources to search ['arxiv', 'semantic_scholar']
        
        Returns:
            list: List of paper dictionaries
        """
        logger.info(f"Searching for papers with query: {query}")
        
        # Default sources if not specified
        if not sources:
            sources = ['arxiv', 'semantic_scholar']
        
        # Initialize results
        results = []
        
        try:
            # For now, we'll use a simplified example
            # In a real implementation, we would connect to actual academic APIs
            # Simulated results for demonstration purposes
            simulated_results = [
                {
                    'id': 1,
                    'title': f"TensorFlow Application in {query} Research",
                    'authors': ['A. Researcher', 'B. Scientist'],
                    'abstract': f"This paper explores the application of TensorFlow in {query} research. We demonstrate how deep learning approaches can be used to solve complex problems in this domain.",
                    'url': 'https://example.com/paper1',
                    'pdf_url': 'https://example.com/paper1.pdf',
                    'published_date': datetime.now().isoformat(),
                    'source': 'arxiv',
                    'external_id': 'arxiv:2023.12345'
                },
                {
                    'id': 2,
                    'title': f"Advanced Neural Networks for {query}",
                    'authors': ['C. Engineer', 'D. Developer'],
                    'abstract': f"In this research, we present a novel neural network architecture designed specifically for {query} applications. Our approach demonstrates significant improvements over existing methods.",
                    'url': 'https://example.com/paper2',
                    'pdf_url': 'https://example.com/paper2.pdf',
                    'published_date': datetime.now().isoformat(),
                    'source': 'semantic_scholar',
                    'external_id': 'ss:98765'
                }
            ]
            
            # Add to results
            results.extend(simulated_results[:max_results])
            
            # Log results
            logger.info(f"Found {len(results)} papers for query: {query}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching for papers: {e}")
            return []
    
    def get_paper_details(self, paper_id: str, source: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific paper
        
        Args:
            paper_id (str): Paper ID
            source (str): Paper source ('arxiv' or 'semantic_scholar')
        
        Returns:
            dict: Paper details
        """
        logger.info(f"Getting paper details for {source}:{paper_id}")
        
        try:
            # Here we would connect to the appropriate API based on the source
            # For demonstration, return a template
            paper_details = {
                'id': paper_id,
                'title': f"Paper from {source}",
                'authors': ['Example Author'],
                'abstract': "This is an example paper abstract.",
                'url': f"https://example.com/{source}/{paper_id}",
                'pdf_url': f"https://example.com/{source}/{paper_id}.pdf",
                'published_date': datetime.now().isoformat(),
                'source': source,
                'external_id': f"{source}:{paper_id}"
            }
            
            return paper_details
        
        except Exception as e:
            logger.error(f"Error getting paper details: {e}")
            return {}
    
    def add_paper_to_project(self, paper_data: Dict[str, Any], project_id: int) -> Optional[int]:
        """
        Add a paper to a project
        
        Args:
            paper_data (dict): Paper data
            project_id (int): Project ID
        
        Returns:
            int: Paper ID
        """
        logger.info(f"Adding paper to project {project_id}: {paper_data.get('title', 'Unknown title')}")
        
        try:
            # Check if project exists
            project = ResearchProject.query.get(project_id)
            if not project:
                logger.error(f"Project {project_id} not found")
                return None
            
            # Check if paper with same external_id already exists in this project
            if 'external_id' in paper_data and paper_data['external_id']:
                existing_paper = Paper.query.filter_by(
                    project_id=project_id,
                    external_id=paper_data['external_id']
                ).first()
                
                if existing_paper:
                    logger.info(f"Paper with external_id {paper_data['external_id']} already exists in project {project_id}")
                    return existing_paper.id
            
            # Create new paper
            paper = Paper(
                title=paper_data.get('title', 'Unknown Title'),
                abstract=paper_data.get('abstract', ''),
                url=paper_data.get('url', ''),
                pdf_url=paper_data.get('pdf_url', ''),
                source=paper_data.get('source', 'manual'),
                external_id=paper_data.get('external_id', ''),
                project_id=project_id
            )
            
            # Set published date if provided
            if paper_data.get('published_date'):
                try:
                    if isinstance(paper_data['published_date'], str):
                        paper.published_date = datetime.fromisoformat(paper_data['published_date'])
                    else:
                        paper.published_date = paper_data['published_date']
                except (ValueError, TypeError):
                    pass
            
            # Set authors if provided
            if 'authors' in paper_data and hasattr(paper, 'set_authors'):
                paper.set_authors(paper_data['authors'])
            
            # Set metadata if provided
            if 'metadata' in paper_data and hasattr(paper, 'set_metadata'):
                paper.set_metadata(paper_data['metadata'])
            
            # Save to database
            db.session.add(paper)
            db.session.commit()
            
            logger.info(f"Added paper {paper.id} to project {project_id}")
            return paper.id
        
        except Exception as e:
            logger.error(f"Error adding paper to project: {e}")
            db.session.rollback()
            return None
    
    def search_memory(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search previously retrieved papers in memory
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return
        
        Returns:
            list: List of paper dictionaries
        """
        logger.info(f"Searching memory for query: {query}")
        
        try:
            # In a production system, this would use a vector database or similar
            # For this demo, we'll just do a basic keyword search in the database
            
            # Search in titles and abstracts
            keyword = f"%{query}%"
            papers = Paper.query.filter(
                (Paper.title.like(keyword)) | (Paper.abstract.like(keyword))
            ).limit(max_results).all()
            
            # Convert to dictionaries
            results = []
            for paper in papers:
                paper_dict = {
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'url': paper.url,
                    'pdf_url': paper.pdf_url,
                    'source': paper.source,
                    'external_id': paper.external_id
                }
                
                # Add authors if available
                if hasattr(paper, 'get_authors'):
                    paper_dict['authors'] = paper.get_authors()
                
                # Add published date if available
                if paper.published_date:
                    paper_dict['published_date'] = paper.published_date.isoformat()
                
                results.append(paper_dict)
            
            logger.info(f"Found {len(results)} papers in memory for query: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []