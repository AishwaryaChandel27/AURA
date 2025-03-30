"""
TensorFlow service for AURA Research Assistant
Handles machine learning operations with TensorFlow
"""

import os
import logging
import tensorflow as tf
import numpy as np
import json
from datetime import datetime
from sklearn.cluster import KMeans

# Set up logging
logger = logging.getLogger(__name__)

class TensorFlowService:
    """
    Service for TensorFlow operations
    """
    
    def __init__(self):
        """Initialize TensorFlow service"""
        # Set TensorFlow log level
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=ALL, 1=INFO, 2=WARNING, 3=ERROR
        logger.info("TensorFlow service initialized")
        logger.info(f"TensorFlow version: {tf.__version__}")
        
        # Check if GPU is available
        gpus = tf.config.list_physical_devices('GPU')
        self.has_gpu = len(gpus) > 0
        if self.has_gpu:
            logger.info(f"GPU is available: {gpus}")
        else:
            logger.info("No GPU found, using CPU")
    
    def create_paper_embeddings(self, papers):
        """
        Create embeddings for papers using TensorFlow
        
        Args:
            papers (list): List of paper dictionaries with titles and abstracts
            
        Returns:
            dict: Dictionary mapping paper IDs to embeddings
        """
        try:
            # Load Universal Sentence Encoder
            logger.info("Loading Universal Sentence Encoder...")
            embed = tf.saved_model.load("https://tfhub.dev/google/universal-sentence-encoder/4")
            
            # Create embeddings for papers
            embeddings = {}
            for paper in papers:
                paper_id = paper.get('id')
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                
                # Combine title and abstract
                text = f"{title}. {abstract}"
                
                # Get embedding
                text_embedding = embed([text])[0].numpy()
                embeddings[paper_id] = text_embedding.tolist()
            
            logger.info(f"Created embeddings for {len(embeddings)} papers")
            return embeddings
        
        except Exception as e:
            logger.error(f"Error creating paper embeddings: {e}")
            return {"error": str(e)}
    
    def analyze_research_trends(self, papers):
        """
        Analyze research trends in papers
        
        Args:
            papers (list): List of paper dictionaries with publication dates
            
        Returns:
            dict: Analysis of research trends
        """
        try:
            # Extract publication years
            years = []
            topics = {}
            
            for paper in papers:
                published_date = paper.get('published_date')
                if published_date:
                    if isinstance(published_date, str):
                        # Parse string to datetime
                        try:
                            date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                            year = date.year
                        except:
                            year = None
                    elif isinstance(published_date, datetime):
                        year = published_date.year
                    
                    if year:
                        years.append(year)
                
                # Extract topics from title/abstract
                title = paper.get('title', '').lower()
                abstract = paper.get('abstract', '').lower()
                
                # Simple keyword extraction
                keywords = ['machine learning', 'neural network', 'deep learning', 
                           'transformer', 'attention', 'computer vision', 'nlp',
                           'natural language processing', 'reinforcement learning',
                           'classification', 'regression', 'clustering', 'dataset']
                
                for keyword in keywords:
                    if keyword in title or keyword in abstract:
                        topics[keyword] = topics.get(keyword, 0) + 1
            
            # Analyze years
            year_counts = {}
            for year in years:
                year_counts[year] = year_counts.get(year, 0) + 1
            
            # Sort topics by frequency
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            top_topics = dict(sorted_topics[:10])
            
            return {
                'year_distribution': year_counts,
                'topic_distribution': top_topics,
                'total_papers': len(papers),
                'papers_with_dates': len(years)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing research trends: {e}")
            return {"error": str(e)}
    
    def predict_paper_impact(self, papers):
        """
        Train a simple model to predict paper impact (citations)
        
        Args:
            papers (list): List of paper dictionaries with metadata
            
        Returns:
            dict: Impact prediction results
        """
        try:
            # Extract features from papers
            features = []
            
            for paper in papers:
                # Extract basic features
                feature_dict = {
                    'title_length': len(paper.get('title', '')),
                    'abstract_length': len(paper.get('abstract', '')),
                    'num_authors': len(paper.get('authors', [])),
                    'has_code': 'code' in str(paper.get('metadata', {})).lower(),
                    'has_dataset': 'dataset' in str(paper.get('metadata', {})).lower(),
                    'has_github': 'github' in str(paper.get('metadata', {})).lower()
                }
                
                features.append(feature_dict)
            
            # Convert to numpy arrays
            X = np.array([[
                f['title_length'], 
                f['abstract_length'],
                f['num_authors'],
                int(f['has_code']),
                int(f['has_dataset']),
                int(f['has_github'])
            ] for f in features])
            
            # Normalize features
            X_mean = X.mean(axis=0)
            X_std = X.std(axis=0) + 1e-8  # Avoid division by zero
            X_norm = (X - X_mean) / X_std
            
            # Create a simple model
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(16, activation='relu', input_shape=(X_norm.shape[1],)),
                tf.keras.layers.Dense(8, activation='relu'),
                tf.keras.layers.Dense(1, activation='linear')
            ])
            
            # Compile model
            model.compile(optimizer='adam', loss='mse')
            
            # Generate synthetic impact scores for demonstration
            # Note: In a real scenario, we would use actual citation counts
            np.random.seed(42)  # For reproducibility
            y = np.random.normal(10, 5, size=(X.shape[0],))
            
            # Train model
            model.fit(X_norm, y, epochs=50, verbose=0)
            
            # Predict impact for each paper
            predictions = model.predict(X_norm).flatten()
            
            # Create result
            paper_predictions = []
            for i, paper in enumerate(papers):
                paper_predictions.append({
                    'paper_id': paper.get('id'),
                    'title': paper.get('title', ''),
                    'predicted_impact': float(predictions[i]),
                    'feature_importance': {
                        'title_length': features[i]['title_length'],
                        'abstract_length': features[i]['abstract_length'],
                        'num_authors': features[i]['num_authors'],
                        'has_code': features[i]['has_code'],
                        'has_dataset': features[i]['has_dataset'],
                        'has_github': features[i]['has_github']
                    }
                })
            
            # Sort by predicted impact
            paper_predictions.sort(key=lambda x: x['predicted_impact'], reverse=True)
            
            return {
                'impact_predictions': paper_predictions,
                'model_summary': str(model.summary()),
                'mean_predicted_impact': float(predictions.mean()),
                'note': "This is a demonstration model. Real impact prediction would require actual citation data."
            }
        
        except Exception as e:
            logger.error(f"Error predicting paper impact: {e}")
            return {"error": str(e)}
    
    def find_research_gaps(self, papers, embeddings=None):
        """
        Identify potential research gaps using paper embeddings
        
        Args:
            papers (list): List of paper dictionaries
            embeddings (dict, optional): Pre-computed embeddings
            
        Returns:
            dict: Identified research gaps
        """
        try:
            # Create embeddings if not provided
            if not embeddings:
                embeddings_result = self.create_paper_embeddings(papers)
                if "error" in embeddings_result:
                    return embeddings_result
                embeddings = embeddings_result
            
            # Extract paper topics and methods
            topics = set()
            methods = set()
            datasets = set()
            
            for paper in papers:
                # Extract from title and abstract
                title = paper.get('title', '').lower()
                abstract = paper.get('abstract', '').lower()
                
                # Simple topic extraction
                topic_keywords = ['classification', 'detection', 'generation', 'prediction',
                                 'segmentation', 'recognition', 'synthesis', 'analysis']
                
                # Simple method extraction
                method_keywords = ['cnn', 'rnn', 'lstm', 'gru', 'transformer', 'bert',
                                  'gpt', 'resnet', 'vgg', 'inception', 'attention']
                
                # Simple dataset extraction
                dataset_keywords = ['dataset', 'corpus', 'benchmark', 'imagenet',
                                   'coco', 'cifar', 'mnist', 'glue']
                
                # Check for topics
                for keyword in topic_keywords:
                    if keyword in title or keyword in abstract:
                        topics.add(keyword)
                
                # Check for methods
                for keyword in method_keywords:
                    if keyword in title or keyword in abstract:
                        methods.add(keyword)
                
                # Check for datasets
                for keyword in dataset_keywords:
                    if keyword in title or keyword in abstract:
                        datasets.add(keyword)
            
            # Generate potential combinations
            combinations = []
            potential_gaps = []
            
            for topic in topics:
                for method in methods:
                    combinations.append((topic, method))
            
            # Check which combinations are not covered in papers
            for combo in combinations:
                topic, method = combo
                found = False
                for paper in papers:
                    title = paper.get('title', '').lower()
                    abstract = paper.get('abstract', '').lower()
                    if topic in title or topic in abstract:
                        if method in title or method in abstract:
                            found = True
                            break
                
                if not found:
                    potential_gaps.append({
                        'topic': topic,
                        'method': method,
                        'description': f"Potential gap in applying {method} to {topic} tasks"
                    })
            
            # Suggest research directions
            suggested_directions = []
            for dataset in datasets:
                for method in methods:
                    # Check if this combination is already covered
                    found = False
                    for paper in papers:
                        title = paper.get('title', '').lower()
                        abstract = paper.get('abstract', '').lower()
                        if dataset in title or dataset in abstract:
                            if method in title or method in abstract:
                                found = True
                                break
                    
                    if not found:
                        suggested_directions.append({
                            'method': method,
                            'dataset': dataset,
                            'description': f"Consider applying {method} to the {dataset}"
                        })
            
            return {
                'potential_gaps': potential_gaps[:5],  # Limit to top 5
                'suggested_directions': suggested_directions[:5],  # Limit to top 5
                'topics_identified': list(topics),
                'methods_identified': list(methods),
                'datasets_identified': list(datasets)
            }
        
        except Exception as e:
            logger.error(f"Error finding research gaps: {e}")
            return {"error": str(e)}
    
    def cluster_papers(self, papers, embeddings=None):
        """
        Cluster papers using TensorFlow K-means
        
        Args:
            papers (list): List of paper dictionaries
            embeddings (dict, optional): Pre-computed embeddings
            
        Returns:
            dict: Clustering results
        """
        try:
            # Create embeddings if not provided
            if not embeddings:
                embeddings_result = self.create_paper_embeddings(papers)
                if "error" in embeddings_result:
                    return embeddings_result
                embeddings = embeddings_result
            
            # Get embeddings as numpy array
            paper_ids = list(embeddings.keys())
            embeddings_array = np.array([embeddings[paper_id] for paper_id in paper_ids])
            
            # Determine number of clusters (simple heuristic)
            n_clusters = min(5, len(papers))
            
            # Create K-means clustering model
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings_array)
            
            # Organize papers by cluster
            clusters = {}
            for i, paper_id in enumerate(paper_ids):
                cluster_id = int(cluster_labels[i])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                
                # Find paper data
                for paper in papers:
                    if paper.get('id') == paper_id:
                        clusters[cluster_id].append({
                            'paper_id': paper_id,
                            'title': paper.get('title', ''),
                            'abstract': paper.get('abstract', '')[:200] + '...' if len(paper.get('abstract', '')) > 200 else paper.get('abstract', '')
                        })
                        break
            
            # Extract common terms for each cluster
            cluster_terms = {}
            for cluster_id, cluster_papers in clusters.items():
                # Combine all text
                all_text = ' '.join([p['title'] + ' ' + p['abstract'] for p in cluster_papers])
                
                # Simple term frequency analysis
                words = all_text.lower().split()
                word_counts = {}
                for word in words:
                    if len(word) > 3:  # Filter short words
                        word_counts[word] = word_counts.get(word, 0) + 1
                
                # Get top terms
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                top_terms = [word for word, count in sorted_words[:10]]
                cluster_terms[cluster_id] = top_terms
            
            return {
                'clusters': clusters,
                'cluster_terms': cluster_terms,
                'num_clusters': n_clusters,
                'num_papers': len(papers)
            }
        
        except Exception as e:
            logger.error(f"Error clustering papers: {e}")
            return {"error": str(e)}
    
    def classify_papers(self, papers, categories=None):
        """
        Classify papers into research categories
        
        Args:
            papers (list): List of paper dictionaries
            categories (list, optional): List of categories for classification
            
        Returns:
            dict: Classification results
        """
        try:
            # Default categories if not provided
            if not categories:
                categories = [
                    'Machine Learning', 'Computer Vision', 'Natural Language Processing',
                    'Reinforcement Learning', 'Deep Learning', 'Data Mining',
                    'Speech Recognition', 'Robotics', 'Computational Biology'
                ]
            
            # Load Universal Sentence Encoder
            logger.info("Loading Universal Sentence Encoder for classification...")
            embed = tf.saved_model.load("https://tfhub.dev/google/universal-sentence-encoder/4")
            
            # Create category embeddings
            category_embeddings = embed(categories).numpy()
            
            # Classify each paper
            paper_classifications = []
            for paper in papers:
                paper_id = paper.get('id')
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                
                # Combine title and abstract
                text = f"{title}. {abstract}"
                
                # Get paper embedding
                paper_embedding = embed([text])[0].numpy()
                
                # Calculate similarity with each category
                similarities = []
                for i, category_embedding in enumerate(category_embeddings):
                    # Cosine similarity
                    similarity = np.dot(paper_embedding, category_embedding) / (
                        np.linalg.norm(paper_embedding) * np.linalg.norm(category_embedding)
                    )
                    similarities.append((categories[i], float(similarity)))
                
                # Sort by similarity
                similarities.sort(key=lambda x: x[1], reverse=True)
                top_categories = similarities[:3]  # Top 3 categories
                
                paper_classifications.append({
                    'paper_id': paper_id,
                    'title': title,
                    'categories': [
                        {'category': cat, 'confidence': conf}
                        for cat, conf in top_categories
                    ]
                })
            
            return {
                'classifications': paper_classifications,
                'categories_used': categories,
                'num_papers': len(papers)
            }
        
        except Exception as e:
            logger.error(f"Error classifying papers: {e}")
            return {"error": str(e)}
    
    def evaluate_research_impact(self, research_field, papers):
        """
        Evaluate the impact and future direction of a research field
        
        Args:
            research_field (str): Field of research to evaluate
            papers (list): Papers in the research field
            
        Returns:
            dict: Impact evaluation results
        """
        try:
            # Analyze trends over time
            trend_analysis = self.analyze_research_trends(papers)
            if "error" in trend_analysis:
                return trend_analysis
            
            # Create embeddings
            embeddings_result = self.create_paper_embeddings(papers)
            if "error" in embeddings_result:
                return embeddings_result
            
            # Find research gaps
            gaps_analysis = self.find_research_gaps(papers, embeddings_result)
            if "error" in gaps_analysis:
                return gaps_analysis
            
            # Create impact model
            impact_analysis = self.predict_paper_impact(papers)
            if "error" in impact_analysis:
                return impact_analysis
            
            # Combine results
            return {
                'research_field': research_field,
                'trend_analysis': trend_analysis,
                'gaps_analysis': gaps_analysis,
                'impact_analysis': {
                    'top_papers': impact_analysis['impact_predictions'][:5],
                    'mean_impact': impact_analysis['mean_predicted_impact']
                },
                'num_papers_analyzed': len(papers),
                'summary': f"Analysis of '{research_field}' based on {len(papers)} papers using TensorFlow",
                'future_directions': gaps_analysis['suggested_directions']
            }
        
        except Exception as e:
            logger.error(f"Error evaluating research impact: {e}")
            return {"error": str(e)}