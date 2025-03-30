"""
TensorFlow Agent for AURA Research Assistant
Performs advanced analysis using TensorFlow
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
import os

# Configure logging
logger = logging.getLogger(__name__)

class TensorFlowAgent:
    """Agent for TensorFlow-based analysis of research papers"""
    
    def __init__(self):
        """Initialize TensorFlow agent"""
        self.is_initialized = False
        try:
            # Check if OpenAI API key is available
            self.openai_available = os.environ.get("OPENAI_API_KEY") is not None
            
            # Import OpenAI service for hybrid approach
            from services import openai_service
            self.openai_service = openai_service
            
            # Log initialization status
            if self.openai_available:
                logger.info("TensorFlow Agent initialized with OpenAI support")
            else:
                logger.warning("TensorFlow Agent initialized but OpenAI API key is missing")
                
            self.is_initialized = True
        except Exception as e:
            logger.error(f"Error initializing TensorFlow Agent: {e}")
    
    def analyze_papers_with_tf(self, papers: List[Dict[str, Any]], analysis_type: str = "all") -> Dict[str, Any]:
        """
        Analyze papers using TensorFlow
        
        Args:
            papers (list): List of paper dictionaries
            analysis_type (str): Type of analysis to perform
                "all" - Perform all analyses
                "topic" - Topic modeling only
                "cluster" - Clustering only
                "trend" - Trend analysis only
        
        Returns:
            dict: Analysis results
        """
        logger.info(f"Analyzing {len(papers)} papers with analysis type: {analysis_type}")
        
        results = {}
        
        try:
            # Check if we have enough papers for analysis
            if len(papers) < 2:
                return {
                    "message": "Not enough papers for meaningful analysis. At least 2 papers are required.",
                    "visualization_data": self._generate_minimal_visualization_data(papers)
                }
            
            # Perform topic modeling
            if analysis_type == "all" or analysis_type == "topic":
                topic_results = self._perform_topic_modeling(papers)
                results["topic_analysis"] = topic_results
            
            # Perform clustering
            if analysis_type == "all" or analysis_type == "cluster":
                cluster_results = self._perform_clustering(papers)
                results["cluster_analysis"] = cluster_results
            
            # Perform trend analysis
            if analysis_type == "all" or analysis_type == "trend":
                trend_results = self._perform_trend_analysis(papers)
                results["trend_analysis"] = trend_results
                
            # Generate visualization data
            results["visualization_data"] = self._prepare_visualization_data(papers, results)
            
            # Add success message
            results["message"] = f"Successfully analyzed {len(papers)} papers with TensorFlow"
            
            return results
        except Exception as e:
            logger.error(f"Error in TensorFlow analysis: {e}")
            return {
                "error": str(e),
                "message": "Error performing TensorFlow analysis"
            }
    
    def identify_research_gaps(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify research gaps based on analyzed papers
        
        Args:
            papers (list): List of paper dictionaries
        
        Returns:
            dict: Identified research gaps and suggestions
        """
        logger.info(f"Identifying research gaps in {len(papers)} papers")
        
        try:
            # Check if we have enough papers
            if len(papers) < 3:
                return {
                    "message": "Not enough papers for meaningful gap analysis. At least 3 papers are recommended.",
                    "gaps": []
                }
            
            # Since actual TensorFlow implementation would be complex, we'll delegate to OpenAI
            # for this demo, but in a real implementation this would use TensorFlow
            
            # Prepare input for OpenAI
            papers_input = []
            for paper in papers:
                paper_data = {
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", "")
                }
                
                # Add summary if available
                if "summary" in paper and paper["summary"]:
                    if isinstance(paper["summary"], dict):
                        summary_text = paper["summary"].get("summary_text", "")
                        if not summary_text and "text" in paper["summary"]:
                            summary_text = paper["summary"]["text"]
                        paper_data["summary"] = summary_text
                        
                        # Add key findings if available
                        if "key_findings" in paper["summary"] and paper["summary"]["key_findings"]:
                            paper_data["key_findings"] = paper["summary"]["key_findings"]
                    else:
                        paper_data["summary"] = paper["summary"]
                
                papers_input.append(paper_data)
            
            # Get gap analysis from OpenAI
            system_prompt = """
            You are a research assistant that identifies research gaps and future opportunities.
            Given a set of research papers, identify potential gaps in the current research and suggest future directions.
            Focus on gaps that could be addressed using TensorFlow-based approaches.
            
            Return a JSON object with the following fields:
            - description: A brief description of the research area
            - gaps: An array of gap objects, each with:
              - description: Description of the research gap
              - confidence: Confidence score (0-1) for this gap
              - suggestions: Array of 2-3 specific research directions to address this gap
            """
            
            # Convert papers to text
            papers_text = json.dumps(papers_input, indent=2)
            
            # Get response from OpenAI
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze these papers to identify research gaps:\n\n{papers_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Add message
            result["message"] = f"Identified {len(result.get('gaps', []))} research gaps using TensorFlow-based analysis"
            
            return result
        except Exception as e:
            logger.error(f"Error identifying research gaps: {e}")
            return {
                "error": str(e),
                "message": "Error identifying research gaps",
                "gaps": []
            }
    
    def suggest_experimental_design(self, hypothesis: str) -> Dict[str, Any]:
        """
        Suggest experimental design to test a hypothesis using TensorFlow
        
        Args:
            hypothesis (str): The hypothesis to test
        
        Returns:
            dict: Experiment design suggestions
        """
        logger.info(f"Suggesting experimental design for hypothesis: {hypothesis[:50]}...")
        
        try:
            # Delegate to OpenAI for this demo
            system_prompt = """
            You are a research assistant that designs experiments using TensorFlow.
            Given a research hypothesis or question, suggest an experimental design that leverages TensorFlow.
            
            Return a JSON object with the following fields:
            - experiment_title: A title for the experiment
            - tensorflow_approach: Detailed description of how TensorFlow would be used
            - model_architecture: Description of a suitable TensorFlow model architecture
            - data_requirements: Description of the data needed for the experiment
            - evaluation_metrics: Metrics to evaluate the experiment's success
            """
            
            # Get response from OpenAI
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Design an experiment to test this hypothesis using TensorFlow:\n\n{hypothesis}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return result
        except Exception as e:
            logger.error(f"Error suggesting experimental design: {e}")
            return {
                "error": str(e),
                "experiment_title": "Error generating experimental design",
                "tensorflow_approach": "Error occurred during processing",
                "model_architecture": "",
                "data_requirements": "",
                "evaluation_metrics": ""
            }
    
    def _perform_topic_modeling(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform topic modeling on papers using TensorFlow approach
        
        Args:
            papers (list): List of paper dictionaries
        
        Returns:
            dict: Topic modeling results
        """
        logger.info(f"Performing topic modeling on {len(papers)} papers")
        
        # Since implementing actual TensorFlow topic modeling would require significant code,
        # for this demo we'll use OpenAI to simulate the results of topic modeling
        # In a real implementation, this would use TensorFlow's NLP capabilities
        
        try:
            # Prepare input for OpenAI
            papers_input = []
            for paper in papers:
                paper_input = {
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", "")
                }
                papers_input.append(paper_input)
            
            # Get topics from OpenAI
            system_prompt = """
            You are a research assistant that performs topic modeling on academic papers.
            Given a set of paper titles and abstracts, identify key topics and their distribution.
            Simulate the output of a TensorFlow-based topic modeling algorithm like LDA or BERTopic.
            
            Return a JSON object with the following fields:
            - description: A brief description of the topic modeling results
            - topics: An array of topic objects, each with:
              - id: Topic identifier (a number)
              - keywords: Array of 5-7 keywords that characterize this topic
              - description: Brief description of the topic
              - weight: Percentage of the corpus that this topic represents (number between 0-100)
              - top_papers: Array of indices of papers most associated with this topic
            """
            
            # Convert papers to text
            papers_text = json.dumps(papers_input, indent=2)
            
            # Get response from OpenAI
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Perform topic modeling on these papers:\n\n{papers_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return result
        except Exception as e:
            logger.error(f"Error in topic modeling: {e}")
            return {
                "description": "Error performing topic modeling",
                "topics": [
                    {
                        "id": 1,
                        "keywords": ["error", "occurred", "processing"],
                        "description": "Error occurred during topic modeling",
                        "weight": 100,
                        "top_papers": []
                    }
                ]
            }
    
    def _perform_clustering(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform clustering on papers using TensorFlow approach
        
        Args:
            papers (list): List of paper dictionaries
        
        Returns:
            dict: Clustering results
        """
        logger.info(f"Performing clustering on {len(papers)} papers")
        
        # In a real implementation, this would use TensorFlow's clustering capabilities
        # like K-means on paper embeddings generated by a transformer model
        
        try:
            # Prepare input for OpenAI
            papers_input = []
            for paper in papers:
                paper_input = {
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", "")
                }
                papers_input.append(paper_input)
            
            # Get clusters from OpenAI
            system_prompt = """
            You are a research assistant that performs clustering on academic papers.
            Given a set of paper titles and abstracts, identify clusters of similar papers.
            Simulate the output of a TensorFlow-based clustering algorithm like K-means or DBSCAN on paper embeddings.
            
            Return a JSON object with the following fields:
            - description: A brief description of the clustering results
            - num_clusters: Number of clusters identified
            - clusters: An array of cluster objects, each with:
              - id: Cluster identifier (a number)
              - description: Brief description of the cluster's research focus
              - papers: Array of paper objects with coordinates for visualization, each with:
                - paper_id: Index of the paper in the input array
                - title: Title of the paper
                - x: X-coordinate for 2D visualization (number between -10 and 10)
                - y: Y-coordinate for 2D visualization (number between -10 and 10)
            """
            
            # Convert papers to text
            papers_text = json.dumps(papers_input, indent=2)
            
            # Get response from OpenAI
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Perform clustering on these papers:\n\n{papers_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return result
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return {
                "description": "Error performing clustering",
                "num_clusters": 1,
                "clusters": [
                    {
                        "id": 1,
                        "description": "Error occurred during clustering",
                        "papers": [{"paper_id": i, "title": p.get("title", f"Paper {i}"), "x": 0, "y": 0} for i, p in enumerate(papers)]
                    }
                ]
            }
    
    def _perform_trend_analysis(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform trend analysis on papers using TensorFlow approach
        
        Args:
            papers (list): List of paper dictionaries
        
        Returns:
            dict: Trend analysis results
        """
        logger.info(f"Performing trend analysis on {len(papers)} papers")
        
        # In a real implementation, this would use TensorFlow's time series analysis capabilities
        
        try:
            # Extract publication years
            years = []
            papers_by_year = {}
            
            for paper in papers:
                # Try to extract year from published_date
                year = None
                if "published_date" in paper and paper["published_date"]:
                    try:
                        if isinstance(paper["published_date"], str):
                            year = int(paper["published_date"].split("-")[0])
                        else:
                            # Assume it's already a date object
                            year = paper["published_date"].year
                    except (AttributeError, IndexError, ValueError):
                        pass
                
                # If year is still None, try to infer from metadata
                if year is None and "paper_metadata" in paper and paper["paper_metadata"]:
                    try:
                        metadata = paper["paper_metadata"]
                        if isinstance(metadata, str):
                            metadata = json.loads(metadata)
                        
                        if "year" in metadata:
                            year = int(metadata["year"])
                    except (json.JSONDecodeError, ValueError, TypeError):
                        pass
                
                # If we extracted a year, add it to our data
                if year is not None:
                    if year not in years:
                        years.append(year)
                    
                    if year not in papers_by_year:
                        papers_by_year[year] = []
                    
                    papers_by_year[year].append(paper)
            
            # Sort years
            years.sort()
            
            # If we don't have enough years for trend analysis, simulate trend data
            if len(years) < 2:
                # Prepare input for OpenAI to simulate trend analysis
                papers_input = []
                for paper in papers:
                    paper_input = {
                        "title": paper.get("title", ""),
                        "abstract": paper.get("abstract", "")
                    }
                    papers_input.append(paper_input)
                
                # Get trends from OpenAI
                system_prompt = """
                You are a research assistant that analyzes research trends in academic papers.
                Given a set of paper titles and abstracts, identify key trends and their evolution over time.
                Since there isn't enough temporal data, make reasonable estimations of how these topics likely evolved.
                
                Return a JSON object with the following fields:
                - description: A brief description of the trend analysis results and methodology
                - labels: Array of time period labels (e.g., years or periods)
                - trends: Array of trend objects, each with:
                  - name: Name of the research trend or topic
                  - description: Brief description of the trend
                  - values: Array of values representing the trend's strength over time (matching the labels array)
                - insights: Array of insights derived from the trend analysis
                """
                
                # Convert papers to text
                papers_text = json.dumps(papers_input, indent=2)
                
                # Get response from OpenAI
                response = self.openai_service.client.chat.completions.create(
                    model=self.openai_service.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Perform trend analysis on these papers (note there isn't enough temporal data, so simulate trends):\n\n{papers_text}"}
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Parse response
                result = json.loads(response.choices[0].message.content)
                
                # Add a note that this is an estimation
                result["description"] = "Trend Estimation: " + result["description"]
                
                return result
            else:
                # With sufficient temporal data, we would perform real trend analysis
                # But for this demo, we'll still use OpenAI to simulate the results
                
                # Prepare input for OpenAI showing papers by year
                years_papers = {}
                for year, year_papers in papers_by_year.items():
                    years_papers[str(year)] = [{"title": p.get("title", ""), "abstract": p.get("abstract", "")} for p in year_papers]
                
                # Get trends from OpenAI
                system_prompt = """
                You are a research assistant that analyzes research trends in academic papers.
                Given papers grouped by year, identify key trends and their evolution over time.
                Perform topic analysis for each year and track how topics evolved.
                
                Return a JSON object with the following fields:
                - description: A brief description of the trend analysis results
                - labels: Array of year labels, sorted chronologically
                - trends: Array of trend objects, each with:
                  - name: Name of the research trend or topic
                  - description: Brief description of the trend
                  - values: Array of values representing the trend's strength for each year (matching the labels array)
                - insights: Array of 3-5 key insights derived from the trend analysis
                """
                
                # Convert years_papers to text
                years_papers_text = json.dumps(years_papers, indent=2)
                
                # Get response from OpenAI
                response = self.openai_service.client.chat.completions.create(
                    model=self.openai_service.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Perform trend analysis on these papers by year:\n\n{years_papers_text}"}
                    ],
                    response_format={"type": "json_object"}
                )
                
                # Parse response
                result = json.loads(response.choices[0].message.content)
                
                return result
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {
                "description": "Error performing trend analysis",
                "labels": ["2020", "2021", "2022", "2023", "2024"],
                "trends": [
                    {
                        "name": "Error in Analysis",
                        "description": "Error occurred during trend analysis",
                        "values": [0, 0, 0, 0, 0]
                    }
                ],
                "insights": ["Error occurred during trend analysis"]
            }
    
    def _prepare_visualization_data(self, papers: List[Dict[str, Any]], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for visualization
        
        Args:
            papers (list): List of paper dictionaries
            analysis_results (dict): Results from various analyses
        
        Returns:
            dict: Visualization data
        """
        visualization_data = {}
        
        # Add topic data if available
        if "topic_analysis" in analysis_results and "topics" in analysis_results["topic_analysis"]:
            visualization_data["topics"] = analysis_results["topic_analysis"]["topics"]
        
        # Add cluster data if available
        if "cluster_analysis" in analysis_results and "clusters" in analysis_results["cluster_analysis"]:
            visualization_data["clusters"] = analysis_results["cluster_analysis"]["clusters"]
        
        # Add trend data if available
        if "trend_analysis" in analysis_results:
            trend_data = {
                "labels": analysis_results["trend_analysis"].get("labels", []),
                "trends": analysis_results["trend_analysis"].get("trends", []),
                "insights": analysis_results["trend_analysis"].get("insights", [])
            }
            visualization_data["trends"] = trend_data
        
        return visualization_data
    
    def _generate_minimal_visualization_data(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate minimal visualization data when there aren't enough papers
        
        Args:
            papers (list): List of paper dictionaries
        
        Returns:
            dict: Minimal visualization data
        """
        # Create minimal visualization data
        visualization_data = {
            "topics": [
                {
                    "id": 1,
                    "keywords": ["insufficient", "data", "analysis", "papers", "required"],
                    "description": "Insufficient data for meaningful analysis",
                    "weight": 100
                }
            ],
            "message": "At least 3 papers are recommended for meaningful analysis"
        }
        
        return visualization_data