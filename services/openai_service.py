"""
OpenAI Service for AURA Research Assistant
Handles interactions with OpenAI API
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

import openai
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service for OpenAI API interactions
    """
    
    def __init__(self):
        """Initialize the OpenAIService"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        
        # Use gpt-4o as the default model
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.default_model = "gpt-4o"
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text response from OpenAI
        
        Args:
            prompt (str): The prompt text
            max_tokens (int): Maximum tokens in the response
            
        Returns:
            str: Generated text
        """
        try:
            if not self.api_key:
                logger.warning("OPENAI_API_KEY is not set")
                return "ERROR: OpenAI API key is not set."
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error generating text: {str(e)}"
    
    def generate_structured_response(self, prompt: str) -> Dict[str, Any]:
        """
        Generate structured JSON response from OpenAI
        
        Args:
            prompt (str): The prompt text
            
        Returns:
            dict: Structured response
        """
        try:
            if not self.api_key:
                logger.warning("OPENAI_API_KEY is not set")
                return {"error": "OpenAI API key is not set."}
            
            # Request JSON output
            prompt_with_json = f"{prompt}\n\nProvide your response in valid JSON format."
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt_with_json}],
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Handle case where response isn't valid JSON
                logger.warning("OpenAI response isn't valid JSON")
                return {"error": "Invalid JSON response", "raw_response": response_text}
        
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            return {"error": f"Error generating structured response: {str(e)}"}
    
    def summarize_text(self, text: str) -> str:
        """
        Summarize text
        
        Args:
            text (str): Text to summarize
            
        Returns:
            str: Summary
        """
        prompt = f"Summarize the following academic paper:\n\n{text}\n\nProvide a comprehensive yet concise summary."
        return self.generate_text(prompt)
    
    def extract_key_points(self, text: str) -> List[str]:
        """
        Extract key points from text
        
        Args:
            text (str): Text to extract key points from
            
        Returns:
            list: List of key points
        """
        prompt = f"Extract the key points from the following text as a list:\n\n{text}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            data = json.loads(response_text)
            
            # Try to find a list of points in the response
            if "key_points" in data and isinstance(data["key_points"], list):
                return data["key_points"]
            elif "points" in data and isinstance(data["points"], list):
                return data["points"]
            else:
                # Look for any list in the response
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        return value
                
                # Fallback to text parsing
                return self._parse_list_from_text(self.generate_text(prompt))
                
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return [f"Error extracting key points: {str(e)}"]
    
    def generate_hypothesis(self, research_question: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a research hypothesis based on papers
        
        Args:
            research_question (str): The research question
            papers (list): List of paper data
            
        Returns:
            dict: Generated hypothesis, reasoning, and confidence score
        """
        # Create a prompt with research question and paper information
        papers_text = ""
        for i, paper in enumerate(papers):
            papers_text += f"Paper {i}:\n"
            papers_text += f"Title: {paper.get('title', 'Untitled')}\n"
            papers_text += f"Abstract: {paper.get('abstract', 'No abstract')}\n\n"
        
        prompt = f"""
        Research Question: {research_question}
        
        Papers:
        {papers_text}
        
        Based on the research question and the papers provided, generate a well-founded research hypothesis. Include reasoning and rate your confidence in the hypothesis on a scale of 0.0 to 1.0.
        
        Provide your response in JSON format with the following structure:
        {{
            "hypothesis": "The hypothesis statement",
            "reasoning": "Detailed reasoning behind the hypothesis",
            "confidence_score": 0.8,
            "supporting_papers": {{
                "0": "How paper 0 supports this hypothesis",
                "1": "How paper 1 supports this hypothesis",
                ...
            }}
        }}
        """
        
        return self.generate_structured_response(prompt)
    
    def design_experiment(self, hypothesis: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Design an experiment to test a hypothesis
        
        Args:
            hypothesis (str): The hypothesis to test
            papers (list): List of papers for methodology reference
            
        Returns:
            dict: Experiment design details
        """
        # Create a prompt with hypothesis and paper information
        papers_text = ""
        for i, paper in enumerate(papers):
            papers_text += f"Paper {i}:\n"
            papers_text += f"Title: {paper.get('title', 'Untitled')}\n"
            papers_text += f"Abstract: {paper.get('abstract', 'No abstract')}\n\n"
        
        prompt = f"""
        Hypothesis: {hypothesis}
        
        Papers for Methodology Reference:
        {papers_text}
        
        Design a detailed experiment to test the given hypothesis. Include methodology, variables, controls, and expected outcomes.
        
        Provide your response in JSON format with the following structure:
        {{
            "title": "Experiment title",
            "methodology": "Detailed description of the methodology",
            "variables": {{
                "independent": ["List of independent variables"],
                "dependent": ["List of dependent variables"]
            }},
            "controls": "Description of control measures",
            "expected_outcomes": "Description of expected results",
            "limitations": "Potential limitations of the experiment design"
        }}
        """
        
        return self.generate_structured_response(prompt)
    
    def _parse_list_from_text(self, text: str) -> List[str]:
        """
        Parse a list from text
        
        Args:
            text (str): Text to parse
            
        Returns:
            list: Extracted list items
        """
        lines = text.split('\n')
        items = []
        
        for line in lines:
            line = line.strip()
            # Look for numbered or bulleted list items
            if line and (line[0].isdigit() or line[0] in ['•', '-', '*']):
                # Remove the bullet or number
                clean_line = line.lstrip('0123456789.-*• \t')
                if clean_line:
                    items.append(clean_line)
        
        # If no items found, split by periods and make each sentence an item
        if not items and text:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            items = sentences[:5]  # Limit to first 5 sentences
        
        return items