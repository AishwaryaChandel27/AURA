import logging
import requests
from datetime import datetime
from config import SEMANTIC_SCHOLAR_API_URL, SEMANTIC_SCHOLAR_API_KEY, MAX_PAPERS_PER_QUERY

logger = logging.getLogger(__name__)

class SemanticScholarService:
    """
    Service for retrieving papers from the Semantic Scholar API
    """
    
    def __init__(self):
        self.base_url = SEMANTIC_SCHOLAR_API_URL
        self.api_key = SEMANTIC_SCHOLAR_API_KEY
        self.max_results = MAX_PAPERS_PER_QUERY
        self.headers = {
            'x-api-key': self.api_key
        } if self.api_key else {}
    
    def search_papers(self, query, max_results=None, fields=None):
        """
        Search for papers on Semantic Scholar
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return
            fields (list, optional): Fields to include in the response
        
        Returns:
            list: List of paper dictionaries
        """
        if max_results is None:
            max_results = self.max_results
        
        if fields is None:
            fields = ['paperId', 'title', 'abstract', 'authors', 'url', 'venue', 'year', 'citationCount', 'openAccessPdf']
        
        try:
            # Make the API request
            url = f"{self.base_url}/paper/search"
            
            params = {
                'query': query,
                'limit': max_results,
                'fields': ','.join(fields)
            }
            
            logger.debug(f"Semantic Scholar API request: {url} with params {params}")
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Semantic Scholar API error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            # Parse the results
            return self._parse_search_results(data)
            
        except Exception as e:
            logger.error(f"Error in Semantic Scholar search: {str(e)}")
            return []
    
    def _parse_search_results(self, data):
        """
        Parse the JSON response from Semantic Scholar API
        
        Args:
            data (dict): JSON response from Semantic Scholar
        
        Returns:
            list: List of paper dictionaries
        """
        try:
            papers = []
            
            for item in data.get('data', []):
                # Extract basic metadata
                paper_id = item.get('paperId')
                title = item.get('title', '')
                abstract = item.get('abstract', '')
                
                # Extract authors
                authors = []
                for author in item.get('authors', []):
                    authors.append(author.get('name', ''))
                
                # Extract URLs
                url = item.get('url')
                pdf_url = None
                if 'openAccessPdf' in item and item['openAccessPdf']:
                    pdf_url = item['openAccessPdf'].get('url')
                
                # Extract published date
                year = item.get('year')
                published_date = datetime(year, 1, 1) if year else None
                
                # Extract additional metadata
                venue = item.get('venue', '')
                citation_count = item.get('citationCount', 0)
                
                # Create paper dictionary
                paper = {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'url': url,
                    'pdf_url': pdf_url,
                    'published_date': published_date,
                    'external_id': paper_id,
                    'source': 'semantic_scholar',
                    'metadata': {
                        'venue': venue,
                        'citation_count': citation_count
                    }
                }
                
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error parsing Semantic Scholar response: {str(e)}")
            return []
    
    def get_paper_by_id(self, paper_id, fields=None):
        """
        Get a specific paper by Semantic Scholar ID
        
        Args:
            paper_id (str): Semantic Scholar paper ID
            fields (list, optional): Fields to include in the response
        
        Returns:
            dict: Paper information
        """
        if fields is None:
            fields = ['paperId', 'title', 'abstract', 'authors', 'url', 'venue', 
                      'year', 'citationCount', 'openAccessPdf', 'references', 'citations']
        
        try:
            # Make the API request
            url = f"{self.base_url}/paper/{paper_id}"
            
            params = {
                'fields': ','.join(fields)
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Semantic Scholar API error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            
            # Parse the results
            return self._parse_paper_details(data)
            
        except Exception as e:
            logger.error(f"Error in Semantic Scholar get_paper_by_id: {str(e)}")
            return None
    
    def _parse_paper_details(self, data):
        """
        Parse the JSON response for a single paper from Semantic Scholar API
        
        Args:
            data (dict): JSON response from Semantic Scholar
        
        Returns:
            dict: Paper information
        """
        try:
            # Extract basic metadata
            paper_id = data.get('paperId')
            title = data.get('title', '')
            abstract = data.get('abstract', '')
            
            # Extract authors
            authors = []
            for author in data.get('authors', []):
                authors.append(author.get('name', ''))
            
            # Extract URLs
            url = data.get('url')
            pdf_url = None
            if 'openAccessPdf' in data and data['openAccessPdf']:
                pdf_url = data['openAccessPdf'].get('url')
            
            # Extract published date
            year = data.get('year')
            published_date = datetime(year, 1, 1) if year else None
            
            # Extract additional metadata
            venue = data.get('venue', '')
            citation_count = data.get('citationCount', 0)
            
            # Extract references and citations
            references = []
            for ref in data.get('references', []):
                ref_paper = ref.get('citedPaper', {})
                references.append({
                    'id': ref_paper.get('paperId'),
                    'title': ref_paper.get('title', '')
                })
            
            citations = []
            for citation in data.get('citations', []):
                cite_paper = citation.get('citingPaper', {})
                citations.append({
                    'id': cite_paper.get('paperId'),
                    'title': cite_paper.get('title', '')
                })
            
            # Create paper dictionary
            paper = {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': url,
                'pdf_url': pdf_url,
                'published_date': published_date,
                'external_id': paper_id,
                'source': 'semantic_scholar',
                'metadata': {
                    'venue': venue,
                    'citation_count': citation_count,
                    'references': references,
                    'citations': citations
                }
            }
            
            return paper
            
        except Exception as e:
            logger.error(f"Error parsing Semantic Scholar paper details: {str(e)}")
            return None
