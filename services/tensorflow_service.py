"""
TensorFlow Service for AURA Research Assistant
Handles TensorFlow-related operations for paper analysis and machine learning tasks
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import traceback

# Set up logging
logger = logging.getLogger(__name__)

class TensorFlowService:
    """
    Service for TensorFlow operations
    """
    
    def __init__(self):
        """Initialize TensorFlow service"""
        logger.info("Initializing TensorFlowService")
        
        # Safely import TensorFlow and related libraries with error handling
        self.tf = None
        self.np = None
        self.sklearn_cluster = None
        
        try:
            import tensorflow as tf
            self.tf = tf
            logger.info(f"TensorFlow version: {tf.__version__}")
            
            # Suppress TensorFlow warnings
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            tf.get_logger().setLevel('ERROR')
            
            # Check for GPU
            gpus = tf.config.list_physical_devices('GPU')
            self.gpu_available = len(gpus) > 0
            logger.info(f"GPU available: {self.gpu_available}")
            
            if self.gpu_available:
                # Configure memory growth to avoid memory allocation errors
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                
                logger.info(f"Found {len(gpus)} GPU(s): {gpus}")
            
            # Import related libraries
            import numpy as np
            from sklearn import cluster as sklearn_cluster
            
            self.np = np
            self.sklearn_cluster = sklearn_cluster
            
            logger.info("TensorFlow components initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import TensorFlow or related libraries: {e}")
            self.is_available = False
        except Exception as e:
            logger.error(f"Error initializing TensorFlow: {e}")
            logger.error(traceback.format_exc())
            self.is_available = False
        
        self.is_available = self.tf is not None
    
    def is_tensorflow_available(self) -> bool:
        """Check if TensorFlow is available"""
        return self.is_available
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify text into research fields using TensorFlow
        
        Args:
            text (str): The text to classify
            
        Returns:
            dict: Classification results
        """
        if not self.is_available:
            return {
                "error": "TensorFlow is not available",
                "topic": "Unknown",
                "confidence": 0.0,
                "all_topics": {}
            }
        
        try:
            # Define research fields for classification
            research_fields = {
                "computer_science": ["machine learning", "artificial intelligence", "deep learning", 
                                     "neural network", "computer vision", "natural language processing",
                                     "algorithm", "data mining", "pattern recognition"],
                "biology": ["gene", "protein", "cell", "molecular", "dna", "rna", "genome",
                            "genetic", "organism", "physiology", "evolution"],
                "physics": ["quantum", "relativity", "particle", "theoretical", "astrophysics",
                           "cosmology", "mechanics", "thermodynamics", "string theory"],
                "medicine": ["clinical", "patient", "disease", "treatment", "therapy", "drug",
                            "diagnosis", "medical", "healthcare", "pathology"],
                "psychology": ["cognitive", "behavior", "mental", "brain", "perception",
                              "memory", "emotion", "psychological", "consciousness"],
                "economics": ["market", "economic", "finance", "investment", "monetary",
                             "fiscal", "trade", "business", "macroeconomic"]
            }
            
            # Convert text to lowercase for matching
            text_lower = text.lower()
            
            # Initialize scores
            scores = {field: 0 for field in research_fields}
            
            # Score each field based on keyword matching
            for field, keywords in research_fields.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        scores[field] += 1
            
            # Find the highest scoring field
            if any(scores.values()):
                # Get the field with the highest score
                top_field = max(scores.items(), key=lambda x: x[1])
                field_name = top_field[0]
                
                # Calculate a confidence score (normalized)
                total_matches = sum(scores.values())
                confidence = top_field[1] / total_matches if total_matches > 0 else 0
                
                # Format the field name for display
                display_name = field_name.replace("_", " ").title()
                
                # Format all topics with normalized scores
                all_topics = {
                    k.replace("_", " ").title(): round(v / total_matches, 2) if total_matches > 0 else 0
                    for k, v in scores.items() if v > 0
                }
                
                return {
                    "topic": display_name,
                    "confidence": round(confidence, 2),
                    "all_topics": all_topics
                }
            else:
                return {
                    "topic": "Unclassified",
                    "confidence": 0.0,
                    "all_topics": {}
                }
                
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "topic": "Error",
                "confidence": 0.0,
                "all_topics": {}
            }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of text using TensorFlow
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
        if not self.is_available:
            return {
                "error": "TensorFlow is not available",
                "sentiment": "neutral",
                "score": 0.5
            }
        
        try:
            # Simple rule-based sentiment analysis
            # In a production system, this would use a trained TensorFlow model
            
            # Define positive and negative words
            positive_words = [
                "good", "great", "excellent", "positive", "success", "successful", "breakthrough", 
                "beneficial", "advantage", "advantageous", "improvement", "improved", "advance",
                "effective", "efficient", "promising", "valuable", "significant", "innovative",
                "novel", "revolutionary", "outstanding", "remarkable", "exceptional"
            ]
            
            negative_words = [
                "bad", "poor", "negative", "failure", "failed", "drawback", "challenge", 
                "difficult", "problem", "issue", "limitation", "limited", "constraint",
                "ineffective", "inefficient", "disappointing", "disappointing", "inadequate",
                "insufficient", "unresolved", "unsuccessful", "weak", "flawed", "defect"
            ]
            
            # Normalize text
            text_lower = text.lower()
            
            # Count positive and negative words
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            total_count = positive_count + negative_count
            
            if total_count == 0:
                # No sentiment words found
                return {
                    "sentiment": "neutral",
                    "score": 0.5
                }
            else:
                # Calculate sentiment score (0 to 1, where 0.5 is neutral)
                sentiment_score = positive_count / total_count
                
                # Determine sentiment label
                if sentiment_score > 0.66:
                    sentiment = "positive"
                elif sentiment_score < 0.33:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                return {
                    "sentiment": sentiment,
                    "score": round(sentiment_score, 2)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "sentiment": "error",
                "score": 0.5
            }
    
    def analyze_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of papers using TensorFlow
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: Analysis results
        """
        if not self.is_available:
            return {
                "error": "TensorFlow is not available",
                "topics": [],
                "trends": [],
                "embeddings": []
            }
        
        try:
            # Extract paper texts
            texts = [f"{p.get('title', '')} {p.get('abstract', '')}" for p in papers]
            
            # Generate embeddings using TensorFlow Universal Sentence Encoder
            embeddings = self._generate_embeddings(texts)
            
            if embeddings is None:
                return {
                    "error": "Failed to generate embeddings",
                    "topics": [],
                    "trends": [],
                    "embeddings": []
                }
            
            # Identify topics using clustering
            topics = self._identify_topics(embeddings, texts)
            
            # Identify research trends (mock for demo)
            trends = self._identify_trends(papers)
            
            return {
                "topics": topics,
                "trends": trends,
                "embeddings": embeddings.tolist() if embeddings is not None else []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing papers with TensorFlow: {e}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "topics": [],
                "trends": [],
                "embeddings": []
            }
    
    def _generate_embeddings(self, texts: List[str]) -> Optional[Any]:
        """
        Generate embeddings for text using Universal Sentence Encoder
        
        Args:
            texts (list): List of text strings
            
        Returns:
            array: Embeddings matrix
        """
        try:
            # Check if we have the required libraries
            if self.tf is None or self.np is None:
                logger.error("Missing required libraries for embeddings generation")
                return None
            
            # Load Universal Sentence Encoder (USE) - with error handling for environments without internet
            try:
                # First, check if we've already loaded the model
                if not hasattr(self, 'use_model'):
                    logger.info("Loading Universal Sentence Encoder model")
                    # Try to load the model
                    try:
                        use_model = self.tf.keras.Sequential([
                            self.tf.keras.layers.InputLayer(input_shape=(1,), dtype=self.tf.string),
                            self.tf.hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder/4", 
                                                   trainable=False)
                        ])
                        self.use_model = use_model
                    except Exception as e:
                        logger.warning(f"Could not load USE model from TF Hub: {e}")
                        # Fallback to simpler TF-IDF embeddings
                        return self._generate_simple_embeddings(texts)
            except Exception as e:
                logger.warning(f"Error loading Universal Sentence Encoder: {e}")
                # Fallback to simpler TF-IDF embeddings
                return self._generate_simple_embeddings(texts)
            
            # Generate embeddings using the model
            embeddings = self.use_model(texts).numpy()
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _generate_simple_embeddings(self, texts: List[str]) -> Optional[Any]:
        """
        Generate simple TF-IDF embeddings as a fallback
        
        Args:
            texts (list): List of text strings
            
        Returns:
            array: TF-IDF matrix
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Create a TF-IDF vectorizer
            vectorizer = TfidfVectorizer(max_features=100)
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Convert to dense array for consistency with USE
            return tfidf_matrix.toarray()
        
        except Exception as e:
            logger.error(f"Error generating simple embeddings: {e}")
            return None
    
    def _identify_topics(self, embeddings: Any, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Identify topics in embeddings using clustering
        
        Args:
            embeddings (array): Embeddings matrix
            texts (list): Original text strings
            
        Returns:
            list: List of identified topics with weights
        """
        try:
            if self.sklearn_cluster is None:
                return []
            
            # Determine number of clusters (topics)
            n_clusters = min(4, len(texts))  # Max 4 topics, or fewer if fewer papers
            
            # Use K-means clustering to identify topics
            kmeans = self.sklearn_cluster.KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit(embeddings)
            
            # Create feature names if available from TF-IDF, otherwise use dummy names
            if hasattr(embeddings, 'get_feature_names_out'):
                feature_names = embeddings.get_feature_names_out()
            else:
                # Create topical keywords from most common words in texts
                from collections import Counter
                import re
                
                all_words = []
                for text in texts:
                    # Simple tokenization
                    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                    all_words.extend(words)
                
                # Count word frequency
                word_counts = Counter(all_words)
                # Remove common stopwords
                stopwords = {'the', 'and', 'of', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'as'}
                for word in stopwords:
                    if word in word_counts:
                        del word_counts[word]
                
                # Get the most common words as feature names
                feature_names = [word for word, _ in word_counts.most_common(100)]
            
            # Identify topic keywords based on cluster centers
            topic_keywords = []
            for i in range(n_clusters):
                # Get indices of examples in this cluster
                cluster_indices = [j for j, label in enumerate(clusters.labels_) if label == i]
                
                # Get a representative name for the topic using common words
                topic_words = []
                for idx in cluster_indices:
                    if idx < len(texts):
                        text = texts[idx]
                        # Extract top 5 words by length (simple heuristic)
                        words = sorted(set(re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())), key=len, reverse=True)[:5]
                        topic_words.extend(words)
                
                # Count word frequency
                topic_word_counts = Counter(topic_words)
                
                # Remove common stopwords
                for word in stopwords:
                    if word in topic_word_counts:
                        del topic_word_counts[word]
                
                # Get the most common words for this topic
                keywords = [word for word, _ in topic_word_counts.most_common(3)]
                topic_name = " ".join(keywords[:2]).title() if keywords else f"Topic {i+1}"
                
                # Calculate topic weight (normalized size of cluster)
                weight = len(cluster_indices) / len(texts)
                
                topic_keywords.append({
                    "name": topic_name,
                    "weight": round(weight, 2),
                    "keywords": keywords
                })
            
            # Sort topics by weight
            return sorted(topic_keywords, key=lambda x: x["weight"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error identifying topics: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def _identify_trends(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify research trends from papers
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            list: List of identified trends
        """
        # For demo purposes, generate sample trends
        try:
            # Extract publication years
            years = []
            for paper in papers:
                year_str = paper.get('year', '')
                if isinstance(year_str, str) and year_str.isdigit():
                    years.append(int(year_str))
                elif isinstance(year_str, int):
                    years.append(year_str)
            
            if not years:
                # Use current years if no years found
                years = [2022, 2023, 2024]
            
            # Find the earliest and latest years
            earliest_year = min(years) if years else 2020
            latest_year = max(years) if years else 2024
            
            # Extract keywords from titles and abstracts
            keywords = []
            for paper in papers:
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                
                # Simple keyword extraction (could be improved with NLP techniques)
                import re
                words = re.findall(r'\b[A-Z][a-z]{2,}\w*\b', title + ' ' + abstract)
                keywords.extend(words)
            
            from collections import Counter
            keyword_counts = Counter(keywords)
            
            # Generate trends based on top keywords
            trends = []
            for i, (keyword, count) in enumerate(keyword_counts.most_common(5)):
                if i >= 3:  # Limit to 3 trends
                    break
                
                # Assign a year between earliest and latest
                year = earliest_year + i
                if year > latest_year:
                    year = latest_year
                
                # Calculate a growth score
                growth = 0.9 - (i * 0.1)  # Decreasing growth for less common keywords
                
                trends.append({
                    "name": keyword,
                    "year": year,
                    "growth": round(growth, 2)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error identifying trends: {e}")
            logger.error(traceback.format_exc())
            return []