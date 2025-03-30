"""
Experiment Agent for AURA Research Assistant
Agent responsible for designing experiments to test hypotheses
"""

import logging
from typing import Dict, List, Any

from services.openai_service import OpenAIService

# Set up logging
logger = logging.getLogger(__name__)

class ExperimentAgent:
    """
    Agent responsible for designing experiments to test hypotheses
    """
    
    def __init__(self):
        """Initialize the ExperimentAgent"""
        self.openai_service = OpenAIService()
    
    def design_experiment(self, hypothesis: str, papers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Design an experiment to test a hypothesis
        
        Args:
            hypothesis (str): The hypothesis to test
            papers (list, optional): List of relevant papers for methodology reference
        
        Returns:
            dict: Experiment design details
        """
        try:
            # Use default empty list if papers is None
            papers_data = papers or []
            
            # Use the OpenAI service to design the experiment
            experiment_data = self.openai_service.design_experiment(hypothesis, papers_data)
            
            return {
                'title': experiment_data.get('title', 'Untitled Experiment'),
                'methodology': experiment_data.get('methodology', ''),
                'variables': experiment_data.get('variables', {'independent': [], 'dependent': []}),
                'controls': experiment_data.get('controls', ''),
                'expected_outcomes': experiment_data.get('expected_outcomes', ''),
                'limitations': experiment_data.get('limitations', '')
            }
        
        except Exception as e:
            logger.error(f"Error designing experiment: {e}")
            return {
                'title': 'Error Designing Experiment',
                'methodology': f"Error: {str(e)}",
                'variables': {'independent': [], 'dependent': []},
                'controls': '',
                'expected_outcomes': '',
                'limitations': 'Could not design experiment due to an error.'
            }
    
    def evaluate_experiment(self, experiment_design: Dict[str, Any], evaluation_criteria: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate an experiment design based on criteria like feasibility, validity, etc.
        
        Args:
            experiment_design (dict): The experiment design to evaluate
            evaluation_criteria (list, optional): Specific criteria to evaluate
        
        Returns:
            dict: Evaluation results
        """
        try:
            # Default evaluation criteria if none provided
            if evaluation_criteria is None:
                evaluation_criteria = [
                    'feasibility', 'internal_validity', 'external_validity', 
                    'reliability', 'ethical_considerations'
                ]
            
            # Create a prompt for evaluation
            prompt = f"""
            Please evaluate the following experiment design based on these criteria: {', '.join(evaluation_criteria)}
            
            Experiment Title: {experiment_design.get('title', 'Untitled Experiment')}
            
            Methodology:
            {experiment_design.get('methodology', 'No methodology provided.')}
            
            Variables:
            Independent: {experiment_design.get('variables', {}).get('independent', [])}
            Dependent: {experiment_design.get('variables', {}).get('dependent', [])}
            
            Controls:
            {experiment_design.get('controls', 'No controls specified.')}
            
            Expected Outcomes:
            {experiment_design.get('expected_outcomes', 'No expected outcomes specified.')}
            
            Provide a critical evaluation in JSON format with the following structure:
            {
                "overall_score": Float (0-1),
                "strengths": [list of strengths],
                "weaknesses": [list of weaknesses],
                "recommendations": [list of recommendations for improvement]
            }
            """
            
            # Get evaluation from OpenAI
            evaluation = self.openai_service.generate_structured_response(prompt)
            
            return {
                'overall_score': evaluation.get('overall_score', 0.0),
                'strengths': evaluation.get('strengths', []),
                'weaknesses': evaluation.get('weaknesses', []),
                'recommendations': evaluation.get('recommendations', [])
            }
        
        except Exception as e:
            logger.error(f"Error evaluating experiment: {e}")
            return {
                'overall_score': 0.0,
                'strengths': [],
                'weaknesses': [f"Error during evaluation: {str(e)}"],
                'recommendations': ['Review the experiment design and try again.']
            }
    
    def suggest_measurements(self, experiment_design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest specific measurements and instruments for an experiment
        
        Args:
            experiment_design (dict): The experiment design
        
        Returns:
            dict: Suggested measurements and instruments
        """
        try:
            # Extract dependent variables
            dependent_vars = experiment_design.get('variables', {}).get('dependent', [])
            
            # Create a prompt for suggesting measurements
            prompt = f"""
            Based on the following experiment design, suggest appropriate measurements, instruments, and data collection methods:
            
            Experiment Title: {experiment_design.get('title', 'Untitled Experiment')}
            
            Methodology:
            {experiment_design.get('methodology', 'No methodology provided.')}
            
            Variables to measure: {dependent_vars if dependent_vars else 'No dependent variables specified.'}
            
            Provide suggestions in JSON format with the following structure:
            {{
                "measurements": [
                    {{
                        "variable": String (variable name),
                        "method": String (measurement method),
                        "instrument": String (suggested instrument),
                        "data_type": String (e.g., "continuous", "categorical", "binary"),
                        "units": String (if applicable)
                    }}
                ],
                "data_collection_procedures": String (description of procedures),
                "reliability_considerations": String (reliability considerations)
            }}
            """
            
            # Get suggestions from OpenAI
            suggestions = self.openai_service.generate_structured_response(prompt)
            
            return {
                'measurements': suggestions.get('measurements', []),
                'data_collection_procedures': suggestions.get('data_collection_procedures', ''),
                'reliability_considerations': suggestions.get('reliability_considerations', '')
            }
        
        except Exception as e:
            logger.error(f"Error suggesting measurements: {e}")
            return {
                'measurements': [],
                'data_collection_procedures': f"Error suggesting measurements: {str(e)}",
                'reliability_considerations': ''
            }