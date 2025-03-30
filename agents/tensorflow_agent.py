"""
TensorFlow Agent for AURA Research Assistant
Agent responsible for TensorFlow-based analysis tasks
"""

import logging
from typing import Dict, List, Any, Optional

from services.tensorflow_service import TensorFlowService

# Set up logging
logger = logging.getLogger(__name__)

class TensorFlowAgent:
    """
    Agent responsible for TensorFlow-based analysis and machine learning tasks
    """
    
    def __init__(self):
        """Initialize the TensorFlowAgent"""
        logger.info("Initializing TensorFlow Agent")
        
        # Initialize the TensorFlow service
        self.tensorflow_service = TensorFlowService()
        
        # Check if TensorFlow is available
        self.is_available = self.tensorflow_service.is_tensorflow_available()
        logger.info(f"TensorFlow is {'available' if self.is_available else 'not available'}")
    
    def analyze_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze papers using TensorFlow
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: Analysis results
        """
        if not self.is_available:
            return {
                "error": "TensorFlow is not available",
                "success": False,
                "message": "TensorFlow components could not be initialized. Analysis is not available."
            }
        
        try:
            # Use the TensorFlow service to analyze papers
            analysis_results = self.tensorflow_service.analyze_papers(papers)
            
            # Return the analysis results
            return {
                "success": True,
                "topics": analysis_results.get("topics", []),
                "trends": analysis_results.get("trends", []),
                "message": "Papers analyzed successfully with TensorFlow"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing papers with TensorFlow: {e}")
            return {
                "error": str(e),
                "success": False,
                "message": f"Error analyzing papers: {str(e)}"
            }
    
    def classify_research_field(self, text: str) -> Dict[str, Any]:
        """
        Classify research field based on text
        
        Args:
            text (str): Text to classify
            
        Returns:
            dict: Classification results
        """
        # For demo purposes, just use a simple classification heuristic
        # In a production system, this would use TensorFlow for real classification
        research_fields = {
            "machine learning": ["neural network", "deep learning", "algorithm", "tensorflow", "pytorch", "training"],
            "natural language processing": ["language", "text", "nlp", "gpt", "bert", "transformer", "token"],
            "computer vision": ["image", "video", "vision", "cnn", "detection", "segmentation", "recognition"],
            "robotics": ["robot", "automation", "control", "autonomous", "navigation", "sensor"],
            "bioinformatics": ["biology", "genome", "protein", "dna", "rna", "sequence", "cell"],
        }
        
        # Count matches for each field
        text_lower = text.lower()
        field_scores = {}
        
        for field, keywords in research_fields.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                field_scores[field] = score
        
        # Find the highest scoring field, or "general" if none found
        if field_scores:
            top_field = max(field_scores.items(), key=lambda x: x[1])
            confidence = min(top_field[1] / 3, 0.95)  # Scale confidence, max 0.95
        else:
            top_field = ("general research", 0)
            confidence = 0.5
        
        return {
            "field": top_field[0],
            "confidence": confidence,
            "all_fields": field_scores
        }
    
    def generate_research_summary(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a research summary based on papers
        
        Args:
            papers (list): List of paper dictionaries
            
        Returns:
            dict: Summary results
        """
        try:
            # Extract key topics and themes from papers
            analysis = self.tensorflow_service.analyze_papers(papers)
            topics = analysis.get("topics", [])
            trends = analysis.get("trends", [])
            
            # Generate a summary based on the analysis
            topic_names = [t["name"] for t in topics[:3]]
            trend_names = [t["name"] for t in trends[:2]]
            
            # Create a coherent summary
            summary = f"This research area focuses primarily on {', '.join(topic_names)}. "
            
            if trend_names:
                summary += f"Recent trends include {', '.join(trend_names)}. "
            
            summary += "The analysis shows potential opportunities for integrating TensorFlow-based approaches across these domains."
            
            return {
                "success": True,
                "summary": summary,
                "topics": topics,
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"Error generating research summary: {e}")
            return {
                "error": str(e),
                "success": False,
                "summary": "Unable to generate summary due to an error."
            }