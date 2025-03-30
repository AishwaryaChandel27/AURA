"""
Export Service for AURA Research Assistant
"""

import logging
import json
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class ExportService:
    """
    Service for exporting research data in different formats
    """
    
    def __init__(self):
        """Initialize the ExportService"""
        logger.info("Initializing ExportService")
        
        # Create exports directory if it doesn't exist
        self.exports_dir = "exports"
        if not os.path.exists(self.exports_dir):
            os.makedirs(self.exports_dir)
    
    def export_to_json(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export data to a JSON file
        
        Args:
            data (dict): The data to export
            filename (str, optional): Custom filename
            
        Returns:
            str: Path to the exported file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Create full path
            filepath = os.path.join(self.exports_dir, filename)
            
            # Export the data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_to_markdown(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export data to a Markdown file
        
        Args:
            data (dict): The data to export
            filename (str, optional): Custom filename
            
        Returns:
            str: Path to the exported file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.md"
            
            # Ensure .md extension
            if not filename.endswith('.md'):
                filename += '.md'
            
            # Create full path
            filepath = os.path.join(self.exports_dir, filename)
            
            # Convert data to Markdown
            markdown_content = self._convert_to_markdown(data)
            
            # Export the markdown
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            raise
    
    def _convert_to_markdown(self, data: Dict[str, Any], level: int = 1) -> str:
        """
        Convert data to Markdown format
        
        Args:
            data (dict): The data to convert
            level (int): Current heading level
            
        Returns:
            str: Markdown content
        """
        markdown = ""
        
        # Handle project data specially
        if "title" in data and level == 1:
            markdown += f"# {data['title']}\n\n"
            
            if "description" in data:
                markdown += f"{data['description']}\n\n"
            
            if "created_at" in data:
                created_at = data['created_at']
                if isinstance(created_at, str):
                    markdown += f"Created: {created_at}\n\n"
            
            if "updated_at" in data:
                updated_at = data['updated_at']
                if isinstance(updated_at, str):
                    markdown += f"Last updated: {updated_at}\n\n"
        
        # Handle papers
        if "papers" in data:
            markdown += f"{'#' * level} Papers\n\n"
            
            for i, paper in enumerate(data["papers"]):
                markdown += f"### {i+1}. {paper.get('title', 'Untitled Paper')}\n\n"
                
                if "authors" in paper:
                    authors = paper["authors"]
                    if isinstance(authors, list):
                        author_names = [a.get("name", "") for a in authors if isinstance(a, dict)]
                        markdown += f"**Authors:** {', '.join(author_names)}\n\n"
                    else:
                        markdown += f"**Authors:** {authors}\n\n"
                
                if "abstract" in paper:
                    markdown += f"**Abstract:** {paper['abstract']}\n\n"
                
                if "url" in paper:
                    markdown += f"**URL:** [{paper['url']}]({paper['url']})\n\n"
                
                if "published_date" in paper:
                    markdown += f"**Published:** {paper['published_date']}\n\n"
                
                markdown += "---\n\n"
        
        # Handle hypothesis
        if "hypothesis" in data:
            markdown += f"{'#' * level} Hypothesis\n\n"
            
            hypothesis = data["hypothesis"]
            if isinstance(hypothesis, dict):
                if "hypothesis_text" in hypothesis:
                    markdown += f"**Hypothesis:** {hypothesis['hypothesis_text']}\n\n"
                
                if "reasoning" in hypothesis:
                    markdown += f"**Reasoning:** {hypothesis['reasoning']}\n\n"
                
                if "confidence_score" in hypothesis:
                    markdown += f"**Confidence Score:** {hypothesis['confidence_score']}\n\n"
            else:
                markdown += f"{hypothesis}\n\n"
        
        # Handle experiment
        if "experiment" in data:
            markdown += f"{'#' * level} Experiment Design\n\n"
            
            experiment = data["experiment"]
            if isinstance(experiment, dict):
                if "title" in experiment:
                    markdown += f"**Title:** {experiment['title']}\n\n"
                
                if "methodology" in experiment:
                    markdown += f"**Methodology:**\n\n{experiment['methodology']}\n\n"
                
                if "variables" in experiment and isinstance(experiment["variables"], dict):
                    markdown += "**Variables:**\n\n"
                    
                    if "independent" in experiment["variables"]:
                        markdown += "Independent Variables:\n"
                        for var in experiment["variables"]["independent"]:
                            markdown += f"- {var}\n"
                        markdown += "\n"
                    
                    if "dependent" in experiment["variables"]:
                        markdown += "Dependent Variables:\n"
                        for var in experiment["variables"]["dependent"]:
                            markdown += f"- {var}\n"
                        markdown += "\n"
                
                if "expected_outcomes" in experiment:
                    markdown += f"**Expected Outcomes:**\n\n{experiment['expected_outcomes']}\n\n"
                
                if "limitations" in experiment:
                    markdown += f"**Limitations:**\n\n{experiment['limitations']}\n\n"
            else:
                markdown += f"{experiment}\n\n"
        
        # Handle other data types
        for key, value in data.items():
            if key not in ["title", "description", "created_at", "updated_at", "papers", "hypothesis", "experiment"]:
                markdown += f"{'#' * level} {key.replace('_', ' ').title()}\n\n"
                
                if isinstance(value, dict):
                    markdown += self._convert_to_markdown(value, level + 1)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            markdown += self._convert_to_markdown(item, level + 1)
                        else:
                            markdown += f"- {item}\n"
                    markdown += "\n"
                else:
                    markdown += f"{value}\n\n"
        
        return markdown