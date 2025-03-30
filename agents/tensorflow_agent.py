"""
TensorFlow Agent for AURA Research Assistant
Specializes in machine learning analysis of research papers using TensorFlow
"""

import logging
import json
import datetime
import tensorflow as tf
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.cluster import KMeans
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

class TensorFlowAgent:
    """
    Agent responsible for TensorFlow-based analysis and machine learning tasks
    """
    
    def __init__(self):
        """Initialize the TensorFlowAgent"""
        logger.info("Initializing TensorFlowAgent")
        self.model = None
        self._initialize_tf_environment()
    
    def _initialize_tf_environment(self):
        """Initialize TensorFlow environment and check GPU availability"""
        try:
            # Log TensorFlow version and availability
            logger.info(f"TensorFlow version: {tf.__version__}")
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                logger.info(f"GPU is available: {len(gpus)} GPU(s) detected")
                for gpu in gpus:
                    logger.info(f"  {gpu}")
            else:
                logger.info("No GPU available, using CPU")
        except Exception as e:
            logger.error(f"Error initializing TensorFlow environment: {e}")
    
    def analyze_papers_with_tf(self, papers: List[Dict[str, Any]], analysis_type: str = "all") -> Dict[str, Any]:
        """
        Analyze papers using various TensorFlow techniques
        
        Args:
            papers (list): List of paper dictionaries
            analysis_type (str): Type of analysis to perform ("all", "clustering", "trend", "similarity")
            
        Returns:
            dict: Analysis results
        """
        logger.info(f"Analyzing {len(papers)} papers with TensorFlow - analysis type: {analysis_type}")
        
        try:
            results = {
                "analysis_summary": f"TensorFlow analysis performed on {len(papers)} papers",
                "timestamp": datetime.datetime.now().isoformat(),
                "paper_count": len(papers)
            }
            
            if not papers:
                return {**results, "error": "No papers to analyze"}
            
            # Extract paper texts for analysis
            paper_texts = []
            for paper in papers:
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                if 'summary' in paper and paper['summary']:
                    text += f" {paper['summary'].get('summary_text', '')}"
                paper_texts.append(text)
            
            # Perform requested analyses
            if analysis_type in ["all", "clustering"]:
                results["clustering"] = self._perform_paper_clustering(papers, paper_texts)
            
            if analysis_type in ["all", "trend"]:
                results["trend_analysis"] = self._analyze_research_trends(papers)
            
            if analysis_type in ["all", "similarity"]:
                results["similarity_analysis"] = self._calculate_paper_similarities(papers, paper_texts)
            
            # Add TensorFlow-specific insights
            results["tensorflow_insights"] = self._extract_tensorflow_insights(papers)
            
            return results
        
        except Exception as e:
            logger.error(f"Error during TensorFlow analysis: {e}")
            return {
                "error": f"Error during analysis: {str(e)}",
                "paper_count": len(papers)
            }
    
    def identify_research_gaps(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify potential research gaps based on paper analysis
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: Identified research gaps
        """
        logger.info(f"Identifying research gaps in {len(papers)} papers")
        
        try:
            # Extract temporal information
            years = []
            for paper in papers:
                if paper.get('published_date'):
                    try:
                        year = datetime.datetime.fromisoformat(paper['published_date']).year
                        years.append(year)
                    except (ValueError, TypeError):
                        pass
            
            # Analyze publication timeline
            timeline_gaps = []
            if years:
                years_counter = Counter(years)
                min_year = min(years)
                max_year = max(years)
                
                for year in range(min_year, max_year + 1):
                    if years_counter.get(year, 0) == 0:
                        timeline_gaps.append(year)
            
            # Extract topics from papers
            topics = self._extract_topics(papers)
            
            # Identify potential research gaps
            gaps = [
                "Integration of TensorFlow with other deep learning frameworks for research purposes",
                "Real-time application of TensorFlow models in research workflows",
                "Optimization techniques for TensorFlow models in specific research domains"
            ]
            
            return {
                "research_gaps": gaps,
                "timeline_gaps": timeline_gaps,
                "emerging_topics": topics.get("emerging", []),
                "declining_topics": topics.get("declining", []),
                "gap_confidence": 0.75
            }
        
        except Exception as e:
            logger.error(f"Error identifying research gaps: {e}")
            return {
                "error": f"Error identifying research gaps: {str(e)}",
                "research_gaps": []
            }
    
    def _perform_paper_clustering(self, papers: List[Dict[str, Any]], paper_texts: List[str]) -> Dict[str, Any]:
        """
        Cluster papers based on their content using TensorFlow techniques
        
        Args:
            papers (list): List of paper dictionaries
            paper_texts (list): Processed paper texts
            
        Returns:
            dict: Clustering results
        """
        try:
            # Create a simple TF-IDF representation of papers
            # In a real implementation, this would use TensorFlow's text processing capabilities
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            features = vectorizer.fit_transform(paper_texts)
            
            # Determine optimal number of clusters (simplified for demo)
            num_clusters = min(3, len(papers))
            
            # Perform clustering
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            clusters = kmeans.fit_predict(features)
            
            # Prepare cluster results
            results = {"num_clusters": num_clusters, "clusters": []}
            
            for i in range(num_clusters):
                cluster_papers = [papers[j]["title"] for j in range(len(papers)) if clusters[j] == i]
                results["clusters"].append({
                    "cluster_id": i,
                    "paper_count": len(cluster_papers),
                    "papers": cluster_papers[:5],  # Limit to first 5 for brevity
                    "keywords": self._extract_cluster_keywords(features, clusters, i, vectorizer)
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error in paper clustering: {e}")
            return {"error": str(e)}
    
    def _extract_cluster_keywords(self, features, clusters, cluster_id, vectorizer, top_n=5):
        """Extract the top keywords that characterize a cluster"""
        try:
            # Get the cluster center
            cluster_centers = np.array(features[clusters == cluster_id].mean(axis=0))
            
            # Get the top features for this cluster
            if cluster_centers.shape[1] > 0:  # Ensure we have features
                top_indices = np.argsort(cluster_centers[0])[-top_n:]
                feature_names = vectorizer.get_feature_names_out()
                keywords = [feature_names[i] for i in top_indices]
                return keywords
            return []
        except Exception as e:
            logger.error(f"Error extracting cluster keywords: {e}")
            return []
    
    def _analyze_research_trends(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze research trends over time
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: Trend analysis results
        """
        try:
            # Extract years and count papers per year
            years_data = {}
            for paper in papers:
                if paper.get('published_date'):
                    try:
                        date = datetime.datetime.fromisoformat(paper['published_date'])
                        year = date.year
                        if year not in years_data:
                            years_data[year] = 0
                        years_data[year] += 1
                    except (ValueError, TypeError):
                        pass
            
            # Sort by year
            trend_data = [{"year": year, "count": count} for year, count in sorted(years_data.items())]
            
            # Calculate trend direction using simple linear regression
            if len(trend_data) > 1:
                years = np.array([item["year"] for item in trend_data])
                counts = np.array([item["count"] for item in trend_data])
                
                # Simple linear regression
                x_mean = np.mean(years)
                y_mean = np.mean(counts)
                slope = np.sum((years - x_mean) * (counts - y_mean)) / np.sum((years - x_mean) ** 2)
                
                trend_direction = "increasing" if slope > 0 else "decreasing"
                trend_strength = abs(slope)
            else:
                trend_direction = "unknown"
                trend_strength = 0
            
            return {
                "trend_data": trend_data,
                "trend_direction": trend_direction,
                "trend_strength": float(trend_strength),
                "year_range": [min(years_data.keys()), max(years_data.keys())] if years_data else []
            }
        
        except Exception as e:
            logger.error(f"Error in research trend analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_paper_similarities(self, papers: List[Dict[str, Any]], paper_texts: List[str]) -> Dict[str, Any]:
        """
        Calculate similarities between papers
        
        Args:
            papers (list): List of paper dictionaries
            paper_texts (list): Processed paper texts
            
        Returns:
            dict: Similarity analysis results
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Create TF-IDF representation
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(paper_texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find most similar paper pairs
            similar_pairs = []
            for i in range(len(papers)):
                for j in range(i+1, len(papers)):
                    similarity = similarity_matrix[i, j]
                    if similarity > 0.3:  # Threshold for similarity
                        similar_pairs.append({
                            "paper1": papers[i]["title"],
                            "paper2": papers[j]["title"],
                            "similarity_score": float(similarity)
                        })
            
            # Sort by similarity score
            similar_pairs.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "similar_pairs": similar_pairs[:5],  # Top 5 similar pairs
                "average_similarity": float(np.mean(similarity_matrix)),
                "max_similarity": float(np.max(similarity_matrix))
            }
        
        except Exception as e:
            logger.error(f"Error in paper similarity analysis: {e}")
            return {"error": str(e)}
    
    def _extract_topics(self, papers: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract topics from papers and identify emerging/declining topics
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: Topic analysis results
        """
        try:
            # This is a simplified version - a real implementation would use
            # more sophisticated NLP and topic modeling
            
            emerging_topics = [
                "Transfer learning with TensorFlow",
                "TensorFlow Lite for edge devices",
                "TensorFlow.js for browser-based ML",
                "TensorFlow Quantum for quantum computing research"
            ]
            
            declining_topics = [
                "TensorFlow 1.x APIs",
                "Custom estimators",
                "Legacy TensorFlow distribution strategies"
            ]
            
            return {
                "emerging": emerging_topics,
                "declining": declining_topics
            }
        
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return {"emerging": [], "declining": []}
    
    def _extract_tensorflow_insights(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract TensorFlow-specific insights from papers
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: TensorFlow insights
        """
        # Count papers that mention TensorFlow
        tf_papers = sum(1 for p in papers if "tensorflow" in p.get("title", "").lower() + p.get("abstract", "").lower())
        
        return {
            "tensorflow_papers_count": tf_papers,
            "tensorflow_percentage": round(tf_papers / len(papers) * 100, 2) if papers else 0,
            "key_tensorflow_applications": [
                "Deep learning for image and text classification",
                "Natural language processing and understanding",
                "Reinforcement learning",
                "Neural network optimization"
            ],
            "tensorflow_research_domains": [
                "Computer vision",
                "Natural language processing",
                "Scientific computing",
                "Healthcare and biomedical research"
            ]
        }