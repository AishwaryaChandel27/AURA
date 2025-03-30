"""
Experiment Agent for AURA Research Assistant
Agent responsible for designing experiments to test hypotheses
"""

import logging
from typing import Dict, List, Any, Optional

# Import services
from services import openai_service

# Configure logging
logger = logging.getLogger(__name__)

class ExperimentAgent:
    """
    Agent responsible for designing experiments to test hypotheses
    """
    
    def __init__(self):
        """Initialize the ExperimentAgent"""
        logger.info("Initializing ExperimentAgent")
        self.initialized = True
    
    def design_experiment(self, hypothesis, papers=None):
        """
        Design an experiment to test a hypothesis
        
        Args:
            hypothesis (str): The hypothesis to test
            papers (list, optional): List of relevant papers for methodology reference
        
        Returns:
            dict: Experiment design details
        """
        logger.info(f"Designing experiment for hypothesis: {hypothesis}")
        
        try:
            # Use OpenAI service to design experiment
            experiment_design = openai_service.design_experiment({
                'hypothesis_text': hypothesis
            })
            
            return experiment_design
        except Exception as e:
            logger.error(f"Error designing experiment: {e}")
            return {
                'title': f"Experiment for testing: {hypothesis[:50]}...",
                'methodology': "Error generating methodology.",
                'variables': {},
                'controls': "Error generating controls.",
                'expected_outcomes': "Error generating expected outcomes.",
                'limitations': "Error generating limitations."
            }
    
    def evaluate_experiment(self, experiment_design, evaluation_criteria=None):
        """
        Evaluate an experiment design based on criteria like feasibility, validity, etc.
        
        Args:
            experiment_design (dict): The experiment design to evaluate
            evaluation_criteria (list, optional): Specific criteria to evaluate
        
        Returns:
            dict: Evaluation results
        """
        logger.info(f"Evaluating experiment: {experiment_design.get('title', 'Unknown experiment')}")
        
        try:
            # For a real implementation, this would use more sophisticated criteria
            # For this demo, we'll just return a simple evaluation
            
            # Check for key components
            has_methodology = bool(experiment_design.get('methodology', '').strip())
            has_variables = bool(experiment_design.get('variables', {}))
            has_controls = bool(experiment_design.get('controls', '').strip())
            has_expected_outcomes = bool(experiment_design.get('expected_outcomes', '').strip())
            
            # Calculate completeness score
            components = [has_methodology, has_variables, has_controls, has_expected_outcomes]
            completeness_score = sum(components) / len(components)
            
            # Generate evaluation
            evaluation = {
                'completeness_score': completeness_score,
                'has_methodology': has_methodology,
                'has_variables': has_variables,
                'has_controls': has_controls,
                'has_expected_outcomes': has_expected_outcomes,
                'evaluation': 'This experiment design appears to be ' + 
                             ('well-defined' if completeness_score > 0.8 else 
                              'mostly complete' if completeness_score > 0.6 else 
                              'partially defined' if completeness_score > 0.4 else 
                              'incomplete'),
                'recommendations': []
            }
            
            # Add recommendations for improvement
            if not has_methodology:
                evaluation['recommendations'].append('Add a detailed methodology section.')
            if not has_variables:
                evaluation['recommendations'].append('Define independent and dependent variables.')
            if not has_controls:
                evaluation['recommendations'].append('Specify control measures to ensure validity.')
            if not has_expected_outcomes:
                evaluation['recommendations'].append('Describe expected outcomes and their interpretation.')
            
            return evaluation
        
        except Exception as e:
            logger.error(f"Error evaluating experiment: {e}")
            return {
                'completeness_score': 0.0,
                'evaluation': 'Error evaluating experiment design.',
                'recommendations': ['Unable to provide recommendations due to an error.']
            }
    
    def suggest_measurements(self, experiment_design):
        """
        Suggest specific measurements and instruments for an experiment
        
        Args:
            experiment_design (dict): The experiment design
        
        Returns:
            dict: Suggested measurements and instruments
        """
        logger.info(f"Suggesting measurements for experiment: {experiment_design.get('title', 'Unknown experiment')}")
        
        try:
            # For a real implementation, this would use domain-specific knowledge
            # For this demo, we'll just return a template
            
            # Extract variables if available
            variables = experiment_design.get('variables', {})
            dependent_vars = variables.get('dependent', [])
            
            # Generate measurement suggestions
            measurements = []
            
            if dependent_vars:
                for var in dependent_vars:
                    measurements.append({
                        'variable': var,
                        'instrument': f"Standard instrument for measuring {var}",
                        'frequency': "Every experimental trial",
                        'data_type': "Numeric",
                        'analysis_method': "Statistical comparison between groups"
                    })
            else:
                # Default suggestion
                measurements.append({
                    'variable': "Primary outcome",
                    'instrument': "Appropriate measurement instrument",
                    'frequency': "Pre and post intervention",
                    'data_type': "Numeric",
                    'analysis_method': "Statistical comparison between groups"
                })
            
            return {
                'suggested_measurements': measurements,
                'data_collection_protocol': "Collect data systematically to ensure reliability and validity.",
                'quality_control': "Implement standard quality control procedures to minimize measurement errors."
            }
        
        except Exception as e:
            logger.error(f"Error suggesting measurements: {e}")
            return {
                'suggested_measurements': [],
                'data_collection_protocol': "Error generating protocol.",
                'quality_control': "Error generating quality control guidelines."
            }