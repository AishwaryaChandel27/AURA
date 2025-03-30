"""
OpenAI service for AURA Research Assistant
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI configuration
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    logger.warning("OpenAI API key not found in environment variables")

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

def analyze_query(query_text: str) -> Dict[str, Any]:
    """
    Analyze a user query to determine its nature and how to respond
    
    Args:
        query_text (str): The user's query text
        
    Returns:
        dict: Analysis results
    """
    try:
        # Create system prompt
        system_prompt = """
        You are an assistant that analyzes user queries to determine how to route them.
        Specifically, you need to identify if a query is related to TensorFlow and should be
        handled by a TensorFlow-specific agent.
        
        Return a JSON object with the following fields:
        - query_type: The type of query (e.g., "research", "clarification", "tensorflow", "general")
        - tensorflow_relevance: A brief explanation of why this is or isn't relevant to TensorFlow (if applicable)
        - relevance_score: A score from 0 to 1 indicating how relevant this query is to TensorFlow
        - agent_type: The agent that should handle this query ("tensorflow" or "general")
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query_text}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse and return the result
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        # Return default values if there's an error
        return {
            "query_type": "general",
            "tensorflow_relevance": "",
            "relevance_score": 0,
            "agent_type": "general"
        }

def summarize_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary for a research paper
    
    Args:
        paper (dict): Paper information including title, authors, and abstract
        
    Returns:
        dict: Summary and key findings
    """
    try:
        # Create system prompt
        system_prompt = """
        You are a research assistant that summarizes academic papers.
        Given a paper's title, authors, and abstract, provide a concise summary and a list of key findings.
        
        Return a JSON object with the following fields:
        - summary: A concise summary of the paper (max 3 paragraphs)
        - key_findings: A list of 3-5 key findings or contributions
        """
        
        # Format paper info for the prompt
        paper_text = f"Title: {paper['title']}\n\n"
        
        if 'authors' in paper and paper['authors']:
            if isinstance(paper['authors'], list):
                paper_text += f"Authors: {', '.join(paper['authors'])}\n\n"
            else:
                paper_text += f"Authors: {paper['authors']}\n\n"
        
        if 'abstract' in paper and paper['abstract']:
            paper_text += f"Abstract: {paper['abstract']}\n\n"
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": paper_text}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse and return the result
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error summarizing paper: {e}")
        # Return minimal summary if there's an error
        return {
            "summary": f"Error generating summary for '{paper.get('title', 'unknown paper')}'.",
            "key_findings": []
        }

def generate_hypothesis(research_question: str, paper_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a research hypothesis based on a research question and paper summaries
    
    Args:
        research_question (str): The research question
        paper_summaries (list): List of paper summaries
        
    Returns:
        dict: Generated hypothesis, reasoning, and confidence score
    """
    try:
        # Create system prompt
        system_prompt = """
        You are a research assistant that generates research hypotheses.
        Given a research question and a set of paper summaries, generate a hypothesis that could be tested with TensorFlow.
        
        Return a JSON object with the following fields:
        - hypothesis_text: The generated hypothesis statement
        - reasoning: Explanation of why this hypothesis is worth testing
        - confidence_score: A score from 0 to 1 indicating your confidence in this hypothesis
        - supporting_evidence: A map of paper titles to relevant quotes or findings that support this hypothesis
        - tensorflow_approach: A brief description of how TensorFlow could be used to test this hypothesis
        """
        
        # Format input for the prompt
        input_text = f"Research Question: {research_question}\n\n"
        input_text += "Paper Summaries:\n\n"
        
        for i, paper in enumerate(paper_summaries):
            input_text += f"Paper {i+1}: {paper.get('title', 'Unknown Title')}\n"
            if 'summary' in paper and paper['summary']:
                # Handle different summary formats
                if isinstance(paper['summary'], dict) and 'summary_text' in paper['summary']:
                    input_text += f"Summary: {paper['summary']['summary_text']}\n"
                elif isinstance(paper['summary'], dict) and 'text' in paper['summary']:
                    input_text += f"Summary: {paper['summary']['text']}\n"
                else:
                    input_text += f"Summary: {paper['summary']}\n"
            
            # Add key findings if available
            if 'key_findings' in paper.get('summary', {}) and paper['summary']['key_findings']:
                input_text += "Key Findings:\n"
                for finding in paper['summary']['key_findings']:
                    input_text += f"- {finding}\n"
            
            input_text += "\n"
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse and return the result
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        # Return a minimal response if there's an error
        return {
            "hypothesis_text": f"Error generating hypothesis for '{research_question}'.",
            "reasoning": "An error occurred during hypothesis generation.",
            "confidence_score": 0.0,
            "supporting_evidence": {},
            "tensorflow_approach": "N/A"
        }

def design_experiment(hypothesis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Design an experiment to test a hypothesis using TensorFlow
    
    Args:
        hypothesis (dict): Hypothesis information
        
    Returns:
        dict: Experiment design
    """
    try:
        # Create system prompt
        system_prompt = """
        You are a research assistant that designs experiments using TensorFlow.
        Given a hypothesis, design an experiment that could test it.
        
        Return a JSON object with the following fields:
        - title: A title for the experiment
        - methodology: Description of the experimental methodology
        - variables: JSON object with "independent" and "dependent" variables (each a list of strings)
        - controls: Description of control measures
        - expected_outcomes: Expected results if the hypothesis is correct
        - limitations: Potential limitations or challenges
        - model_architecture: Brief description of a TensorFlow model architecture suitable for this experiment
        - tensorflow_approach: Detailed description of how TensorFlow would be used
        """
        
        # Format hypothesis for the prompt
        hypothesis_text = hypothesis.get('hypothesis_text', '')
        reasoning = hypothesis.get('reasoning', '')
        
        input_text = f"Hypothesis: {hypothesis_text}\n\n"
        
        if reasoning:
            input_text += f"Reasoning: {reasoning}\n\n"
        
        if 'supporting_evidence' in hypothesis:
            input_text += "Supporting Evidence:\n"
            for source, evidence in hypothesis['supporting_evidence'].items():
                input_text += f"- {source}: {evidence}\n"
        
        if 'tensorflow_approach' in hypothesis:
            input_text += f"\nSuggested TensorFlow Approach: {hypothesis['tensorflow_approach']}\n"
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse and return the result
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error designing experiment: {e}")
        # Return a minimal response if there's an error
        return {
            "title": f"Error designing experiment for hypothesis",
            "methodology": "An error occurred during experiment design.",
            "variables": {"independent": [], "dependent": []},
            "controls": "",
            "expected_outcomes": "",
            "limitations": "",
            "model_architecture": "",
            "tensorflow_approach": ""
        }