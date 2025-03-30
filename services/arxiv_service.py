import logging
import urllib.parse
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from config import ARXIV_API_URL, MAX_PAPERS_PER_QUERY

logger = logging.getLogger(__name__)

class ArxivService:
    """
    Service for retrieving papers from the ArXiv API
    """
    
    def __init__(self):
        self.base_url = ARXIV_API_URL
        self.max_results = MAX_PAPERS_PER_QUERY
    
    def search_papers(self, query, max_results=None):
        """
        Search for papers on ArXiv
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return
        
        Returns:
            list: List of paper dictionaries
        """
        if max_results is None:
            max_results = self.max_results
        
        try:
            # Encode the query parameters
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            encoded_params = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{encoded_params}"
            
            logger.debug(f"ArXiv API request: {url}")
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"ArXiv API error: {response.status_code} - {response.text}")
                return []
            
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Error in ArXiv search: {str(e)}")
            return []
    
    def _parse_response(self, response_text):
        """
        Parse the XML response from ArXiv API
        
        Args:
            response_text (str): XML response from ArXiv
        
        Returns:
            list: List of paper dictionaries
        """
        try:
            # Parse XML response
            root = ET.fromstring(response_text)
            
            # Define namespace map
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            
            # Extract entries (papers)
            entries = root.findall('.//atom:entry', ns)
            
            for entry in entries:
                # Extract basic metadata
                title = entry.find('./atom:title', ns).text.strip()
                abstract = entry.find('./atom:summary', ns).text.strip()
                
                # Extract authors
                authors = []
                author_elements = entry.findall('./atom:author/atom:name', ns)
                for author_element in author_elements:
                    authors.append(author_element.text)
                
                # Extract links
                links = entry.findall('./atom:link', ns)
                url = next((link.get('href') for link in links if link.get('rel') == 'alternate')), None
                pdf_url = next((link.get('href') for link in links if link.get('title') == 'pdf')), None
                
                # Extract published date
                published_text = entry.find('./atom:published', ns).text
                published_date = datetime.strptime(published_text, '%Y-%m-%dT%H:%M:%SZ')
                
                # Extract ArXiv ID
                id_url = entry.find('./atom:id', ns).text
                arxiv_id = id_url.split('/abs/')[-1]
                
                # Extract categories/tags
                categories = []
                category_elements = entry.findall('./arxiv:primary_category', ns)
                for cat in category_elements:
                    categories.append(cat.get('term'))
                
                # Create paper dictionary
                paper = {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'url': url,
                    'pdf_url': pdf_url,
                    'published_date': published_date,
                    'external_id': arxiv_id,
                    'source': 'arxiv',
                    'metadata': {
                        'categories': categories
                    }
                }
                
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error parsing ArXiv response: {str(e)}")
            return []
    
    def get_paper_by_id(self, arxiv_id):
        """
        Get a specific paper by ArXiv ID
        
        Args:
            arxiv_id (str): ArXiv paper ID
        
        Returns:
            dict: Paper information
        """
        try:
            params = {
                'id_list': arxiv_id
            }
            
            encoded_params = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{encoded_params}"
            
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"ArXiv API error: {response.status_code} - {response.text}")
                return None
            
            papers = self._parse_response(response.text)
            
            if not papers:
                return None
                
            return papers[0]
            
        except Exception as e:
            logger.error(f"Error in ArXiv get_paper_by_id: {str(e)}")
            return None
