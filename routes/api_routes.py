"""
API routes for AURA Research Assistant
"""

import logging
from flask import Blueprint, request, jsonify

from services import OpenAIService, TensorFlowService
from agents import TensorFlowAgent

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services and agents
openai_service = OpenAIService()
tensorflow_service = TensorFlowService()
tensorflow_agent = TensorFlowAgent()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "tensorflow_available": tensorflow_service.is_tensorflow_available(),
        "openai_available": openai_service.api_key is not None
    })

# Analyze papers endpoint
@api_bp.route('/analyze', methods=['POST'])
def analyze_papers():
    """Analyze papers using TensorFlow"""
    try:
        # Get request data
        data = request.json
        logger.debug(f"Received papers analysis request data: {data}")
        
        # Papers data is required
        papers = data.get('papers', [])
        logger.debug(f"Processing paper analysis, received {len(papers)} papers")
        
        if not papers:
            logger.warning("No papers data provided for paper analysis")
            return jsonify({"error": "Papers data is required"}), 400
            
        # Analyze papers with TensorFlow agent
        analysis_results = tensorflow_agent.analyze_papers(papers)
        return jsonify(analysis_results)
        
    except Exception as e:
        logger.error(f"Error analyzing papers: {e}")
        logger.error(f"Request data: {request.json}")
        return jsonify({"error": str(e)}), 500

# Text analysis endpoint - separate from papers analysis
@api_bp.route('/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze text using TensorFlow"""
    try:
        # Get request data
        data = request.json
        logger.debug(f"Received text analysis request data: {data}")
        
        # Text content is required
        text = data.get('text', '')
        logger.debug(f"Processing text analysis for: {text[:50]}...")
        
        if not text:
            logger.warning("No text provided for text analysis")
            return jsonify({"error": "Text is required"}), 400
        
        # Extract analysis type
        analysis_type = data.get('analysis_type', 'topic')
        logger.debug(f"Text analysis type: {analysis_type}")
        
        if analysis_type == 'topic':
            # Classify research field using basic text
            logger.debug("Running topic classification")
            result = tensorflow_service.classify_text(text)
            logger.debug(f"Classification result: {result}")
            return jsonify({
                "success": True,
                "topic": result.get("topic"),
                "confidence": result.get("confidence"),
                "all_topics": result.get("all_topics", {})
            })
            
        elif analysis_type == 'sentiment':
            # Analyze sentiment
            logger.debug("Running sentiment analysis")
            result = tensorflow_service.analyze_sentiment(text)
            return jsonify({
                "success": True,
                "sentiment": result.get("sentiment"),
                "score": result.get("score")
            })
            
        else:  # field classification
            # Research field classification with TensorFlow agent
            logger.debug("Running field classification with agent")
            try:
                field_info = tensorflow_agent.classify_research_field(text)
                return jsonify({
                    "success": True,
                    "field": field_info.get("field"),
                    "confidence": field_info.get("confidence"),
                    "all_fields": field_info.get("all_fields", {})
                })
            except Exception as e:
                logger.error(f"Error in TensorFlow agent: {e}")
                return jsonify({"error": str(e)}), 500
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        logger.error(f"Request data: {request.json}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/generate', methods=['POST'])
def generate_text():
    """Generate text using OpenAI"""
    try:
        # Get request data
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Generate text
        response = openai_service.generate_text(prompt)
        
        return jsonify({
            "success": True,
            "text": response
        })
        
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return jsonify({"error": str(e)}), 500