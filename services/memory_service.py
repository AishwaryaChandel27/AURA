import os
import logging
import json
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from config import CHROMA_PERSIST_DIRECTORY, COLLECTION_NAME

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for storing and retrieving vector embeddings using ChromaDB
    """
    
    def __init__(self):
        # Create directories if they don't exist
        os.makedirs(CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            
            # Use OpenAI embedding function
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.environ.get("OPENAI_API_KEY"),
                model_name="text-embedding-ada-002"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {COLLECTION_NAME}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            # Create a fallback in-memory implementation if persistent storage fails
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.environ.get("OPENAI_API_KEY"),
                model_name="text-embedding-ada-002"
            )
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            logger.warning("Using in-memory ChromaDB as fallback")
    
    def add_document(self, doc_id, text, metadata=None):
        """
        Add a document to the vector store
        
        Args:
            doc_id (str): Unique document ID
            text (str): Document text to embed
            metadata (dict, optional): Metadata for the document
        
        Returns:
            bool: Success status
        """
        try:
            if metadata is None:
                metadata = {}
                
            # Convert any non-string metadata values to strings
            clean_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (dict, list)):
                    clean_metadata[k] = json.dumps(v)
                else:
                    clean_metadata[k] = str(v)
            
            self.collection.add(
                documents=[text],
                metadatas=[clean_metadata],
                ids=[str(doc_id)]
            )
            
            logger.debug(f"Added document {doc_id} to memory")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {str(e)}")
            return False
    
    def query(self, query_text, n_results=5, filter_criteria=None):
        """
        Query the vector store for similar documents
        
        Args:
            query_text (str): Query text
            n_results (int, optional): Number of results to return
            filter_criteria (dict, optional): Metadata filter criteria
        
        Returns:
            list: List of document dictionaries
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_criteria
            )
            
            # Process and format the results
            formatted_results = []
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    doc_id = results['ids'][0][i]
                    document = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                    distance = results['distances'][0][i] if 'distances' in results else None
                    
                    # Try to parse any JSON strings in metadata back to objects
                    for k, v in metadata.items():
                        if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
                            try:
                                metadata[k] = json.loads(v)
                            except json.JSONDecodeError:
                                pass
                    
                    formatted_results.append({
                        'id': doc_id,
                        'document': document,
                        'metadata': metadata,
                        'distance': distance
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            return []
    
    def get_document(self, doc_id):
        """
        Get a document by ID
        
        Args:
            doc_id (str): Document ID
        
        Returns:
            dict: Document with metadata or None
        """
        try:
            result = self.collection.get(ids=[str(doc_id)])
            
            if result and len(result['ids']) > 0:
                metadata = result['metadatas'][0] if 'metadatas' in result else {}
                
                # Try to parse any JSON strings in metadata back to objects
                for k, v in metadata.items():
                    if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
                        try:
                            metadata[k] = json.loads(v)
                        except json.JSONDecodeError:
                            pass
                
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': metadata
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting document from ChromaDB: {str(e)}")
            return None
    
    def update_document(self, doc_id, text=None, metadata=None):
        """
        Update a document in the vector store
        
        Args:
            doc_id (str): Document ID
            text (str, optional): New document text
            metadata (dict, optional): New or updated metadata
        
        Returns:
            bool: Success status
        """
        try:
            # Get current document if we're only updating part of it
            if (text is None or metadata is None) and not (text is None and metadata is None):
                current_doc = self.get_document(doc_id)
                if not current_doc:
                    return False
                
                if text is None:
                    text = current_doc['document']
                if metadata is None:
                    metadata = current_doc['metadata']
            
            # Convert any non-string metadata values to strings
            if metadata:
                clean_metadata = {}
                for k, v in metadata.items():
                    if isinstance(v, (dict, list)):
                        clean_metadata[k] = json.dumps(v)
                    else:
                        clean_metadata[k] = str(v)
                metadata = clean_metadata
            
            # Build update arguments
            update_args = {'ids': [str(doc_id)]}
            if text is not None:
                update_args['documents'] = [text]
            if metadata is not None:
                update_args['metadatas'] = [metadata]
            
            self.collection.update(**update_args)
            
            logger.debug(f"Updated document {doc_id} in memory")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document in ChromaDB: {str(e)}")
            return False
    
    def delete_document(self, doc_id):
        """
        Delete a document from the vector store
        
        Args:
            doc_id (str): Document ID
        
        Returns:
            bool: Success status
        """
        try:
            self.collection.delete(ids=[str(doc_id)])
            
            logger.debug(f"Deleted document {doc_id} from memory")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document from ChromaDB: {str(e)}")
            return False
    
    def clear_collection(self):
        """
        Clear all documents from the collection
        
        Returns:
            bool: Success status
        """
        try:
            self.collection.delete(where={})
            
            logger.debug(f"Cleared all documents from collection {COLLECTION_NAME}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing ChromaDB collection: {str(e)}")
            return False
