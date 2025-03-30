"""
Agents package for AURA Research Assistant
"""

# Import all agent classes for easy access
from agents.agent_controller import AgentController
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.summarization_agent import SummarizationAgent
from agents.hypothesis_agent import HypothesisAgent  
from agents.experiment_agent import ExperimentAgent
from agents.tensorflow_agent import TensorFlowAgent

__all__ = [
    'AgentController',
    'DataRetrievalAgent',
    'SummarizationAgent',
    'HypothesisAgent',
    'ExperimentAgent',
    'TensorFlowAgent'
]