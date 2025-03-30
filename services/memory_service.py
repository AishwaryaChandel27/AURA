"""
Memory Service for AURA Research Assistant
"""

import logging
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for storing and retrieving memory in a vector database
    """
    
    def __init__(self):
        """Initialize the MemoryService"""
        logger.info("Initializing MemoryService")
        
        # For demo purposes, use a simple dictionary to store memories
        # In a production environment, this would use a vector database like ChromaDB or Pinecone
        self.memories = {}
    
    def store_memory(self, memory_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory
        
        Args:
            memory_type (str): Type of memory (e.g., 'paper', 'hypothesis', 'experiment')
            content (str): The memory content
            metadata (dict, optional): Additional metadata about the memory
            
        Returns:
            str: Memory ID
        """
        # Generate a simple memory ID
        import random
        import string
        memory_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Store the memory
        self.memories[memory_id] = {
            'type': memory_type,
            'content': content,
            'metadata': metadata or {}
        }
        
        return memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by ID
        
        Args:
            memory_id (str): The memory ID
            
        Returns:
            dict or None: The memory if found, None otherwise
        """
        return self.memories.get(memory_id)
    
    def search_similar(self, query: str, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar memories
        
        Args:
            query (str): The search query
            memory_type (str, optional): Filter by memory type
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of similar memories
        """
        # For demo purposes, just do a simple text match
        # In a production environment, this would use vector embeddings and similarity search
        
        query_lower = query.lower()
        results = []
        
        for memory_id, memory in self.memories.items():
            if memory_type and memory['type'] != memory_type:
                continue
            
            content_lower = memory['content'].lower()
            if query_lower in content_lower:
                # Calculate a simple similarity score
                similarity = content_lower.count(query_lower) / len(content_lower)
                
                results.append({
                    'id': memory_id,
                    'memory': memory,
                    'similarity': similarity
                })
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]