"""
Memory Service for AURA Research Assistant
Handles long-term storage and retrieval of research data
"""

import logging
from typing import Dict, List, Any, Optional
import json

# Set up logging
logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for managing long-term memory of research projects
    
    In a real implementation, this would use a vector database like Chroma or Pinecone
    For this prototype, it provides basic memory functionality
    """
    
    def __init__(self):
        """Initialize MemoryService"""
        logger.info("Initializing MemoryService")
        self.memory_store = {}  # Project ID -> memory items
    
    def add_memory_item(self, project_id: int, item_type: str, item: Dict[str, Any]) -> str:
        """
        Add an item to memory
        
        Args:
            project_id (int): Project ID
            item_type (str): Type of item (paper, hypothesis, experiment, etc.)
            item (dict): Item data
            
        Returns:
            str: Item ID
        """
        try:
            # Create project entry if it doesn't exist
            if project_id not in self.memory_store:
                self.memory_store[project_id] = {
                    'papers': {},
                    'hypotheses': {},
                    'experiments': {},
                    'queries': {},
                    'chat': []
                }
            
            # Get item ID
            item_id = item.get('id')
            
            # Add to appropriate collection
            if item_type == 'paper':
                self.memory_store[project_id]['papers'][item_id] = item
            elif item_type == 'hypothesis':
                self.memory_store[project_id]['hypotheses'][item_id] = item
            elif item_type == 'experiment':
                self.memory_store[project_id]['experiments'][item_id] = item
            elif item_type == 'query':
                self.memory_store[project_id]['queries'][item_id] = item
            elif item_type == 'chat':
                self.memory_store[project_id]['chat'].append(item)
            
            logger.info(f"Added {item_type} {item_id} to memory for project {project_id}")
            return item_id
        
        except Exception as e:
            logger.error(f"Error adding memory item: {e}")
            return ""
    
    def get_memory_item(self, project_id: int, item_type: str, item_id: str) -> Dict[str, Any]:
        """
        Get an item from memory
        
        Args:
            project_id (int): Project ID
            item_type (str): Type of item
            item_id (str): Item ID
            
        Returns:
            dict: Item data
        """
        try:
            if project_id not in self.memory_store:
                return {}
            
            if item_type == 'paper':
                return self.memory_store[project_id]['papers'].get(item_id, {})
            elif item_type == 'hypothesis':
                return self.memory_store[project_id]['hypotheses'].get(item_id, {})
            elif item_type == 'experiment':
                return self.memory_store[project_id]['experiments'].get(item_id, {})
            elif item_type == 'query':
                return self.memory_store[project_id]['queries'].get(item_id, {})
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting memory item: {e}")
            return {}
    
    def search_memory(self, project_id: int, query: str, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search memory for items related to a query
        
        Args:
            project_id (int): Project ID
            query (str): Search query
            item_type (str, optional): Type of item to search for
            
        Returns:
            list: List of matching items
        """
        try:
            if project_id not in self.memory_store:
                return []
            
            results = []
            
            # In a real implementation, this would use vector similarity search
            # For this prototype, it does a simple text search
            
            # Construct collection to search
            collections = {}
            if item_type == 'paper':
                collections = {'papers': self.memory_store[project_id]['papers']}
            elif item_type == 'hypothesis':
                collections = {'hypotheses': self.memory_store[project_id]['hypotheses']}
            elif item_type == 'experiment':
                collections = {'experiments': self.memory_store[project_id]['experiments']}
            elif item_type == 'query':
                collections = {'queries': self.memory_store[project_id]['queries']}
            else:
                collections = {
                    'papers': self.memory_store[project_id]['papers'],
                    'hypotheses': self.memory_store[project_id]['hypotheses'],
                    'experiments': self.memory_store[project_id]['experiments'],
                    'queries': self.memory_store[project_id]['queries']
                }
            
            # Search each collection
            query_terms = query.lower().split()
            for collection_name, collection in collections.items():
                for item_id, item in collection.items():
                    item_text = json.dumps(item).lower()
                    match_score = 0
                    
                    for term in query_terms:
                        if term in item_text:
                            match_score += 1
                    
                    if match_score > 0:
                        results.append({
                            'id': item_id,
                            'type': collection_name[:-1],  # Remove 's' from collection name
                            'score': match_score / len(query_terms),
                            'data': item
                        })
            
            # Sort by score (descending)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []
    
    def get_chat_history(self, project_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a project
        
        Args:
            project_id (int): Project ID
            limit (int): Maximum number of messages to return
            
        Returns:
            list: List of chat messages
        """
        try:
            if project_id not in self.memory_store:
                return []
            
            # Get chat history (most recent first)
            chat_history = list(reversed(self.memory_store[project_id]['chat']))
            
            # Limit the number of messages
            chat_history = chat_history[:limit]
            
            return chat_history
        
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    def clear_memory(self, project_id: int) -> bool:
        """
        Clear memory for a project
        
        Args:
            project_id (int): Project ID
            
        Returns:
            bool: Success flag
        """
        try:
            if project_id in self.memory_store:
                self.memory_store[project_id] = {
                    'papers': {},
                    'hypotheses': {},
                    'experiments': {},
                    'queries': {},
                    'chat': []
                }
                
                logger.info(f"Cleared memory for project {project_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False