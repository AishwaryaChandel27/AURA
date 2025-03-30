"""
OpenAI Service for AURA Research Assistant
Handles communication with OpenAI API for various NLP tasks
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

# Import the OpenAI SDK
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def summarize_paper(title: str, abstract: str) -> Dict[str, Any]:
    """
    Generate a summary for a research paper
    
    Args:
        title (str): Paper title
        abstract (str): Paper abstract
        
    Returns:
        dict: Summary and key findings
    """
    logger.info(f"Summarizing paper: {title}")
    
    try:
        # Prepare the prompt for OpenAI
        prompt = f"""
        Paper Title: {title}
        
        Abstract: {abstract}
        
        Please provide a concise summary of this research paper and extract the key findings.
        Format your response as JSON with the following structure:
        {{
            "summary": "A concise summary of the paper",
            "key_findings": ["Key finding 1", "Key finding 2", "Key finding 3", "Key finding 4", "Key finding 5"]
        }}
        Ensure the summary is no longer than 150 words and extract 3-5 key findings as bullet points.
        """
        
        # Call the OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600
        )
        
        # Parse the response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Ensure the expected structure
        if "summary" not in result or "key_findings" not in result:
            logger.warning("OpenAI response missing expected fields")
            return {
                "summary": f"Summary of {title}",
                "key_findings": ["No key findings identified"]
            }
        
        return result
    
    except Exception as e:
        logger.error(f"Error summarizing paper: {e}")
        return {
            "summary": f"Error generating summary for: {title}",
            "key_findings": ["Error processing paper"]
        }

def generate_hypothesis(research_question: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a hypothesis based on a research question and paper data
    
    Args:
        research_question (str): The research question
        papers (list): List of paper data
        
    Returns:
        dict: Generated hypothesis
    """
    logger.info(f"Generating hypothesis for question: {research_question}")
    
    try:
        # Prepare paper summaries for the prompt
        paper_info = []
        for i, paper in enumerate(papers[:5]):  # Limit to 5 papers to stay within token limits
            summary_text = ""
            if "summary" in paper and paper["summary"]:
                summary_text = paper["summary"].get("summary_text", "")
            
            paper_info.append(f"""
            Paper {i+1}: {paper.get('title', 'Untitled')}
            Abstract: {paper.get('abstract', 'No abstract available')}
            Summary: {summary_text}
            """)
        
        # Join paper information
        papers_text = "\n".join(paper_info)
        
        # Prepare the prompt for OpenAI
        prompt = f"""
        Research Question: {research_question}
        
        Available Papers:
        {papers_text}
        
        Based on the research question and the available papers, please generate a hypothesis. 
        Include reasoning and a confidence score.
        
        Format your response as JSON with the following structure:
        {{
            "hypothesis_text": "The clear hypothesis statement",
            "reasoning": "Reasoning behind this hypothesis based on the papers",
            "confidence_score": 0.8,  # A number between 0 and 1
            "supporting_evidence": {{
                "paper1": "Relevant quote or finding from paper 1",
                "paper2": "Relevant quote or finding from paper 2"
            }}
        }}
        """
        
        # Call the OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=800
        )
        
        # Parse the response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Ensure the expected structure
        if "hypothesis_text" not in result:
            logger.warning("OpenAI response missing expected fields")
            return {
                "hypothesis_text": f"Hypothesis for: {research_question}",
                "reasoning": "Insufficient data to generate reasoning",
                "confidence_score": 0.3,
                "supporting_evidence": {}
            }
        
        return result
    
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return {
            "hypothesis_text": f"Error generating hypothesis for: {research_question}",
            "reasoning": "An error occurred during hypothesis generation",
            "confidence_score": 0.1,
            "supporting_evidence": {}
        }

def design_experiment(hypothesis: str) -> Dict[str, Any]:
    """
    Design an experiment to test a hypothesis
    
    Args:
        hypothesis (str): The hypothesis to test
        
    Returns:
        dict: Experiment design details
    """
    logger.info(f"Designing experiment for hypothesis: {hypothesis}")
    
    try:
        # Prepare the prompt for OpenAI
        prompt = f"""
        Hypothesis: {hypothesis}
        
        Please design an experiment to test this hypothesis. 
        Include methodology, variables, controls, expected outcomes, and limitations.
        
        Format your response as JSON with the following structure:
        {{
            "experiment_title": "Title of the experiment",
            "methodology": "Detailed methodology",
            "variables": {{
                "independent": ["Variable 1", "Variable 2"],
                "dependent": ["Variable 3", "Variable 4"]
            }},
            "controls": "Control measures",
            "expected_outcomes": "Expected results",
            "limitations": "Potential limitations"
        }}
        """
        
        # Call the OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=1000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Ensure the expected structure
        if "experiment_title" not in result or "methodology" not in result:
            logger.warning("OpenAI response missing expected fields")
            return {
                "experiment_title": f"Experiment for: {hypothesis[:50]}...",
                "methodology": "No methodology provided",
                "variables": {"independent": [], "dependent": []},
                "controls": "No controls specified",
                "expected_outcomes": "No expected outcomes provided",
                "limitations": "No limitations identified"
            }
        
        return result
    
    except Exception as e:
        logger.error(f"Error designing experiment: {e}")
        return {
            "experiment_title": f"Error designing experiment for: {hypothesis[:50]}...",
            "methodology": "An error occurred during experiment design",
            "variables": {"independent": [], "dependent": []},
            "controls": "Not specified due to error",
            "expected_outcomes": "Not available",
            "limitations": "Could not complete design"
        }

def analyze_query(query_text: str) -> Dict[str, Any]:
    """
    Analyze a query to determine its type and relevance to TensorFlow
    
    Args:
        query_text (str): The query to analyze
        
    Returns:
        dict: Query analysis results
    """
    logger.info(f"Analyzing query: {query_text}")
    
    try:
        # Prepare the prompt for OpenAI
        prompt = f"""
        Query: {query_text}
        
        Please analyze this query to determine:
        1. The type of query (e.g., paper_search, summarization, hypothesis, experiment, visualization, tensorflow_specific)
        2. Its relevance to TensorFlow and machine learning research (score from 0 to 1)
        
        Format your response as JSON with the following structure:
        {{
            "query_type": "paper_search",
            "relevance_score": 0.85,
            "tensorflow_specific_terms": ["term1", "term2"]
        }}
        """
        
        # Call the OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse the response
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Ensure the expected structure
        if "query_type" not in result or "relevance_score" not in result:
            logger.warning("OpenAI response missing expected fields")
            return {
                "query_type": "general",
                "relevance_score": 0.5,
                "tensorflow_specific_terms": []
            }
        
        return result
    
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        return {
            "query_type": "general",
            "relevance_score": 0.0,
            "tensorflow_specific_terms": []
        }