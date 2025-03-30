import logging
import json
from services.openai_service import design_experiment
from services.memory_service import MemoryService

logger = logging.getLogger(__name__)

class ExperimentAgent:
    """
    Agent responsible for designing experiments to test hypotheses
    """
    
    def __init__(self):
        self.memory_service = MemoryService()
    
    def design_experiment(self, hypothesis, papers=None):
        """
        Design an experiment to test a hypothesis
        
        Args:
            hypothesis (str): The hypothesis to test
            papers (list, optional): List of relevant papers for methodology reference
        
        Returns:
            dict: Experiment design details
        """
        try:
            logger.info(f"Designing experiment for hypothesis: {hypothesis[:50]}...")
            
            # Process relevant papers for methodological reference
            relevant_papers_text = []
            
            if papers:
                for paper in papers:
                    # Get paper details
                    title = paper.get('title', '')
                    abstract = paper.get('abstract', '')
                    methodology = ""
                    
                    # Try to extract methodology from paper summary if available
                    if paper.get('summary'):
                        if isinstance(paper['summary'], dict):
                            methodology = paper['summary'].get('methodology', '')
                        elif isinstance(paper['summary'], str):
                            # Try to find methodology section in the summary
                            summary_lines = paper['summary'].split('\n')
                            for i, line in enumerate(summary_lines):
                                if 'method' in line.lower() and i < len(summary_lines) - 1:
                                    methodology = summary_lines[i+1]
                    
                    # Format paper reference
                    paper_text = f"Paper: {title}\nAbstract: {abstract}"
                    if methodology:
                        paper_text += f"\nMethodology: {methodology}"
                    
                    relevant_papers_text.append(paper_text)
            
            # Design experiment using OpenAI
            experiment_result = design_experiment(hypothesis, relevant_papers_text)
            
            # Store experiment design in memory
            if experiment_result and 'error' not in experiment_result:
                # Create a unique ID for this experiment design
                import hashlib
                hyp_hash = hashlib.md5(hypothesis.encode()).hexdigest()
                doc_id = f"experiment_{hyp_hash}"
                
                # Create experiment text
                experiment_text = json.dumps(experiment_result)
                
                # Store in memory
                self.memory_service.add_document(
                    doc_id=doc_id,
                    text=experiment_text,
                    metadata={
                        'type': 'experiment',
                        'hypothesis': hypothesis,
                        'title': experiment_result.get('title', 'Experiment Design')
                    }
                )
            
            return experiment_result
            
        except Exception as e:
            logger.error(f"Error in experiment design: {str(e)}")
            return {"error": str(e)}
    
    def evaluate_experiment(self, experiment_design, evaluation_criteria=None):
        """
        Evaluate an experiment design based on criteria like feasibility, validity, etc.
        
        Args:
            experiment_design (dict): The experiment design to evaluate
            evaluation_criteria (list, optional): Specific criteria to evaluate
        
        Returns:
            dict: Evaluation results
        """
        try:
            logger.info(f"Evaluating experiment design: {experiment_design.get('title', '')}")
            
            if evaluation_criteria is None:
                evaluation_criteria = [
                    "Feasibility", "Internal Validity", "External Validity", 
                    "Statistical Power", "Ethical Considerations"
                ]
            
            # Create system prompt for evaluation
            system_prompt = """
            You are an expert in research methodology and experimental design. Evaluate the provided experiment design
            based on the specified criteria. For each criterion, provide a score from 1-10 and a detailed explanation.
            
            Your response should be in JSON format with the following structure:
            {
                "overall_score": 7.5,
                "evaluation": [
                    {
                        "criterion": "Feasibility",
                        "score": 8,
                        "explanation": "Detailed explanation of the score"
                    }
                ],
                "strengths": ["List of design strengths"],
                "weaknesses": ["List of design weaknesses"],
                "improvement_suggestions": ["List of specific improvement suggestions"]
            }
            """
            
            # Create user prompt
            experiment_json = json.dumps(experiment_design, indent=2)
            criteria_list = ", ".join(evaluation_criteria)
            
            prompt = f"Experiment Design:\n{experiment_json}\n\nPlease evaluate this experiment design based on the following criteria: {criteria_list}"
            
            # Use OpenAI service to evaluate
            from services.openai_service import generate_completion
            evaluation_result = generate_completion(prompt, system_prompt, json_response=True)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error in experiment evaluation: {str(e)}")
            return {"error": str(e)}
    
    def suggest_measurements(self, experiment_design):
        """
        Suggest specific measurements and instruments for an experiment
        
        Args:
            experiment_design (dict): The experiment design
        
        Returns:
            dict: Suggested measurements and instruments
        """
        try:
            logger.info(f"Suggesting measurements for experiment: {experiment_design.get('title', '')}")
            
            # Create system prompt for measurement suggestions
            system_prompt = """
            You are an expert in research methodology and measurement. Based on the provided experiment design,
            suggest specific measurements, scales, instruments, and data collection methods that would be appropriate.
            
            Your response should be in JSON format with the following structure:
            {
                "variables": [
                    {
                        "variable": "Name of the variable",
                        "type": "Independent/Dependent/Control",
                        "measurement_approach": "How to measure this variable",
                        "instruments": ["Specific instruments or scales to use"],
                        "data_type": "Nominal/Ordinal/Interval/Ratio",
                        "justification": "Why this measurement approach is appropriate"
                    }
                ],
                "data_collection_methods": ["List of data collection methods"],
                "analysis_techniques": ["List of suggested analysis techniques"],
                "potential_confounds": ["List of potential confounding variables to control"],
                "reliability_considerations": ["Suggestions for ensuring measurement reliability"]
            }
            """
            
            # Create user prompt
            experiment_json = json.dumps(experiment_design, indent=2)
            
            prompt = f"Experiment Design:\n{experiment_json}\n\nPlease suggest appropriate measurements and instruments for this experiment design."
            
            # Use OpenAI service to suggest measurements
            from services.openai_service import generate_completion
            measurements_result = generate_completion(prompt, system_prompt, json_response=True)
            
            return measurements_result
            
        except Exception as e:
            logger.error(f"Error in measurement suggestion: {str(e)}")
            return {"error": str(e)}
