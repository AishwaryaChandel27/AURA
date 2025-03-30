import logging
from services.arxiv_service import ArxivService
from services.semantic_scholar_service import SemanticScholarService
from services.memory_service import MemoryService
from config import MAX_PAPERS_PER_QUERY

logger = logging.getLogger(__name__)

class DataRetrievalAgent:
    """
    Agent responsible for retrieving academic papers from various sources
    """
    
    def __init__(self):
        self.arxiv_service = ArxivService()
        self.semantic_scholar_service = SemanticScholarService()
        self.memory_service = MemoryService()
        self.max_papers = MAX_PAPERS_PER_QUERY
    
    def search_papers(self, query, max_results=None, sources=None):
        """
        Search for papers across multiple sources
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return
            sources (list, optional): List of sources to search ['arxiv', 'semantic_scholar']
        
        Returns:
            list: List of paper dictionaries
        """
        if max_results is None:
            max_results = self.max_papers
        
        if sources is None:
            sources = ['arxiv', 'semantic_scholar']
        
        papers = []
        
        # Calculate how many papers to retrieve from each source
        papers_per_source = max(1, max_results // len(sources))
        
        try:
            # Search ArXiv if requested
            if 'arxiv' in sources:
                logger.info(f"Searching ArXiv for: {query}")
                arxiv_papers = self.arxiv_service.search_papers(query, papers_per_source)
                papers.extend(arxiv_papers)
                logger.info(f"Found {len(arxiv_papers)} papers from ArXiv")
            
            # Search Semantic Scholar if requested
            if 'semantic_scholar' in sources:
                logger.info(f"Searching Semantic Scholar for: {query}")
                ss_papers = self.semantic_scholar_service.search_papers(query, papers_per_source)
                papers.extend(ss_papers)
                logger.info(f"Found {len(ss_papers)} papers from Semantic Scholar")
            
            # Truncate if we have more than max_results
            if len(papers) > max_results:
                papers = papers[:max_results]
            
            # Store papers in memory for future reference
            self._store_papers_in_memory(papers, query)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error in data retrieval agent search: {str(e)}")
            return []
    
    def get_paper_details(self, paper_id, source):
        """
        Get detailed information for a specific paper
        
        Args:
            paper_id (str): Paper ID
            source (str): Paper source ('arxiv' or 'semantic_scholar')
        
        Returns:
            dict: Paper details
        """
        try:
            paper = None
            
            if source == 'arxiv':
                paper = self.arxiv_service.get_paper_by_id(paper_id)
            elif source == 'semantic_scholar':
                paper = self.semantic_scholar_service.get_paper_by_id(paper_id)
            
            # Store in memory if found
            if paper:
                self._store_paper_in_memory(paper)
            
            return paper
            
        except Exception as e:
            logger.error(f"Error getting paper details: {str(e)}")
            return None
    
    def find_similar_papers(self, paper_id, max_results=5):
        """
        Find papers similar to a given paper
        
        Args:
            paper_id (str): Paper ID to find similar papers for
            max_results (int, optional): Maximum number of results to return
        
        Returns:
            list: List of similar papers
        """
        try:
            # First, try to get the paper from memory
            paper_doc = self.memory_service.get_document(paper_id)
            
            if not paper_doc:
                logger.warning(f"Paper {paper_id} not found in memory")
                return []
            
            # Get paper metadata
            paper_title = paper_doc['metadata'].get('title', '')
            paper_abstract = paper_doc['metadata'].get('abstract', '')
            
            # Create search query from title and abstract
            query = f"{paper_title} {paper_abstract[:200]}"
            
            # Search for similar papers
            similar_papers = self.memory_service.query(
                query_text=query,
                n_results=max_results + 1,  # Add 1 to filter out the original paper
                filter_criteria=None  # No specific filter
            )
            
            # Filter out the original paper
            similar_papers = [p for p in similar_papers if p['id'] != str(paper_id)]
            
            # Limit to max_results
            if len(similar_papers) > max_results:
                similar_papers = similar_papers[:max_results]
            
            return similar_papers
            
        except Exception as e:
            logger.error(f"Error finding similar papers: {str(e)}")
            return []
    
    def _store_papers_in_memory(self, papers, query):
        """
        Store papers in the vector memory for future reference
        
        Args:
            papers (list): List of paper dictionaries
            query (str): Original query used to find these papers
        """
        for paper in papers:
            self._store_paper_in_memory(paper, query)
    
    def _store_paper_in_memory(self, paper, query=None):
        """
        Store a single paper in the vector memory
        
        Args:
            paper (dict): Paper dictionary
            query (str, optional): Original query used to find this paper
        """
        try:
            # Create ID from source and external_id
            doc_id = f"{paper['source']}_{paper['external_id']}"
            
            # Create document text from title and abstract
            doc_text = f"Title: {paper['title']}\n\nAbstract: {paper['abstract']}"
            
            # Create metadata
            metadata = {
                'title': paper['title'],
                'authors': paper['authors'],
                'abstract': paper['abstract'],
                'url': paper['url'],
                'pdf_url': paper['pdf_url'],
                'source': paper['source'],
                'external_id': paper['external_id']
            }
            
            # Add publication date if available
            if paper.get('published_date'):
                metadata['published_date'] = paper['published_date'].isoformat()
            
            # Add original query if available
            if query:
                metadata['query'] = query
            
            # Add source-specific metadata
            if paper.get('metadata'):
                for key, value in paper['metadata'].items():
                    metadata[f"meta_{key}"] = value
            
            # Store in vector database
            self.memory_service.add_document(doc_id, doc_text, metadata)
            
        except Exception as e:
            logger.error(f"Error storing paper in memory: {str(e)}")
    
    def search_memory(self, query, max_results=5):
        """
        Search previously retrieved papers in memory
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return
        
        Returns:
            list: List of paper dictionaries
        """
        try:
            results = self.memory_service.query(
                query_text=query,
                n_results=max_results
            )
            
            papers = []
            
            for result in results:
                metadata = result['metadata']
                
                paper = {
                    'title': metadata.get('title', ''),
                    'authors': metadata.get('authors', []),
                    'abstract': metadata.get('abstract', ''),
                    'url': metadata.get('url', ''),
                    'pdf_url': metadata.get('pdf_url', ''),
                    'external_id': metadata.get('external_id', ''),
                    'source': metadata.get('source', ''),
                }
                
                # Add published date if available
                if metadata.get('published_date'):
                    try:
                        from datetime import datetime
                        paper['published_date'] = datetime.fromisoformat(metadata['published_date'])
                    except:
                        pass
                
                # Add relevance score
                paper['relevance_score'] = 1.0 - (result.get('distance', 0) or 0)
                
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            return []
