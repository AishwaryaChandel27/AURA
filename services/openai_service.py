"""
OpenAI service for AURA Research Assistant
Handles interactions with the OpenAI API
"""

import os
import json
import logging
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_completion(prompt, system_prompt=None, model="gpt-4o"):
    """
    Generate a text completion using OpenAI's API
    
    Args:
        prompt (str): The prompt to send to the API
        system_prompt (str, optional): System prompt for context
        model (str, optional): Model to use. Defaults to "gpt-4o"
        
    Returns:
        str: Generated text
    """
    # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # Do not change this unless explicitly requested by the user
    
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating OpenAI completion: {e}")
        return f"Error generating response: {str(e)}"

def analyze_paper(paper_data):
    """
    Analyze a paper using OpenAI API
    
    Args:
        paper_data (dict): Paper data with title, abstract, etc.
        
    Returns:
        dict: Analysis results
    """
    # Prepare prompt
    prompt = f"""
    Analyze the following research paper:
    
    Title: {paper_data.get('title', 'Unknown Title')}
    Authors: {', '.join(paper_data.get('authors', []))}
    Abstract: {paper_data.get('abstract', 'No abstract available')}
    
    Please provide:
    1. A summary of the paper (3-5 sentences)
    2. Key findings (bullet points)
    3. Research methods used
    4. Potential impact and significance
    5. Limitations or gaps
    
    Format your response as JSON with the following structure:
    {{
        "summary": "summary text here",
        "key_findings": ["finding 1", "finding 2", ...],
        "methods": "research methods description",
        "impact": "impact assessment",
        "limitations": "limitations description"
    }}
    """
    
    system_prompt = """
    You are a research analysis assistant. Your task is to analyze academic papers and provide clear,
    accurate summaries and insights. Focus on extracting the most important information and presenting
    it in a structured format. Always respond with valid JSON.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error analyzing paper: {e}")
        return {"error": f"Error analyzing paper: {str(e)}"}

def generate_hypotheses(papers, research_question):
    """
    Generate research hypotheses based on papers and a research question
    
    Args:
        papers (list): List of paper dictionaries
        research_question (str): The research question
        
    Returns:
        dict: Generated hypotheses and supporting evidence
    """
    # Prepare paper summaries
    paper_summaries = []
    for i, paper in enumerate(papers[:5]):  # Limit to 5 papers for token limit
        title = paper.get('title', f'Paper {i+1}')
        summary = paper.get('summary', 'No summary available')
        findings = paper.get('key_findings', [])
        
        findings_text = ""
        if findings:
            findings_text = "\n".join([f"- {finding}" for finding in findings[:5]])
            
        paper_summaries.append(f"""
        Paper: {title}
        Summary: {summary}
        Key Findings:
        {findings_text}
        """)
    
    # Prepare prompt
    prompt = f"""
    Research Question: {research_question}
    
    Based on the following paper summaries, generate 3-5 research hypotheses:
    
    {"\n".join(paper_summaries)}
    
    For each hypothesis:
    1. State the hypothesis clearly
    2. Provide reasoning based on the papers
    3. Identify supporting evidence from the papers
    4. Assign a confidence score (0.0 to 1.0)
    
    Format your response as JSON with the following structure:
    {{
        "hypotheses": [
            {{
                "hypothesis": "Hypothesis statement",
                "reasoning": "Reasoning text",
                "supporting_evidence": {{
                    "paper_titles": ["title1", "title2", ...],
                    "relevant_quotes": ["quote1", "quote2", ...]
                }},
                "confidence_score": 0.X
            }},
            ...
        ]
    }}
    """
    
    system_prompt = """
    You are a research hypothesis generator. Your task is to formulate well-reasoned research hypotheses
    based on paper summaries and a research question. Make sure the hypotheses are:
    1. Clearly stated
    2. Testable
    3. Supported by evidence from the papers
    4. Relevant to the research question
    
    Always respond with valid JSON.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error generating hypotheses: {e}")
        return {"error": f"Error generating hypotheses: {str(e)}"}

def design_experiment(hypothesis, papers=None):
    """
    Design an experiment to test a hypothesis
    
    Args:
        hypothesis (str): The hypothesis to test
        papers (list, optional): List of paper dictionaries for reference
        
    Returns:
        dict: Experiment design details
    """
    paper_references = ""
    if papers:
        paper_summaries = []
        for i, paper in enumerate(papers[:3]):  # Limit to 3 papers for token limit
            title = paper.get('title', f'Paper {i+1}')
            methods = paper.get('methods', 'Methods not specified')
            if isinstance(methods, str) and methods:
                paper_summaries.append(f"Paper: {title}\nMethods: {methods}")
        
        if paper_summaries:
            paper_references = "Reference papers and their methods:\n" + "\n\n".join(paper_summaries)
    
    # Prepare prompt
    prompt = f"""
    Design an experiment to test the following hypothesis:
    
    Hypothesis: {hypothesis}
    
    {paper_references}
    
    Please include:
    1. Experiment title
    2. Detailed methodology
    3. Independent and dependent variables
    4. Controls and experimental conditions
    5. Expected outcomes if the hypothesis is true
    6. Potential limitations
    
    Format your response as JSON with the following structure:
    {{
        "title": "Experiment title",
        "methodology": "Detailed methodology description",
        "variables": {{
            "independent": ["var1", "var2", ...],
            "dependent": ["var1", "var2", ...],
            "controlled": ["var1", "var2", ...]
        }},
        "controls": "Description of control conditions",
        "expected_outcomes": "Expected outcomes description",
        "limitations": "Potential limitations"
    }}
    """
    
    system_prompt = """
    You are an experiment design specialist. Your task is to create robust, scientific experiments
    to test research hypotheses. Ensure your designs are:
    1. Methodologically sound
    2. Properly controlled
    3. Feasible to implement
    4. Capable of producing valid results
    
    Always respond with valid JSON.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Error designing experiment: {e}")
        return {"error": f"Error designing experiment: {str(e)}"}