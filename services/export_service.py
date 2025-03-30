"""
Export Service for AURA Research Assistant
Handles export of research data in various formats
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Set up logging
logger = logging.getLogger(__name__)

class ExportService:
    """
    Service for exporting project data in various formats
    """
    
    def export_project(self, project, papers, hypotheses, format_type='json'):
        """
        Export project data in the specified format
        
        Args:
            project: The project object
            papers: List of paper objects
            hypotheses: List of hypothesis objects
            format_type (str): Export format ('json', 'csv', 'bibtex')
            
        Returns:
            dict: Export data
        """
        try:
            logger.info(f"Exporting project {project.id} in {format_type} format")
            
            if format_type == 'json':
                return self._export_json(project, papers, hypotheses)
            elif format_type == 'csv':
                return self._export_csv(project, papers, hypotheses)
            elif format_type == 'bibtex':
                return self._export_bibtex(project, papers)
            else:
                logger.warning(f"Unsupported export format: {format_type}")
                return {
                    'error': f"Unsupported export format: {format_type}",
                    'supported_formats': ['json', 'csv', 'bibtex']
                }
        
        except Exception as e:
            logger.error(f"Error exporting project: {e}")
            return {'error': f"Error exporting project: {str(e)}"}
    
    def _export_json(self, project, papers, hypotheses):
        """Export project data as JSON"""
        try:
            # Convert project to dict
            project_data = {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            }
            
            # Convert papers to dict
            papers_data = []
            for paper in papers:
                paper_dict = {
                    'id': paper.id,
                    'title': paper.title,
                    'authors': paper.get_authors() if hasattr(paper, 'get_authors') else [],
                    'abstract': paper.abstract,
                    'url': paper.url,
                    'pdf_url': paper.pdf_url,
                    'published_date': paper.published_date.isoformat() if paper.published_date else None,
                    'source': paper.source,
                    'metadata': paper.get_metadata() if hasattr(paper, 'get_metadata') else {}
                }
                
                # Add summary if available
                if hasattr(paper, 'summary') and paper.summary:
                    paper_dict['summary'] = {
                        'summary_text': paper.summary.summary_text,
                        'key_findings': paper.summary.get_key_findings() if hasattr(paper.summary, 'get_key_findings') else []
                    }
                
                papers_data.append(paper_dict)
            
            # Convert hypotheses to dict
            hypotheses_data = []
            for hypothesis in hypotheses:
                hypothesis_dict = {
                    'id': hypothesis.id,
                    'hypothesis_text': hypothesis.hypothesis_text,
                    'reasoning': hypothesis.reasoning,
                    'confidence_score': hypothesis.confidence_score,
                    'supporting_evidence': hypothesis.get_supporting_evidence() if hasattr(hypothesis, 'get_supporting_evidence') else {},
                    'created_at': hypothesis.created_at.isoformat() if hypothesis.created_at else None
                }
                
                # Add experiments if available
                if hasattr(hypothesis, 'experiments') and hypothesis.experiments:
                    hypothesis_dict['experiments'] = []
                    for experiment in hypothesis.experiments:
                        experiment_dict = {
                            'id': experiment.id,
                            'title': experiment.title,
                            'methodology': experiment.methodology,
                            'variables': experiment.get_variables() if hasattr(experiment, 'get_variables') else {},
                            'controls': experiment.controls,
                            'expected_outcomes': experiment.expected_outcomes,
                            'limitations': experiment.limitations
                        }
                        hypothesis_dict['experiments'].append(experiment_dict)
                
                hypotheses_data.append(hypothesis_dict)
            
            # Create the export data
            export_data = {
                'project': project_data,
                'papers': papers_data,
                'hypotheses': hypotheses_data,
                'export_date': datetime.utcnow().isoformat(),
                'format': 'json'
            }
            
            return export_data
        
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return {'error': f"Error exporting to JSON: {str(e)}"}
    
    def _export_csv(self, project, papers, hypotheses):
        """Export project data as CSV (in JSON format for API response)"""
        try:
            # For API response, return JSON with CSV content as strings
            
            # Create CSV strings
            papers_csv = "id,title,authors,published_date,source,url\n"
            for paper in papers:
                authors = paper.get_authors() if hasattr(paper, 'get_authors') else []
                if authors and isinstance(authors[0], dict):
                    author_names = [a.get('name', '') for a in authors]
                    authors_text = '; '.join(author_names)
                else:
                    authors_text = '; '.join(authors) if authors else ''
                
                # Escape quotes in text fields
                title = paper.title.replace('"', '""') if paper.title else ''
                authors_text = authors_text.replace('"', '""')
                
                published_date = paper.published_date.strftime('%Y-%m-%d') if paper.published_date else ''
                url = paper.url or ''
                
                papers_csv += f"{paper.id},\"{title}\",\"{authors_text}\",{published_date},{paper.source},\"{url}\"\n"
            
            hypotheses_csv = "id,hypothesis_text,confidence_score,created_at\n"
            for hypothesis in hypotheses:
                # Escape quotes in text fields
                hypothesis_text = hypothesis.hypothesis_text.replace('"', '""') if hypothesis.hypothesis_text else ''
                
                created_at = hypothesis.created_at.strftime('%Y-%m-%d') if hypothesis.created_at else ''
                
                hypotheses_csv += f"{hypothesis.id},\"{hypothesis_text}\",{hypothesis.confidence_score},{created_at}\n"
            
            # Create the export data
            export_data = {
                'project': {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description
                },
                'papers_csv': papers_csv,
                'hypotheses_csv': hypotheses_csv,
                'export_date': datetime.utcnow().isoformat(),
                'format': 'csv'
            }
            
            return export_data
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return {'error': f"Error exporting to CSV: {str(e)}"}
    
    def _export_bibtex(self, project, papers):
        """Export papers as BibTeX (in JSON format for API response)"""
        try:
            bibtex_content = ""
            
            for paper in papers:
                # Create BibTeX entry
                entry_type = "article"  # Default type
                
                # Create a citation key from first author's last name and year
                authors = paper.get_authors() if hasattr(paper, 'get_authors') else []
                citation_key = "paper"
                
                if authors:
                    if isinstance(authors[0], dict):
                        first_author = authors[0].get('name', '')
                    else:
                        first_author = authors[0]
                    
                    if first_author:
                        # Extract last name
                        last_name = first_author.split()[-1]
                        citation_key = last_name.lower()
                
                # Add year if available
                if paper.published_date:
                    year = paper.published_date.year
                    citation_key += str(year)
                else:
                    year = ""
                
                # Format authors for BibTeX
                bibtex_authors = ""
                if authors:
                    if isinstance(authors[0], dict):
                        author_names = [a.get('name', '') for a in authors]
                        bibtex_authors = " and ".join(author_names)
                    else:
                        bibtex_authors = " and ".join(authors)
                
                # Create the BibTeX entry
                bibtex_entry = f"@{entry_type}{{{citation_key},\n"
                bibtex_entry += f"  title = {{{paper.title}}},\n" if paper.title else ""
                bibtex_entry += f"  author = {{{bibtex_authors}}},\n" if bibtex_authors else ""
                bibtex_entry += f"  year = {{{year}}},\n" if year else ""
                bibtex_entry += f"  url = {{{paper.url}}},\n" if paper.url else ""
                bibtex_entry += f"  source = {{{paper.source}}}\n" if paper.source else ""
                bibtex_entry += "}\n\n"
                
                bibtex_content += bibtex_entry
            
            # Create the export data
            export_data = {
                'project': {
                    'id': project.id,
                    'title': project.title
                },
                'bibtex': bibtex_content,
                'paper_count': len(papers),
                'export_date': datetime.utcnow().isoformat(),
                'format': 'bibtex'
            }
            
            return export_data
        
        except Exception as e:
            logger.error(f"Error exporting to BibTeX: {e}")
            return {'error': f"Error exporting to BibTeX: {str(e)}"}