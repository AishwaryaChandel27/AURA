import logging
import json
from services.openai_service import generate_hypothesis, analyze_research_question
from services.memory_service import MemoryService

logger = logging.getLogger(__name__)

class HypothesisAgent:
    """
    Agent responsible for generating research hypotheses based on paper summaries
    """
    
    def __init__(self):
        self.memory_service = MemoryService()
    
    def generate_hypotheses(self, papers, research_question):
        """
        Generate hypotheses based on paper summaries and a research question
        
        Args:
            papers (list): List of papers with summaries
            research_question (str): The research question to guide hypothesis generation
        
        Returns:
            dict: Generated hypotheses and supporting evidence
        """
        try:
            logger.info(f"Generating hypotheses for question: {research_question}")
            
            # Get paper summaries
            paper_summaries = []
            for paper in papers:
                # Try to get summary from the paper dictionary
                if paper.get('summary'):
                    summary = paper['summary']
                else:
                    # Try to get summary from memory
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
                        # Use abstract if no summary is available
                        summary = f"Title: {paper['title']}\nAbstract: {paper['abstract']}"
                
                # Format paper with title and ID
                formatted_summary = f"Title: {paper['title']}\nID: {paper['source']}_{paper['external_id']}\n\n{summary}"
                paper_summaries.append(formatted_summary)
            
            # Generate hypotheses using OpenAI
            hypotheses_result = generate_hypothesis(paper_summaries, research_question)
            
            # Store hypotheses in memory
            if hypotheses_result and 'error' not in hypotheses_result:
                # Create a unique ID for these hypotheses
                import hashlib
                hypotheses_hash = hashlib.md5(f"{research_question}_{len(papers)}".encode()).hexdigest()
                doc_id = f"hypotheses_{hypotheses_hash}"
                
                # Create hypotheses text
                hypotheses_text = json.dumps(hypotheses_result)
                
                # Store in memory
                self.memory_service.add_document(
                    doc_id=doc_id,
                    text=hypotheses_text,
                    metadata={
                        'type': 'hypotheses',
                        'research_question': research_question,
                        'paper_count': len(papers),
                        'paper_ids': [f"{p['source']}_{p['external_id']}" for p in papers],
                    }
                )
            
            return hypotheses_result
            
        except Exception as e:
            logger.error(f"Error in hypothesis generation: {str(e)}")
            return {"error": str(e)}
    
    def analyze_question(self, research_question):
        """
        Analyze a research question to break it down into components
        
        Args:
            research_question (str): The research question to analyze
        
        Returns:
            dict: Analysis of the research question
        """
        try:
            logger.info(f"Analyzing research question: {research_question}")
            
            # Analyze the question using OpenAI
            analysis_result = analyze_research_question(research_question)
            
            # Store analysis in memory
            if analysis_result and 'error' not in analysis_result:
                # Create a unique ID for this analysis
                import hashlib
                question_hash = hashlib.md5(research_question.encode()).hexdigest()
                doc_id = f"question_analysis_{question_hash}"
                
                # Create analysis text
                analysis_text = json.dumps(analysis_result)
                
                # Store in memory
                self.memory_service.add_document(
                    doc_id=doc_id,
                    text=analysis_text,
                    metadata={
                        'type': 'question_analysis',
                        'research_question': research_question
                    }
                )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in research question analysis: {str(e)}")
            return {"error": str(e)}
    
    def refine_hypothesis(self, hypothesis, feedback):
        """
        Refine a hypothesis based on user feedback
        
        Args:
            hypothesis (str): The original hypothesis
            feedback (str): User feedback for refinement
        
        Returns:
            dict: Refined hypothesis
        """
        try:
            logger.info(f"Refining hypothesis based on feedback")
            
            # Create system prompt for refinement
            system_prompt = """
            You are an expert research scientist. Refine the provided hypothesis based on the given feedback.
            Your response should be in JSON format with the following structure:
            {
                "refined_hypothesis": "The refined hypothesis statement",
                "explanation": "Explanation of how the hypothesis was refined based on feedback",
                "improvements": ["List of specific improvements made"]
            }
            """
            
            # Create user prompt
            prompt = f"Original Hypothesis: {hypothesis}\n\nFeedback: {feedback}\n\nPlease refine this hypothesis based on the feedback."
            
            # Use OpenAI service to refine
            from services.openai_service import generate_completion
            refined_result = generate_completion(prompt, system_prompt, json_response=True)
            
            return refined_result
            
        except Exception as e:
            logger.error(f"Error in hypothesis refinement: {str(e)}")
            return {"error": str(e)}
    
    def suggest_relevant_fields(self, research_question):
        """
        Suggest relevant fields and experts for a research question
        
        Args:
            research_question (str): The research question
        
        Returns:
            dict: Suggested fields and experts
        """
        try:
            logger.info(f"Suggesting relevant fields for question: {research_question}")
            
            # Create system prompt for field suggestions
            system_prompt = """
            You are an expert academic advisor familiar with various research fields and notable researchers.
            Based on the provided research question, suggest relevant academic fields, subfields, and notable 
            researchers or experts in this area. Also suggest relevant journals and conferences.
            
            Your response should be in JSON format with the following structure:
            {
                "primary_fields": ["List of primary academic fields"],
                "secondary_fields": ["List of related or secondary fields"],
                "notable_researchers": ["List of notable researchers in this area"],
                "relevant_journals": ["List of relevant academic journals"],
                "relevant_conferences": ["List of relevant conferences"]
            }
            """
            
            # Create user prompt
            prompt = f"Research Question: {research_question}\n\nPlease suggest relevant fields, researchers, journals, and conferences for this research question."
            
            # Use OpenAI service to get suggestions
            from services.openai_service import generate_completion
            suggestions = generate_completion(prompt, system_prompt, json_response=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error in field suggestion: {str(e)}")
            return {"error": str(e)}
