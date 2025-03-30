"""
ArXiv service for AURA Research Assistant
Handles interactions with the ArXiv API
"""

import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# ArXiv API constants
ARXIV_API_URL = "http://export.arxiv.org/api/query"

def search_papers(query, max_results=10):
    """
    Search for papers on ArXiv
    
    Args:
        query (str): Search query
        max_results (int, optional): Maximum number of results to return
    
    Returns:
        list: List of paper dictionaries
    """
    try:
        # Format query parameters
        params = {
            'search_query': query,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        # Build query URL
        query_url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
        
        # Make request
        with urllib.request.urlopen(query_url) as response:
            response_text = response.read().decode('utf-8')
        
        # Parse XML response
        return _parse_arxiv_response(response_text)
    
    except Exception as e:
        logger.error(f"Error searching ArXiv: {e}")
        return []

def get_paper_by_id(paper_id):
    """
    Get a paper from ArXiv by ID
    
    Args:
        paper_id (str): ArXiv paper ID
    
    Returns:
        dict: Paper information
    """
    try:
        # Format query parameters
        params = {
            'id_list': paper_id
        }
        
        # Build query URL
        query_url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
        
        # Make request
        with urllib.request.urlopen(query_url) as response:
            response_text = response.read().decode('utf-8')
        
        # Parse XML response
        papers = _parse_arxiv_response(response_text)
        
        # Return first (should be only) paper
        if papers:
            return papers[0]
        else:
            return None
    
    except Exception as e:
        logger.error(f"Error getting ArXiv paper {paper_id}: {e}")
        return None

def _parse_arxiv_response(response_text):
    """
    Parse ArXiv API XML response
    
    Args:
        response_text (str): XML response text
    
    Returns:
        list: List of paper dictionaries
    """
    # Parse XML
    root = ET.fromstring(response_text)
    
    # Define namespace
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    # Extract papers
    papers = []
    
    for entry in root.findall('atom:entry', ns):
        # Skip the first entry if it's the opensearch description
        if entry.find('atom:title', ns).text == 'ArXiv Query:':
            continue
        
        # Extract paper information
        paper = {
            'title': entry.find('atom:title', ns).text.strip(),
            'abstract': entry.find('atom:summary', ns).text.strip(),
            'url': entry.find('atom:id', ns).text,
            'published_date': None,
            'authors': [],
            'source': 'arxiv',
            'external_id': None,
            'pdf_url': None
        }
        
        # Extract authors
        authors = entry.findall('atom:author', ns)
        paper['authors'] = [author.find('atom:name', ns).text for author in authors]
        
        # Extract published date
        published = entry.find('atom:published', ns)
        if published is not None and published.text:
            try:
                published_date = datetime.strptime(published.text, '%Y-%m-%dT%H:%M:%SZ')
                paper['published_date'] = published_date.strftime('%Y-%m-%d')
            except Exception:
                pass
        
        # Extract ArXiv ID (from URL)
        id_url = entry.find('atom:id', ns).text
        if 'arxiv.org/abs/' in id_url:
            paper['external_id'] = id_url.split('arxiv.org/abs/')[1]
        
        # Add PDF URL
        if paper['external_id']:
            paper['pdf_url'] = f"http://arxiv.org/pdf/{paper['external_id']}"
        
        # Add paper to results
        papers.append(paper)
    
    return papers