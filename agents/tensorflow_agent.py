"""
TensorFlow Agent for AURA Research Assistant
Handles machine learning model training, predictions, and research trend analysis
"""

import logging
import re
from services.tensorflow_service import TensorFlowService

# Set up logging
logger = logging.getLogger(__name__)

class TensorFlowAgent:
    """
    Agent responsible for TensorFlow-based machine learning operations
    """
    
    def __init__(self):
        """Initialize TensorFlow agent"""
        self.tensorflow_service = TensorFlowService()
        logger.info("TensorFlow agent initialized")
    
    def analyze_papers_with_tf(self, papers, analysis_type="all"):
        """
        Analyze a collection of papers using TensorFlow models
        
        Args:
            papers (list): List of paper dictionaries
            analysis_type (str): Type of analysis to perform (embeddings, trends, impact, all)
        
        Returns:
            dict: Analysis results
        """
        if not papers:
            return {"error": "No papers provided for analysis"}
        
        results = {}
        
        try:
            # Create paper embeddings
            if analysis_type in ["embeddings", "all"]:
                embeddings = self.tensorflow_service.create_paper_embeddings(papers)
                if "error" not in embeddings:
                    results["embeddings"] = {
                        "message": f"Created embeddings for {len(embeddings)} papers",
                        "paper_count": len(embeddings)
                    }
                else:
                    results["embeddings"] = {
                        "error": embeddings["error"]
                    }
            
            # Analyze research trends
            if analysis_type in ["trends", "all"]:
                trends = self.tensorflow_service.analyze_research_trends(papers)
                if "error" not in trends:
                    results["trends"] = trends
                else:
                    results["trends"] = {
                        "error": trends["error"]
                    }
            
            # Predict paper impact
            if analysis_type in ["impact", "all"]:
                impact = self.tensorflow_service.predict_paper_impact(papers)
                if "error" not in impact:
                    results["impact"] = {
                        "message": "Completed citation impact prediction",
                        "top_papers": impact["impact_predictions"][:5]  # Top 5 papers
                    }
                else:
                    results["impact"] = {
                        "error": impact["error"]
                    }
            
            # Find similarities between papers
            if analysis_type in ["similarities", "all"]:
                # Get embeddings if not already computed
                if "embeddings" not in results:
                    embeddings = self.tensorflow_service.create_paper_embeddings(papers)
                    if "error" in embeddings:
                        results["similarities"] = {
                            "error": embeddings["error"]
                        }
                        return results
                
                # Cluster papers
                clusters = self.tensorflow_service.cluster_papers(papers)
                if "error" not in clusters:
                    results["similarities"] = {
                        "message": f"Clustered {len(papers)} papers into {clusters['num_clusters']} groups",
                        "clusters": clusters["clusters"],
                        "cluster_terms": clusters["cluster_terms"]
                    }
                else:
                    results["similarities"] = {
                        "error": clusters["error"]
                    }
            
            # Summary of all analyses
            if analysis_type == "all":
                results["summary"] = {
                    "message": f"Completed TensorFlow analysis on {len(papers)} papers",
                    "analyses_performed": [k for k in results.keys() if k != "summary"],
                    "paper_count": len(papers)
                }
            
            return results
        
        except Exception as e:
            logger.error(f"Error in TensorFlow paper analysis: {e}")
            return {"error": f"Error in TensorFlow paper analysis: {str(e)}"}
    
    def identify_research_gaps(self, papers):
        """
        Identify potential research gaps based on paper analysis
        
        Args:
            papers (list): List of paper dictionaries with embeddings
        
        Returns:
            dict: Identified research gaps and opportunities
        """
        if not papers:
            return {"error": "No papers provided for gap analysis"}
        
        try:
            # Create embeddings
            embeddings = self.tensorflow_service.create_paper_embeddings(papers)
            if "error" in embeddings:
                return {"error": embeddings["error"]}
            
            # Find research gaps
            gaps = self.tensorflow_service.find_research_gaps(papers, embeddings)
            if "error" in gaps:
                return {"error": gaps["error"]}
            
            return {
                "message": "Identified potential research gaps and opportunities",
                "potential_gaps": gaps["potential_gaps"],
                "suggested_directions": gaps["suggested_directions"],
                "topics_identified": gaps["topics_identified"],
                "methods_identified": gaps["methods_identified"],
                "datasets_identified": gaps["datasets_identified"]
            }
        
        except Exception as e:
            logger.error(f"Error identifying research gaps: {e}")
            return {"error": f"Error identifying research gaps: {str(e)}"}
    
    def suggest_experimental_design(self, hypothesis, papers=None):
        """
        Suggest experimental design for testing a hypothesis using TensorFlow analysis
        
        Args:
            hypothesis (str): The research hypothesis
            papers (list, optional): Reference papers for the experiment design
        
        Returns:
            dict: Experimental design suggestion
        """
        try:
            # Analyze papers if provided
            if papers:
                analysis = self.analyze_papers_with_tf(papers, analysis_type="trends")
                
                # Extract topics and methods
                topics = []
                methods = []
                
                if "trends" in analysis and "error" not in analysis["trends"]:
                    topic_dist = analysis["trends"].get("topic_distribution", {})
                    topics = list(topic_dist.keys())
                
                if papers:
                    # Extract methods from paper titles and abstracts
                    for paper in papers:
                        title = paper.get("title", "").lower()
                        abstract = paper.get("abstract", "").lower()
                        text = f"{title} {abstract}"
                        
                        # Look for common ML methods
                        method_keywords = [
                            "regression", "classification", "clustering", "neural network",
                            "cnn", "rnn", "lstm", "transformer", "bert", "gpt",
                            "reinforcement learning", "deep learning", "gan"
                        ]
                        
                        for method in method_keywords:
                            if method in text and method not in methods:
                                methods.append(method)
                
                # Generate experiment design
                return {
                    "hypothesis": hypothesis,
                    "title": f"Experiment to test: {hypothesis[:50]}...",
                    "methodology": self._generate_methodology(hypothesis, topics, methods),
                    "variables": {
                        "independent": self._extract_variables(hypothesis, "independent"),
                        "dependent": self._extract_variables(hypothesis, "dependent"),
                        "controlled": self._suggest_controls(topics, methods)
                    },
                    "metrics": self._suggest_metrics(topics, methods),
                    "technological_requirements": self._suggest_tech_requirements(topics, methods),
                    "tensorflow_components": self._suggest_tensorflow_components(topics, methods),
                    "references": [paper.get("title") for paper in papers[:3]] if papers else []
                }
            
            # Simpler design if no papers provided
            return {
                "hypothesis": hypothesis,
                "title": f"Experiment to test: {hypothesis[:50]}...",
                "methodology": self._generate_methodology(hypothesis, [], []),
                "variables": {
                    "independent": self._extract_variables(hypothesis, "independent"),
                    "dependent": self._extract_variables(hypothesis, "dependent"),
                    "controlled": []
                },
                "metrics": [],
                "technological_requirements": [],
                "tensorflow_components": self._suggest_tensorflow_components([], [])
            }
        
        except Exception as e:
            logger.error(f"Error suggesting experimental design: {e}")
            return {"error": f"Error suggesting experimental design: {str(e)}"}
    
    def train_citation_prediction_model(self, papers):
        """
        Train a TensorFlow model to predict citation counts/impact
        
        Args:
            papers (list): List of paper dictionaries with citation data
        
        Returns:
            dict: Training results
        """
        if not papers:
            return {"error": "No papers provided for citation prediction"}
        
        try:
            # Predict paper impact
            impact = self.tensorflow_service.predict_paper_impact(papers)
            if "error" in impact:
                return {"error": impact["error"]}
            
            return {
                "message": "Trained citation prediction model",
                "model_created": True,
                "impact_predictions": impact["impact_predictions"],
                "mean_predicted_impact": impact["mean_predicted_impact"],
                "feature_importance": self._extract_feature_importance(impact["impact_predictions"]),
                "note": impact["note"]
            }
        
        except Exception as e:
            logger.error(f"Error training citation prediction model: {e}")
            return {"error": f"Error training citation prediction model: {str(e)}"}
    
    def classify_research_papers(self, papers, categories=None):
        """
        Classify research papers into categories using TensorFlow
        
        Args:
            papers (list): List of paper dictionaries
            categories (list, optional): List of categories for classification
            
        Returns:
            dict: Classification results
        """
        if not papers:
            return {"error": "No papers provided for classification"}
        
        try:
            # Classify papers
            classification = self.tensorflow_service.classify_papers(papers, categories)
            if "error" in classification:
                return {"error": classification["error"]}
            
            return {
                "message": f"Classified {len(papers)} papers into research categories",
                "classifications": classification["classifications"],
                "categories_used": classification["categories_used"]
            }
        
        except Exception as e:
            logger.error(f"Error classifying research papers: {e}")
            return {"error": f"Error classifying research papers: {str(e)}"}
    
    def evaluate_research_impact(self, research_field, papers=None):
        """
        Evaluate the impact and future direction of a research field
        
        Args:
            research_field (str): Field of research to evaluate
            papers (list, optional): Papers in the research field
            
        Returns:
            dict: Impact evaluation results
        """
        if not papers:
            return {"error": "No papers provided for research impact evaluation"}
        
        try:
            # Evaluate research impact
            impact = self.tensorflow_service.evaluate_research_impact(research_field, papers)
            if "error" in impact:
                return {"error": impact["error"]}
            
            return {
                "message": f"Evaluated research impact for '{research_field}'",
                "research_field": impact["research_field"],
                "trend_analysis": impact["trend_analysis"],
                "future_directions": impact["future_directions"],
                "top_papers": impact["impact_analysis"]["top_papers"],
                "mean_impact": impact["impact_analysis"]["mean_impact"]
            }
        
        except Exception as e:
            logger.error(f"Error evaluating research impact: {e}")
            return {"error": f"Error evaluating research impact: {str(e)}"}
    
    # Helper methods
    def _generate_methodology(self, hypothesis, topics, methods):
        """Generate methodology based on hypothesis and paper topics/methods"""
        if "classification" in methods or "predict" in hypothesis.lower():
            return "Train a classification model using TensorFlow to predict outcomes based on features extracted from the data."
        elif "clustering" in methods or "group" in hypothesis.lower():
            return "Implement clustering algorithms to identify patterns and groupings in the data."
        elif "neural network" in methods or "deep learning" in topics:
            return "Design and train neural network architectures using TensorFlow to model the relationships in the data."
        else:
            return "Design a controlled experiment using TensorFlow models to test the hypothesis by analyzing the relationship between variables."
    
    def _extract_variables(self, hypothesis, var_type):
        """Extract potential variables from hypothesis text"""
        hypothesis_lower = hypothesis.lower()
        
        if var_type == "independent":
            # Look for phrases indicating independent variables
            patterns = [
                r"effect of ([\w\s]+) on",
                r"impact of ([\w\s]+) on",
                r"influence of ([\w\s]+) on",
                r"role of ([\w\s]+) in",
                r"relationship between ([\w\s]+) and"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, hypothesis_lower)
                if match:
                    return [match.group(1).strip()]
            
            # Default if no match
            return ["experimental condition"]
        
        elif var_type == "dependent":
            # Look for phrases indicating dependent variables
            patterns = [
                r"effect (?:of|on) (?:[\w\s]+) on ([\w\s]+)",
                r"impact (?:of|on) (?:[\w\s]+) on ([\w\s]+)",
                r"influence (?:of|on) (?:[\w\s]+) on ([\w\s]+)",
                r"changes in ([\w\s]+)",
                r"measured by ([\w\s]+)",
                r"predict(?:ing)? ([\w\s]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, hypothesis_lower)
                if match:
                    return [match.group(1).strip()]
            
            # Default if no match
            return ["outcome measure"]
    
    def _suggest_controls(self, topics, methods):
        """Suggest control variables based on topics and methods"""
        controls = ["sample size", "data distribution"]
        
        if "deep learning" in topics or "neural network" in methods:
            controls.extend(["learning rate", "network architecture", "batch size"])
        
        if "clustering" in methods:
            controls.extend(["number of clusters", "distance metric"])
        
        if "classification" in methods:
            controls.extend(["feature selection", "class distribution"])
        
        return controls[:5]  # Limit to 5 controls
    
    def _suggest_metrics(self, topics, methods):
        """Suggest evaluation metrics based on topics and methods"""
        metrics = ["accuracy", "F1 score"]
        
        if "classification" in methods:
            metrics.extend(["precision", "recall", "ROC AUC"])
        
        if "clustering" in methods:
            metrics.extend(["silhouette score", "Davies-Bouldin index"])
        
        if "regression" in methods:
            metrics.extend(["MSE", "MAE", "R-squared"])
        
        return metrics[:5]  # Limit to 5 metrics
    
    def _suggest_tech_requirements(self, topics, methods):
        """Suggest technological requirements based on topics and methods"""
        requirements = ["TensorFlow", "Python environment"]
        
        if "deep learning" in topics or "neural network" in methods:
            requirements.extend(["GPU acceleration", "sufficient RAM for model training"])
        
        if "clustering" in methods or "classification" in methods:
            requirements.append("scikit-learn for preprocessing and evaluation")
        
        if any(m in methods for m in ["bert", "gpt", "transformer"]):
            requirements.append("transformer libraries (e.g., Hugging Face)")
        
        return requirements[:5]  # Limit to 5 requirements
    
    def _suggest_tensorflow_components(self, topics, methods):
        """Suggest TensorFlow components based on topics and methods"""
        components = ["tf.keras for model building"]
        
        if "deep learning" in topics or "neural network" in methods:
            components.extend([
                "tf.keras.layers for network architecture",
                "tf.keras.callbacks for training monitoring"
            ])
        
        if "clustering" in methods:
            components.append("tf.cluster for clustering algorithms")
        
        if any(m in methods for m in ["lstm", "rnn"]):
            components.append("tf.keras.layers.LSTM for sequence modeling")
        
        if any(m in methods for m in ["cnn", "computer vision"]):
            components.append("tf.keras.layers.Conv2D for image processing")
        
        return components[:5]  # Limit to 5 components
    
    def _extract_feature_importance(self, predictions):
        """Extract feature importance from predictions"""
        if not predictions:
            return {}
        
        # Aggregate feature values across all predictions
        feature_sums = {}
        feature_counts = {}
        
        for pred in predictions:
            if "feature_importance" in pred:
                for feature, value in pred["feature_importance"].items():
                    if isinstance(value, (int, float)):
                        feature_sums[feature] = feature_sums.get(feature, 0) + value
                        feature_counts[feature] = feature_counts.get(feature, 0) + 1
                    elif isinstance(value, bool):
                        # Convert boolean to integer (1 for True, 0 for False)
                        int_value = 1 if value else 0
                        feature_sums[feature] = feature_sums.get(feature, 0) + int_value
                        feature_counts[feature] = feature_counts.get(feature, 0) + 1
        
        # Calculate average values
        feature_avgs = {}
        for feature in feature_sums:
            if feature_counts[feature] > 0:
                feature_avgs[feature] = feature_sums[feature] / feature_counts[feature]
        
        return feature_avgs