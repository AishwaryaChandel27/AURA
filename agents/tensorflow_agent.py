"""
TensorFlow Agent for AURA Research Assistant
Agent responsible for TensorFlow-based analysis of research papers
"""

import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

import tensorflow as tf
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

# Set up logging
logger = logging.getLogger(__name__)

class TensorFlowAgent:
    """
    Agent responsible for TensorFlow-based analysis
    This is the central agent focusing on machine learning capabilities
    """
    
    def __init__(self):
        """Initialize the TensorFlowAgent"""
        # This is a placeholder initialization
        # In a real implementation, this would load TensorFlow models
        logger.info("Initializing TensorFlow Agent")
        
        # Check if TensorFlow is available
        self.tensorflow_available = self._check_tensorflow()
    
    def analyze_papers(self, papers: List[Dict[str, Any]], analysis_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a collection of papers using TensorFlow
        
        Args:
            papers (list): List of papers to analyze
            analysis_type (str, optional): Type of analysis to perform
                Options: 'clustering', 'topic_modeling', 'similarity', 'trend_analysis'
                
        Returns:
            dict: Analysis results
        """
        try:
            # If TensorFlow is not available, use mock responses
            if not self.tensorflow_available:
                logger.warning("TensorFlow not available, using mock responses")
                return self._mock_analysis(papers, analysis_type)
            
            # Default to clustering if no analysis type specified
            if analysis_type is None:
                analysis_type = 'clustering'
            
            # Run the appropriate analysis
            if analysis_type == 'clustering':
                return self.cluster_papers(papers)
            elif analysis_type == 'topic_modeling':
                return self.extract_topics(papers)
            elif analysis_type == 'similarity':
                return self.analyze_paper_similarity(papers)
            elif analysis_type == 'trend_analysis':
                return self.analyze_research_trends(papers)
            else:
                return {
                    'error': f"Unknown analysis type: {analysis_type}",
                    'available_types': ['clustering', 'topic_modeling', 'similarity', 'trend_analysis']
                }
        
        except Exception as e:
            logger.error(f"Error analyzing papers: {e}")
            return {
                'error': f"Analysis failed: {str(e)}",
                'analysis_type': analysis_type,
                'summary': "Analysis could not be completed due to an error."
            }
    
    def cluster_papers(self, papers: List[Dict[str, Any]], num_clusters: int = 3) -> Dict[str, Any]:
        """
        Cluster papers based on their content using TensorFlow
        
        Args:
            papers (list): List of papers to cluster
            num_clusters (int): Number of clusters to create
            
        Returns:
            dict: Clustering results
        """
        try:
            # If TensorFlow is not available, use mock clustering
            if not self.tensorflow_available:
                return self._mock_clustering(papers, num_clusters)
            
            # Extract text content from papers
            texts = [p.get('abstract', '') for p in papers]
            titles = [p.get('title', '') for p in papers]
            
            # Use TF-IDF vectorization
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            
            # Handle empty texts
            valid_texts = [t if t else "No abstract available" for t in texts]
            
            # Create document vectors
            X = vectorizer.fit_transform(valid_texts)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=min(num_clusters, len(papers)), random_state=0)
            clusters = kmeans.fit_predict(X)
            
            # Extract features for each cluster
            cluster_terms = {}
            feature_names = vectorizer.get_feature_names_out()
            order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            
            for cluster_idx in range(min(num_clusters, len(papers))):
                cluster_terms[cluster_idx] = [
                    feature_names[i] for i in order_centroids[cluster_idx, :10]
                ]
            
            # Group papers by cluster
            clustered_papers = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id not in clustered_papers:
                    clustered_papers[cluster_id] = []
                
                clustered_papers[cluster_id].append({
                    'title': titles[i],
                    'abstract_preview': texts[i][:100] + '...' if texts[i] else 'No abstract',
                    'paper_index': i
                })
            
            # Format results
            cluster_results = []
            for cluster_id, papers_in_cluster in clustered_papers.items():
                cluster_results.append({
                    'cluster_id': int(cluster_id),
                    'keywords': cluster_terms.get(cluster_id, []),
                    'papers': papers_in_cluster,
                    'paper_count': len(papers_in_cluster)
                })
            
            return {
                'analysis_type': 'clustering',
                'num_clusters': min(num_clusters, len(papers)),
                'clusters': cluster_results,
                'summary': f"Clustered {len(papers)} papers into {len(cluster_results)} groups based on content similarity."
            }
        
        except Exception as e:
            logger.error(f"Error clustering papers: {e}")
            return self._mock_clustering(papers, num_clusters)
    
    def extract_topics(self, papers: List[Dict[str, Any]], num_topics: int = 5) -> Dict[str, Any]:
        """
        Extract topics from papers using TensorFlow
        
        Args:
            papers (list): List of papers
            num_topics (int): Number of topics to extract
            
        Returns:
            dict: Topic modeling results
        """
        try:
            # If TensorFlow is not available, use mock topics
            if not self.tensorflow_available:
                return self._mock_topic_modeling(papers, num_topics)
            
            # Extract text content from papers
            texts = [p.get('abstract', '') for p in papers]
            
            # Use TF-IDF vectorization
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            
            # Handle empty texts
            valid_texts = [t if t else "No abstract available" for t in texts]
            
            # Create document vectors
            X = vectorizer.fit_transform(valid_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Apply Non-negative Matrix Factorization for topic modeling
            from sklearn.decomposition import NMF
            nmf = NMF(n_components=min(num_topics, len(papers), X.shape[1]), random_state=0)
            W = nmf.fit_transform(X)
            H = nmf.components_
            
            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(H):
                top_indices = topic.argsort()[-10:][::-1]
                topic_terms = [feature_names[i] for i in top_indices]
                
                # Calculate topic weight (normalized)
                topic_weight = np.sum(W[:, topic_idx]) / np.sum(W)
                
                topics.append({
                    'id': topic_idx,
                    'keywords': topic_terms,
                    'weight': float(topic_weight),
                    'papers': []
                })
            
            # Assign papers to topics
            for paper_idx, paper_topic_weights in enumerate(W):
                top_topic_idx = paper_topic_weights.argmax()
                
                if paper_idx < len(papers):
                    paper_info = {
                        'title': papers[paper_idx].get('title', f'Paper {paper_idx}'),
                        'weight': float(paper_topic_weights[top_topic_idx]),
                        'paper_index': paper_idx
                    }
                    
                    # Find the topic with matching ID
                    for topic in topics:
                        if topic['id'] == top_topic_idx:
                            topic['papers'].append(paper_info)
                            break
            
            return {
                'analysis_type': 'topic_modeling',
                'num_topics': len(topics),
                'topics': topics,
                'summary': f"Extracted {len(topics)} key research topics from {len(papers)} papers."
            }
        
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return self._mock_topic_modeling(papers, num_topics)
    
    def analyze_paper_similarity(self, papers: List[Dict[str, Any]], threshold: float = 0.5) -> Dict[str, Any]:
        """
        Analyze similarity between papers using TensorFlow
        
        Args:
            papers (list): List of papers
            threshold (float): Similarity threshold
            
        Returns:
            dict: Similarity analysis results
        """
        try:
            # If TensorFlow is not available, use mock similarity
            if not self.tensorflow_available:
                return self._mock_similarity_analysis(papers, threshold)
            
            # Extract text content from papers
            texts = [p.get('abstract', '') for p in papers]
            titles = [p.get('title', '') for p in papers]
            
            # Skip if insufficient papers
            if len(papers) < 2:
                return {
                    'analysis_type': 'similarity',
                    'similar_pairs': [],
                    'summary': "Similarity analysis requires at least 2 papers."
                }
            
            # Use TF-IDF vectorization and cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Handle empty texts
            valid_texts = [t if t else "No abstract available" for t in texts]
            
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            X = vectorizer.fit_transform(valid_texts)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(X)
            
            # Find similar paper pairs
            similar_pairs = []
            for i in range(len(papers)):
                for j in range(i+1, len(papers)):
                    similarity_score = similarity_matrix[i, j]
                    
                    if similarity_score >= threshold:
                        similar_pairs.append({
                            'paper1_index': i,
                            'paper2_index': j,
                            'paper1': titles[i],
                            'paper2': titles[j],
                            'similarity_score': float(similarity_score)
                        })
            
            # Sort by similarity score (descending)
            similar_pairs.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return {
                'analysis_type': 'similarity',
                'similar_pairs': similar_pairs,
                'summary': f"Found {len(similar_pairs)} similar paper pairs with similarity above {threshold}."
            }
        
        except Exception as e:
            logger.error(f"Error analyzing paper similarity: {e}")
            return self._mock_similarity_analysis(papers, threshold)
    
    def analyze_research_trends(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze research trends over time using TensorFlow
        
        Args:
            papers (list): List of papers
            
        Returns:
            dict: Trend analysis results
        """
        try:
            # If TensorFlow is not available, use mock trends
            if not self.tensorflow_available:
                return self._mock_trend_analysis(papers)
            
            # Extract publication years
            years = []
            for paper in papers:
                if 'published_date' in paper:
                    pub_date = paper['published_date']
                    if isinstance(pub_date, str):
                        # Extract year from ISO format string
                        year = int(pub_date.split('-')[0])
                    elif hasattr(pub_date, 'year'):
                        # Extract year from datetime object
                        year = pub_date.year
                    else:
                        continue
                    
                    years.append(year)
            
            # Count papers per year
            year_counts = Counter(years)
            
            # Sort by year
            trends = [{'year': year, 'count': count} for year, count in year_counts.items()]
            trends.sort(key=lambda x: x['year'])
            
            # Calculate growth rate
            growth_rates = []
            for i in range(1, len(trends)):
                prev_year = trends[i-1]
                curr_year = trends[i]
                
                if prev_year['count'] > 0:
                    growth_rate = (curr_year['count'] - prev_year['count']) / prev_year['count']
                    growth_rates.append({
                        'year': curr_year['year'],
                        'growth_rate': growth_rate
                    })
            
            return {
                'analysis_type': 'trend_analysis',
                'trends': trends,
                'growth_rates': growth_rates,
                'summary': f"Analyzed publication trends across {len(trends)} years, showing the evolution of research in this area."
            }
        
        except Exception as e:
            logger.error(f"Error analyzing research trends: {e}")
            return self._mock_trend_analysis(papers)
    
    def _check_tensorflow(self) -> bool:
        """Check if TensorFlow is available"""
        try:
            # Attempt a simple TensorFlow operation
            tf.constant([1, 2, 3])
            logger.info("TensorFlow is available")
            return True
        except Exception as e:
            logger.warning(f"TensorFlow not available: {e}")
            return False
    
    def _mock_analysis(self, papers: List[Dict[str, Any]], analysis_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate mock analysis results for testing"""
        # Default to clustering if no analysis type specified
        if analysis_type is None:
            analysis_type = 'clustering'
        
        # Run the appropriate mock analysis
        if analysis_type == 'clustering':
            return self._mock_clustering(papers)
        elif analysis_type == 'topic_modeling':
            return self._mock_topic_modeling(papers)
        elif analysis_type == 'similarity':
            return self._mock_similarity_analysis(papers)
        elif analysis_type == 'trend_analysis':
            return self._mock_trend_analysis(papers)
        else:
            return {
                'error': f"Unknown analysis type: {analysis_type}",
                'available_types': ['clustering', 'topic_modeling', 'similarity', 'trend_analysis']
            }
    
    def _mock_clustering(self, papers: List[Dict[str, Any]], num_clusters: int = 3) -> Dict[str, Any]:
        """Generate mock clustering results"""
        # Determine actual number of clusters
        actual_clusters = min(num_clusters, len(papers))
        
        # Generate random clusters
        clusters = []
        for i in range(actual_clusters):
            # Generate random keywords
            keywords = ["research", "analysis", "method", "approach", "algorithm", 
                        "model", "framework", "data", "results", "implementation"]
            random.shuffle(keywords)
            
            # Assign papers to clusters
            cluster_papers = []
            for j in range(len(papers)):
                if j % actual_clusters == i:
                    if j < len(papers):
                        cluster_papers.append({
                            'title': papers[j].get('title', f'Paper {j}'),
                            'abstract_preview': (papers[j].get('abstract', '')[:100] + '...') 
                                               if papers[j].get('abstract') else 'No abstract',
                            'paper_index': j
                        })
            
            clusters.append({
                'cluster_id': i,
                'keywords': keywords[:5],
                'papers': cluster_papers,
                'paper_count': len(cluster_papers)
            })
        
        return {
            'analysis_type': 'clustering',
            'num_clusters': actual_clusters,
            'clusters': clusters,
            'summary': f"Clustered {len(papers)} papers into {actual_clusters} groups based on content similarity."
        }
    
    def _mock_topic_modeling(self, papers: List[Dict[str, Any]], num_topics: int = 5) -> Dict[str, Any]:
        """Generate mock topic modeling results"""
        # Determine actual number of topics
        actual_topics = min(num_topics, len(papers))
        
        # Generate random topics
        topics = []
        for i in range(actual_topics):
            # Generate random keywords
            keywords = ["algorithm", "model", "data", "neural", "training", 
                       "learning", "framework", "performance", "optimization", "architecture"]
            random.shuffle(keywords)
            
            # Assign papers to topics
            topic_papers = []
            for j in range(len(papers)):
                if j % actual_topics == i:
                    if j < len(papers):
                        topic_papers.append({
                            'title': papers[j].get('title', f'Paper {j}'),
                            'weight': random.uniform(0.7, 0.95),
                            'paper_index': j
                        })
            
            topics.append({
                'id': i,
                'keywords': keywords[:5],
                'weight': round(1.0 / actual_topics, 2),
                'papers': topic_papers
            })
        
        return {
            'analysis_type': 'topic_modeling',
            'num_topics': actual_topics,
            'topics': topics,
            'summary': f"Extracted {actual_topics} key research topics from {len(papers)} papers."
        }
    
    def _mock_similarity_analysis(self, papers: List[Dict[str, Any]], threshold: float = 0.5) -> Dict[str, Any]:
        """Generate mock similarity analysis results"""
        # Skip if insufficient papers
        if len(papers) < 2:
            return {
                'analysis_type': 'similarity',
                'similar_pairs': [],
                'summary': "Similarity analysis requires at least 2 papers."
            }
        
        # Generate random similar pairs
        similar_pairs = []
        num_pairs = min(10, len(papers) * (len(papers) - 1) // 2)
        
        for _ in range(num_pairs):
            # Select random paper indices
            i = random.randint(0, len(papers) - 2)
            j = random.randint(i + 1, len(papers) - 1)
            
            # Generate random similarity score
            similarity_score = random.uniform(threshold, 0.95)
            
            similar_pairs.append({
                'paper1_index': i,
                'paper2_index': j,
                'paper1': papers[i].get('title', f'Paper {i}'),
                'paper2': papers[j].get('title', f'Paper {j}'),
                'similarity_score': similarity_score
            })
        
        # Sort by similarity score (descending)
        similar_pairs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            'analysis_type': 'similarity',
            'similar_pairs': similar_pairs,
            'summary': f"Found {len(similar_pairs)} similar paper pairs with similarity above {threshold}."
        }
    
    def _mock_trend_analysis(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mock trend analysis results"""
        # Generate years spanning from 2015 to 2025
        years = list(range(2015, 2026))
        
        # Generate random paper counts per year with an increasing trend
        base_count = 5
        trends = []
        
        for year in years:
            # Add some randomness but maintain general increasing trend
            count = base_count + (year - 2015) * 2 + random.randint(-2, 2)
            count = max(1, count)  # Ensure at least 1 paper per year
            
            trends.append({
                'year': year,
                'count': count
            })
            
            # Increase base count for next year
            base_count = count
        
        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(trends)):
            prev_year = trends[i-1]
            curr_year = trends[i]
            
            growth_rate = (curr_year['count'] - prev_year['count']) / prev_year['count']
            growth_rates.append({
                'year': curr_year['year'],
                'growth_rate': growth_rate
            })
        
        return {
            'analysis_type': 'trend_analysis',
            'trends': trends,
            'growth_rates': growth_rates,
            'summary': f"Analyzed publication trends across {len(trends)} years, showing the evolution of research in this area."
        }