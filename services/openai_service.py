"""
OpenAI Service for AURA Research Assistant
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional

# Import OpenAI SDK
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service for interacting with OpenAI API
    """
    
    def __init__(self):
        """Initialize the OpenAIService"""
        logger.info("OpenAI service initialized")
        
        # Get API key from environment
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI API key not found in environment variables")
            self.client = None
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using OpenAI
        
        Args:
            prompt (str): The prompt for text generation
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            str: Generated text
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def summarize_text(self, text: str, max_tokens: int = 250) -> str:
        """
        Summarize text using OpenAI
        
        Args:
            text (str): The text to summarize
            max_tokens (int): Maximum number of tokens in the summary
            
        Returns:
            str: Generated summary
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        prompt = f"Please summarize the following text concisely while maintaining key points:\n\n{text}"
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            raise
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key points from text using OpenAI
        
        Args:
            text (str): The text to extract key points from
            num_points (int): Number of key points to extract
            
        Returns:
            list: List of key points
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        prompt = (
            f"Extract {num_points} key points from the following text. "
            f"Respond with a JSON array of strings, with each string being a key point:\n\n{text}"
        )
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            response_content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                result = json.loads(response_content)
                if "key_points" in result:
                    return result["key_points"]
                else:
                    return list(result.values())[0] if result else []
            except json.JSONDecodeError:
                # If JSON parsing fails, extract manually
                key_points = []
                for line in response_content.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        key_points.append(line[1:].strip())
                return key_points[:num_points]
                
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            raise
    
    def generate_hypothesis(self, research_question: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a research hypothesis based on a research question and paper summaries
        
        Args:
            research_question (str): The research question
            papers (list): List of paper data with titles, abstracts, etc.
            
        Returns:
            dict: Generated hypothesis, reasoning, and confidence score
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        # Format paper data for the prompt
        papers_text = ""
        for i, paper in enumerate(papers):
            papers_text += f"Paper {i+1}: {paper.get('title', 'Untitled')}\n"
            papers_text += f"Abstract: {paper.get('abstract', 'No abstract available')}\n\n"
        
        prompt = (
            f"Based on the following research question and papers, generate a well-formed scientific hypothesis. "
            f"Return your response as a JSON object with the following keys: "
            f"'hypothesis_text', 'reasoning', and 'confidence_score' (between 0 and 1).\n\n"
            f"Research Question: {research_question}\n\n"
            f"Papers:\n{papers_text}"
        )
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "hypothesis_text": result.get("hypothesis_text", ""),
                "reasoning": result.get("reasoning", ""),
                "confidence_score": result.get("confidence_score", 0.0)
            }
                
        except Exception as e:
            logger.error(f"Error generating hypothesis: {e}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a text
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Sentiment analysis results including rating and confidence
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. "
                        + "Analyze the sentiment of the text and provide a rating "
                        + "from 1 to 5 stars and a confidence score between 0 and 1. "
                        + "Respond with JSON in this format: "
                        + "{'rating': number, 'confidence': number}",
                    },
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "rating": max(1, min(5, round(result.get("rating", 3)))),
                "confidence": max(0, min(1, result.get("confidence", 0.5))),
            }
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise

    def analyze_image(self, base64_image: str) -> str:
        """
        Analyze an image using OpenAI's multimodal capabilities
        
        Args:
            base64_image (str): Base64-encoded image data
            
        Returns:
            str: Image analysis results
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image in detail and describe its key "
                                + "elements, context, and any notable aspects.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise

    def design_experiment(self, hypothesis: str, papers: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Design an experiment to test a hypothesis
        
        Args:
            hypothesis (str): The hypothesis to test
            papers (list, optional): List of relevant papers for methodology reference
            
        Returns:
            dict: Experiment design details
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        # Format paper data for the prompt if available
        papers_text = ""
        if papers:
            for i, paper in enumerate(papers):
                papers_text += f"Paper {i+1}: {paper.get('title', 'Untitled')}\n"
                papers_text += f"Abstract: {paper.get('abstract', 'No abstract available')}\n\n"
        
        prompt = (
            f"Design a scientific experiment to test the following hypothesis. "
            f"Return your response as a JSON object with the following keys: "
            f"'title', 'methodology', 'variables' (with 'independent' and 'dependent' arrays), "
            f"'controls', 'expected_outcomes', and 'limitations'.\n\n"
            f"Hypothesis: {hypothesis}\n\n"
        )
        
        if papers_text:
            prompt += f"Relevant Papers:\n{papers_text}"
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "title": result.get("title", ""),
                "methodology": result.get("methodology", ""),
                "variables": result.get("variables", {"independent": [], "dependent": []}),
                "controls": result.get("controls", ""),
                "expected_outcomes": result.get("expected_outcomes", ""),
                "limitations": result.get("limitations", "")
            }
                
        except Exception as e:
            logger.error(f"Error designing experiment: {e}")
            raise
            
    def generate_image(self, text: str) -> Dict[str, str]:
        """
        Generate an image based on a text prompt using DALL-E
        
        Args:
            text (str): The text prompt for image generation
            
        Returns:
            dict: Generated image URL
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=text,
                n=1,
                size="1024x1024",
            )
            
            return {"url": response.data[0].url}
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise
            
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                
            return response.text
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise