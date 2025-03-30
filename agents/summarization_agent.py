import logging
import json
from services.openai_service import summarize_paper, extract_paper_insights
from services.memory_service import MemoryService
from config import SUMMARY_MAX_TOKENS

logger = logging.getLogger(__name__)

class SummarizationAgent:
    """
    Agent responsible for summarizing and analyzing research papers
    """
    
    def __init__(self):
        self.memory_service = MemoryService()
        self.max_tokens = SUMMARY_MAX_TOKENS
    
    def summarize_paper(self, paper):
        """
        Generate a summary for a research paper
        
        Args:
            paper (dict): Paper dictionary with title, abstract, and possibly full text
        
        Returns:
            dict: Summary with key findings
        """
        try:
            logger.info(f"Summarizing paper: {paper.get('title', '(Untitled)')}")
            
            # Get paper details
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            full_text = paper.get('full_text', None)  # This might be None for most papers
            
            # Generate summary using OpenAI
            summary_result = summarize_paper(title, abstract, full_text)
            
            # Store summary in memory
            if summary_result and not isinstance(summary_result, dict) or 'error' not in summary_result:
                paper_id = f"{paper['source']}_{paper['external_id']}"
                doc_id = f"summary_{paper_id}"
                
                # Create summary text
                summary_text = json.dumps(summary_result) if isinstance(summary_result, dict) else summary_result
                
                # Store in memory
                self.memory_service.add_document(
                    doc_id=doc_id,
                    text=summary_text,
                    metadata={
                        'type': 'summary',
                        'paper_id': paper_id,
                        'title': title,
                        'summary': summary_result.get('summary') if isinstance(summary_result, dict) else summary_text[:200]
                    }
                )
            
            return summary_result
            
        except Exception as e:
            logger.error(f"Error in summarization agent: {str(e)}")
            return {"error": str(e)}
    
    def analyze_papers(self, papers):
        """
        Analyze a collection of papers to extract insights, contradictions, and trends
        
        Args:
            papers (list): List of papers with summaries
        
        Returns:
            dict: Analysis results
        """
        try:
            logger.info(f"Analyzing {len(papers)} papers")
            
            # Extract summaries from papers
            summaries = []
            for paper in papers:
                if paper.get('summary'):
                    summary = paper['summary']
                else:
                    # Get summary from memory if available
                    paper_id = f"{paper['source']}_{paper['external_id']}"
                    doc_id = f"summary_{paper_id}"
                    summary_doc = self.memory_service.get_document(doc_id)
                    
                    if summary_doc:
                        try:
                            summary_data = json.loads(summary_doc['document'])
                            summary = summary_data.get('summary', summary_doc['document'])
                        except json.JSONDecodeError:
                            summary = summary_doc['document']
                    else:
                        # Generate summary if not in memory
                        summary_result = self.summarize_paper(paper)
                        if isinstance(summary_result, dict):
                            summary = summary_result.get('summary', '')
                        else:
                            summary = summary_result
                
                paper_summary = f"Paper: {paper['title']}\n{summary}"
                summaries.append(paper_summary)
            
            # Perform analysis using OpenAI
            analysis_result = extract_paper_insights(summaries)
            
            # Store analysis in memory
            if analysis_result and 'error' not in analysis_result:
                # Create a unique ID for this analysis
                import hashlib
                papers_hash = hashlib.md5(str([p['title'] for p in papers]).encode()).hexdigest()
                doc_id = f"analysis_{papers_hash}"
                
                # Create analysis text
                analysis_text = json.dumps(analysis_result)
                
                # Store in memory
                self.memory_service.add_document(
                    doc_id=doc_id,
                    text=analysis_text,
                    metadata={
                        'type': 'analysis',
                        'paper_count': len(papers),
                        'paper_ids': [f"{p['source']}_{p['external_id']}" for p in papers],
                        'analysis_type': 'insights_and_contradictions'
                    }
                )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in paper analysis: {str(e)}")
            return {"error": str(e)}
    
    def get_key_findings(self, paper_id):
        """
        Get key findings for a specific paper
        
        Args:
            paper_id (str): Paper ID
        
        Returns:
            list: Key findings
        """
        try:
            # Try to get summary from memory
            doc_id = f"summary_{paper_id}"
            summary_doc = self.memory_service.get_document(doc_id)
            
            if summary_doc:
                try:
                    summary_data = json.loads(summary_doc['document'])
                    key_findings = summary_data.get('key_findings', [])
                    if isinstance(key_findings, list):
                        return key_findings
                    else:
                        return [key_findings]
                except (json.JSONDecodeError, TypeError):
                    return [summary_doc['document']]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting key findings: {str(e)}")
            return []
    
    def compare_papers(self, paper_ids):
        """
        Compare multiple papers to highlight similarities and differences
        
        Args:
            paper_ids (list): List of paper IDs to compare
        
        Returns:
            dict: Comparison results
        """
        try:
            papers = []
            
            # Retrieve papers and their summaries
            for paper_id in paper_ids:
                # Get paper from memory
                paper_doc = self.memory_service.get_document(paper_id)
                
                if not paper_doc:
                    continue
                
                # Get summary from memory
                summary_doc = self.memory_service.get_document(f"summary_{paper_id}")
                
                paper = {
                    'id': paper_id,
                    'title': paper_doc['metadata'].get('title', ''),
                    'abstract': paper_doc['metadata'].get('abstract', '')
                }
                
                if summary_doc:
                    try:
                        summary_data = json.loads(summary_doc['document'])
                        paper['summary'] = summary_data.get('summary', '')
                        paper['key_findings'] = summary_data.get('key_findings', [])
                    except json.JSONDecodeError:
                        paper['summary'] = summary_doc['document']
                
                papers.append(paper)
            
            # If we have at least two papers, perform a comparison analysis
            if len(papers) >= 2:
                return self.analyze_papers(papers)
            else:
                return {"error": "Need at least two valid papers for comparison"}
            
        except Exception as e:
            logger.error(f"Error comparing papers: {str(e)}")
            return {"error": str(e)}
