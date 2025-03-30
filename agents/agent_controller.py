import logging
import json
from agents.data_retrieval_agent import DataRetrievalAgent
from agents.summarization_agent import SummarizationAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.experiment_agent import ExperimentAgent
from agents.tensorflow_agent import TensorFlowAgent
from services.memory_service import MemoryService
from models import ResearchProject, ResearchQuery, Paper, PaperSummary, Hypothesis, ExperimentDesign, ChatMessage
from app import db

logger = logging.getLogger(__name__)

class AgentController:
    """
    Controller for coordinating multiple agents for research tasks
    """
    
    def __init__(self):
        self.data_agent = DataRetrievalAgent()
        self.summarization_agent = SummarizationAgent()
        self.hypothesis_agent = HypothesisAgent()
        self.experiment_agent = ExperimentAgent()
        self.tensorflow_agent = TensorFlowAgent()  # Main focus: TensorFlow agent
        self.memory_service = MemoryService()
    
    def process_research_question(self, project_id, query_text):
        """
        Process a research question through the agent workflow
        
        Args:
            project_id (int): ID of the research project
            query_text (str): The research question or query
        
        Returns:
            dict: Results of the research process
        """
        try:
            logger.info(f"Processing research question for project {project_id}: {query_text}")
            
            # Step 1: Analyze the research question
            question_analysis = self.hypothesis_agent.analyze_question(query_text)
            
            # Step 2: Store the query in the database
            query = ResearchQuery(
                query_text=query_text,
                project_id=project_id
            )
            db.session.add(query)
            db.session.commit()
            
            # Step 3: Extract search keywords from the analysis
            search_keywords = query_text
            if isinstance(question_analysis, dict) and 'keywords' in question_analysis:
                if isinstance(question_analysis['keywords'], list) and question_analysis['keywords']:
                    search_keywords = ' '.join(question_analysis['keywords'][:5])
            
            # Step 4: Retrieve papers
            papers = self.data_agent.search_papers(search_keywords)
            
            # Step 5: Store papers in database
            stored_papers = []
            for paper_data in papers:
                # Check if paper already exists
                existing_paper = Paper.query.filter_by(
                    external_id=paper_data['external_id'],
                    source=paper_data['source'],
                    project_id=project_id
                ).first()
                
                if existing_paper:
                    stored_papers.append(existing_paper)
                    continue
                
                # Create new paper
                paper = Paper(
                    title=paper_data['title'],
                    abstract=paper_data['abstract'],
                    url=paper_data['url'],
                    pdf_url=paper_data['pdf_url'],
                    external_id=paper_data['external_id'],
                    source=paper_data['source'],
                    project_id=project_id,
                    query_id=query.id
                )
                
                # Set authors
                paper.set_authors(paper_data['authors'])
                
                # Set published date if available
                if paper_data.get('published_date'):
                    paper.published_date = paper_data['published_date']
                
                # Set metadata if available
                if paper_data.get('metadata'):
                    paper.set_metadata(paper_data['metadata'])
                
                db.session.add(paper)
                db.session.commit()
                stored_papers.append(paper)
            
            # Step 6: Summarize papers
            for paper in stored_papers:
                # Skip if summary already exists
                if PaperSummary.query.filter_by(paper_id=paper.id).first():
                    continue
                    
                # Convert paper to dictionary format for the summarization agent
                paper_dict = {
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'external_id': paper.external_id,
                    'source': paper.source
                }
                
                # Generate summary
                summary_result = self.summarization_agent.summarize_paper(paper_dict)
                
                # Store summary in database
                if isinstance(summary_result, dict) and 'error' not in summary_result:
                    summary = PaperSummary(
                        summary_text=summary_result.get('summary', ''),
                        paper_id=paper.id
                    )
                    
                    # Store key findings if available
                    if 'key_findings' in summary_result:
                        summary.set_key_findings(summary_result['key_findings'])
                    
                    db.session.add(summary)
                    db.session.commit()
            
            # Step 7: Extract insights from papers
            paper_dicts = []
            for paper in stored_papers:
                paper_dict = {
                    'title': paper.title,
                    'source': paper.source,
                    'external_id': paper.external_id
                }
                
                # Add summary if available
                if paper.summary:
                    paper_dict['summary'] = paper.summary.summary_text
                
                paper_dicts.append(paper_dict)
            
            insights = self.summarization_agent.analyze_papers(paper_dicts)
            
            # Step 8: Generate hypotheses
            hypotheses_result = self.hypothesis_agent.generate_hypotheses(paper_dicts, query_text)
            
            # Store hypotheses in database
            stored_hypotheses = []
            if isinstance(hypotheses_result, dict) and 'hypotheses' in hypotheses_result:
                for hyp_data in hypotheses_result['hypotheses']:
                    hypothesis = Hypothesis(
                        hypothesis_text=hyp_data.get('hypothesis', ''),
                        reasoning=hyp_data.get('reasoning', ''),
                        confidence_score=hyp_data.get('confidence', 0.5),
                        project_id=project_id
                    )
                    
                    # Store supporting evidence if available
                    if 'supporting_evidence' in hyp_data:
                        hypothesis.set_supporting_evidence(hyp_data['supporting_evidence'])
                    
                    db.session.add(hypothesis)
                    db.session.commit()
                    stored_hypotheses.append(hypothesis)
            
            # Step 9: Design an experiment for the first hypothesis if available
            experiment_result = None
            if stored_hypotheses:
                experiment_result = self.experiment_agent.design_experiment(
                    stored_hypotheses[0].hypothesis_text,
                    paper_dicts
                )
                
                # Store experiment in database
                if isinstance(experiment_result, dict) and 'error' not in experiment_result:
                    experiment = ExperimentDesign(
                        title=experiment_result.get('title', 'Experiment Design'),
                        methodology=experiment_result.get('methodology', ''),
                        controls=experiment_result.get('controls', ''),
                        expected_outcomes=experiment_result.get('expected_outcomes', ''),
                        limitations=experiment_result.get('limitations', ''),
                        hypothesis_id=stored_hypotheses[0].id
                    )
                    
                    # Store variables if available
                    if 'variables' in experiment_result:
                        experiment.set_variables(experiment_result['variables'])
                    
                    db.session.add(experiment)
                    db.session.commit()
            
            # Step 10: Add chat message summarizing the research process
            chat_message = ChatMessage(
                role='system',
                content=f"Completed research process for query: '{query_text}'. Found {len(stored_papers)} papers, generated {len(stored_hypotheses)} hypotheses, and designed an experiment.",
                agent_type='controller',
                project_id=project_id
            )
            db.session.add(chat_message)
            db.session.commit()
            
            # Step 11: Return results
            return {
                'query': {
                    'id': query.id,
                    'text': query.query_text
                },
                'question_analysis': question_analysis,
                'papers': [{
                    'id': p.id,
                    'title': p.title,
                    'authors': p.get_authors(),
                    'abstract': p.abstract,
                    'url': p.url
                } for p in stored_papers],
                'insights': insights,
                'hypotheses': [{
                    'id': h.id,
                    'text': h.hypothesis_text,
                    'confidence': h.confidence_score
                } for h in stored_hypotheses],
                'experiment': experiment_result
            }
            
        except Exception as e:
            logger.error(f"Error in research process: {str(e)}")
            
            # Add error message to chat
            try:
                chat_message = ChatMessage(
                    role='system',
                    content=f"Error processing research query: {str(e)}",
                    agent_type='controller',
                    project_id=project_id
                )
                db.session.add(chat_message)
                db.session.commit()
            except:
                pass
                
            return {"error": str(e)}
    
    def handle_chat_query(self, project_id, query_text):
        """
        Handle a chat query by routing to the appropriate agent
        
        Args:
            project_id (int): ID of the research project
            query_text (str): The user's chat query
        
        Returns:
            dict: Response from the agent
        """
        try:
            logger.info(f"Handling chat query for project {project_id}: {query_text}")
            
            # Store user message
            user_message = ChatMessage(
                role='user',
                content=query_text,
                project_id=project_id
            )
            db.session.add(user_message)
            db.session.commit()
            
            # Determine query type and route to appropriate agent
            query_type, agent_type = self._classify_query(query_text)
            
            response = None
            
            if query_type == 'paper_search':
                # Route to data retrieval agent
                papers = self.data_agent.search_papers(query_text)
                response = {
                    'message': f"Found {len(papers)} papers related to your query.",
                    'papers': papers
                }
                agent_type = 'retrieval'
                
            elif query_type == 'paper_summary':
                # Extract paper ID from query if possible
                import re
                paper_match = re.search(r'paper[:\s]+(\d+)', query_text, re.IGNORECASE)
                
                if paper_match:
                    paper_id = int(paper_match.group(1))
                    paper = Paper.query.filter_by(id=paper_id, project_id=project_id).first()
                    
                    if paper:
                        # Convert to dictionary format
                        paper_dict = {
                            'title': paper.title,
                            'abstract': paper.abstract,
                            'external_id': paper.external_id,
                            'source': paper.source
                        }
                        
                        # Generate or retrieve summary
                        if paper.summary:
                            summary_text = paper.summary.summary_text
                            key_findings = paper.summary.get_key_findings()
                            response = {
                                'message': f"Summary of '{paper.title}':",
                                'summary': summary_text,
                                'key_findings': key_findings
                            }
                        else:
                            summary_result = self.summarization_agent.summarize_paper(paper_dict)
                            
                            if isinstance(summary_result, dict) and 'error' not in summary_result:
                                # Store summary
                                summary = PaperSummary(
                                    summary_text=summary_result.get('summary', ''),
                                    paper_id=paper.id
                                )
                                
                                if 'key_findings' in summary_result:
                                    summary.set_key_findings(summary_result['key_findings'])
                                
                                db.session.add(summary)
                                db.session.commit()
                                
                                response = {
                                    'message': f"Summary of '{paper.title}':",
                                    'summary': summary_result.get('summary', ''),
                                    'key_findings': summary_result.get('key_findings', [])
                                }
                            else:
                                response = {
                                    'message': f"Could not generate summary for '{paper.title}'."
                                }
                    else:
                        response = {
                            'message': f"Could not find paper with ID {paper_id} in this project."
                        }
                else:
                    # Try to find papers by title match
                    papers = Paper.query.filter(
                        Paper.project_id == project_id,
                        Paper.title.ilike(f"%{query_text}%")
                    ).limit(5).all()
                    
                    if papers:
                        response = {
                            'message': "Found these papers matching your query. Please specify which one you'd like summarized:",
                            'papers': [{
                                'id': p.id,
                                'title': p.title
                            } for p in papers]
                        }
                    else:
                        response = {
                            'message': "Could not find a specific paper to summarize. Please specify a paper ID or title."
                        }
                
                agent_type = 'summarization'
                
            elif query_type == 'generate_hypothesis':
                # Get all papers for the project
                papers = Paper.query.filter_by(project_id=project_id).all()
                
                if papers:
                    paper_dicts = []
                    for paper in papers:
                        paper_dict = {
                            'title': paper.title,
                            'abstract': paper.abstract,
                            'source': paper.source,
                            'external_id': paper.external_id
                        }
                        
                        # Add summary if available
                        if paper.summary:
                            paper_dict['summary'] = paper.summary.summary_text
                        
                        paper_dicts.append(paper_dict)
                    
                    # Generate hypotheses
                    hypotheses_result = self.hypothesis_agent.generate_hypotheses(paper_dicts, query_text)
                    
                    if isinstance(hypotheses_result, dict) and 'hypotheses' in hypotheses_result:
                        # Store hypotheses
                        for hyp_data in hypotheses_result['hypotheses']:
                            hypothesis = Hypothesis(
                                hypothesis_text=hyp_data.get('hypothesis', ''),
                                reasoning=hyp_data.get('reasoning', ''),
                                confidence_score=hyp_data.get('confidence', 0.5),
                                project_id=project_id
                            )
                            
                            if 'supporting_evidence' in hyp_data:
                                hypothesis.set_supporting_evidence(hyp_data['supporting_evidence'])
                            
                            db.session.add(hypothesis)
                        
                        db.session.commit()
                        
                        response = {
                            'message': "Generated the following hypotheses based on the literature:",
                            'hypotheses': hypotheses_result['hypotheses'],
                            'gaps': hypotheses_result.get('gaps_identified', []),
                            'directions': hypotheses_result.get('suggested_research_directions', [])
                        }
                    else:
                        response = {
                            'message': "Could not generate hypotheses. Please try again with a more specific research question."
                        }
                else:
                    response = {
                        'message': "No papers found in this project. Please search for papers first."
                    }
                
                agent_type = 'hypothesis'
                
            elif query_type == 'design_experiment':
                # Extract hypothesis ID from query if possible
                import re
                hypothesis_match = re.search(r'hypothesis[:\s]+(\d+)', query_text, re.IGNORECASE)
                
                if hypothesis_match:
                    hypothesis_id = int(hypothesis_match.group(1))
                    hypothesis = Hypothesis.query.filter_by(id=hypothesis_id, project_id=project_id).first()
                    
                    if hypothesis:
                        # Get papers for reference
                        papers = Paper.query.filter_by(project_id=project_id).all()
                        paper_dicts = []
                        
                        for paper in papers:
                            paper_dict = {
                                'title': paper.title,
                                'abstract': paper.abstract
                            }
                            
                            # Add summary if available
                            if paper.summary:
                                paper_dict['summary'] = paper.summary.summary_text
                            
                            paper_dicts.append(paper_dict)
                        
                        # Design experiment
                        experiment_result = self.experiment_agent.design_experiment(hypothesis.hypothesis_text, paper_dicts)
                        
                        if isinstance(experiment_result, dict) and 'error' not in experiment_result:
                            # Store experiment
                            experiment = ExperimentDesign(
                                title=experiment_result.get('title', 'Experiment Design'),
                                methodology=experiment_result.get('methodology', ''),
                                controls=experiment_result.get('controls', ''),
                                expected_outcomes=experiment_result.get('expected_outcomes', ''),
                                limitations=experiment_result.get('limitations', ''),
                                hypothesis_id=hypothesis.id
                            )
                            
                            if 'variables' in experiment_result:
                                experiment.set_variables(experiment_result['variables'])
                            
                            db.session.add(experiment)
                            db.session.commit()
                            
                            response = {
                                'message': f"Designed an experiment for hypothesis: '{hypothesis.hypothesis_text}'",
                                'experiment': experiment_result
                            }
                        else:
                            response = {
                                'message': f"Could not design experiment for hypothesis: '{hypothesis.hypothesis_text}'."
                            }
                    else:
                        response = {
                            'message': f"Could not find hypothesis with ID {hypothesis_id} in this project."
                        }
                else:
                    # Get recent hypotheses
                    hypotheses = Hypothesis.query.filter_by(project_id=project_id).order_by(Hypothesis.id.desc()).limit(5).all()
                    
                    if hypotheses:
                        response = {
                            'message': "Please specify which hypothesis you'd like to design an experiment for:",
                            'hypotheses': [{
                                'id': h.id,
                                'text': h.hypothesis_text
                            } for h in hypotheses]
                        }
                    else:
                        response = {
                            'message': "No hypotheses found in this project. Please generate hypotheses first."
                        }
                
                agent_type = 'experiment'
            
            # TensorFlow Analysis (main focus)
            elif query_type in ['tensorflow_analysis', 'research_gaps', 'impact_prediction', 'paper_classification', 'research_impact']:
                # Get papers for analysis
                papers = Paper.query.filter_by(project_id=project_id).all()
                
                if not papers:
                    response = {
                        'message': "No papers found for analysis. Please search for papers first."
                    }
                    agent_type = 'tensorflow'
                    
                else:
                    # Convert papers to dictionary format
                    paper_dicts = []
                    for paper in papers:
                        paper_dict = {
                            'id': paper.id,
                            'title': paper.title,
                            'abstract': paper.abstract,
                            'authors': paper.get_authors(),
                            'source': paper.source,
                            'external_id': paper.external_id
                        }
                        
                        # Add metadata if available
                        if paper.get_metadata():
                            paper_dict['metadata'] = paper.get_metadata()
                        
                        # Add published date if available
                        if paper.published_date:
                            paper_dict['published_date'] = paper.published_date
                        
                        # Add summary if available
                        if paper.summary:
                            paper_dict['summary'] = paper.summary.summary_text
                            paper_dict['key_findings'] = paper.summary.get_key_findings()
                        
                        paper_dicts.append(paper_dict)
                    
                    # Process by specific query type
                    if query_type == 'tensorflow_analysis':
                        # Extract analysis type from the query
                        analysis_type = "all"
                        if "embedding" in query_text.lower():
                            analysis_type = "embeddings"
                        elif "trend" in query_text.lower():
                            analysis_type = "trends"
                        elif "impact" in query_text.lower() or "citation" in query_text.lower():
                            analysis_type = "impact"
                        elif "similar" in query_text.lower():
                            analysis_type = "similarities"
                        
                        # Perform analysis
                        tf_results = self.tensorflow_agent.analyze_papers_with_tf(paper_dicts, analysis_type)
                        
                        if isinstance(tf_results, dict) and 'error' not in tf_results:
                            response = {
                                'message': f"Completed TensorFlow analysis on {len(paper_dicts)} papers.",
                                'analysis_results': tf_results
                            }
                        else:
                            response = {
                                'message': f"Error in TensorFlow analysis: {tf_results.get('error', 'Unknown error')}"
                            }
                    
                    elif query_type == 'research_gaps':
                        # Identify research gaps
                        gaps_results = self.tensorflow_agent.identify_research_gaps(paper_dicts)
                        
                        if isinstance(gaps_results, dict) and 'error' not in gaps_results:
                            response = {
                                'message': "Identified potential research gaps and opportunities.",
                                'gaps_analysis': gaps_results
                            }
                        else:
                            response = {
                                'message': f"Error in research gap analysis: {gaps_results.get('error', 'Unknown error')}"
                            }
                    
                    elif query_type == 'impact_prediction':
                        # Predict paper impacts
                        impact_results = self.tensorflow_agent.train_citation_prediction_model(paper_dicts)
                        
                        if isinstance(impact_results, dict) and 'error' not in impact_results:
                            response = {
                                'message': "Completed citation impact prediction analysis.",
                                'impact_analysis': impact_results
                            }
                        else:
                            response = {
                                'message': f"Error in impact prediction: {impact_results.get('error', 'Unknown error')}"
                            }
                    
                    elif query_type == 'paper_classification':
                        # Extract categories from query if available
                        categories = None
                        category_match = re.search(r'categories:?\s*\[(.*?)\]', query_text, re.IGNORECASE)
                        if category_match:
                            categories_str = category_match.group(1)
                            categories = [cat.strip() for cat in categories_str.split(',')]
                        
                        # Classify papers
                        classification_results = self.tensorflow_agent.classify_research_papers(paper_dicts, categories)
                        
                        if isinstance(classification_results, dict) and 'error' not in classification_results:
                            response = {
                                'message': f"Classified {len(paper_dicts)} papers into research categories.",
                                'classification_results': classification_results
                            }
                        else:
                            response = {
                                'message': f"Error in paper classification: {classification_results.get('error', 'Unknown error')}"
                            }
                    
                    elif query_type == 'research_impact':
                        # Extract research field from query
                        research_field = query_text
                        field_match = re.search(r'field[:\s]+(.*?)(?:\.|$)', query_text, re.IGNORECASE)
                        if field_match:
                            research_field = field_match.group(1).strip()
                        
                        # Evaluate research impact
                        impact_results = self.tensorflow_agent.evaluate_research_impact(research_field, paper_dicts)
                        
                        if isinstance(impact_results, dict) and 'error' not in impact_results:
                            response = {
                                'message': f"Evaluated research impact for '{research_field}'.",
                                'impact_evaluation': impact_results
                            }
                        else:
                            response = {
                                'message': f"Error in research impact evaluation: {impact_results.get('error', 'Unknown error')}"
                            }
                    
                    agent_type = 'tensorflow'
                        
                        if isinstance(experiment_result, dict) and 'error' not in experiment_result:
                            # Store experiment
                            experiment = ExperimentDesign(
                                title=experiment_result.get('title', 'Experiment Design'),
                                methodology=experiment_result.get('methodology', ''),
                                controls=experiment_result.get('controls', ''),
                                expected_outcomes=experiment_result.get('expected_outcomes', ''),
                                limitations=experiment_result.get('limitations', ''),
                                hypothesis_id=hypothesis.id
                            )
                            
                            if 'variables' in experiment_result:
                                experiment.set_variables(experiment_result['variables'])
                            
                            db.session.add(experiment)
                            db.session.commit()
                            
                            response = {
                                'message': f"Designed an experiment for hypothesis: '{hypothesis.hypothesis_text}'",
                                'experiment': experiment_result
                            }
                        else:
                            response = {
                                'message': f"Could not design experiment for hypothesis: '{hypothesis.hypothesis_text}'."
                            }
                    else:
                        response = {
                            'message': f"Could not find hypothesis with ID {hypothesis_id} in this project."
                        }
                else:
                    # Get recent hypotheses
                    hypotheses = Hypothesis.query.filter_by(project_id=project_id).order_by(Hypothesis.id.desc()).limit(5).all()
                    
                    if hypotheses:
                        response = {
                            'message': "Please specify which hypothesis you'd like to design an experiment for:",
                            'hypotheses': [{
                                'id': h.id,
                                'text': h.hypothesis_text
                            } for h in hypotheses]
                        }
                    else:
                        response = {
                            'message': "No hypotheses found in this project. Please generate hypotheses first."
                        }
                
                agent_type = 'experiment'
                
            else:
                # General query - use OpenAI to generate a response based on project context
                from services.openai_service import generate_completion
                
                # Get project data for context
                project = ResearchProject.query.get(project_id)
                papers = Paper.query.filter_by(project_id=project_id).limit(10).all()
                hypotheses = Hypothesis.query.filter_by(project_id=project_id).limit(5).all()
                
                # Create context
                context = f"Project: {project.title}\nDescription: {project.description}\n\n"
                
                if papers:
                    context += "Recent papers:\n"
                    for i, paper in enumerate(papers):
                        context += f"{i+1}. {paper.title}\n"
                
                if hypotheses:
                    context += "\nHypotheses:\n"
                    for i, hypothesis in enumerate(hypotheses):
                        context += f"{i+1}. {hypothesis.hypothesis_text}\n"
                
                # Get recent chat messages for context
                recent_messages = ChatMessage.query.filter_by(
                    project_id=project_id
                ).order_by(ChatMessage.id.desc()).limit(5).all()
                
                if recent_messages:
                    context += "\nRecent conversation:\n"
                    for msg in reversed(recent_messages):
                        context += f"{msg.role}: {msg.content}\n"
                
                # Create system prompt
                system_prompt = """
                You are AURA, an AI-powered autonomous research assistant. You help researchers with
                literature reviews, summarizing findings, generating hypotheses, and designing experiments.
                You should respond based on the project context provided, and be helpful, clear, and concise.
                
                You can suggest specific actions the user might want to take, such as:
                1. Searching for specific papers
                2. Summarizing papers
                3. Generating hypotheses
                4. Designing experiments
                
                Always maintain a professional, academic tone.
                """
                
                # Generate response
                prompt = f"Context:\n{context}\n\nUser query: {query_text}\n\nPlease provide a helpful response."
                response_text = generate_completion(prompt, system_prompt)
                
                response = {
                    'message': response_text
                }
                agent_type = 'assistant'
            
            # Store agent response
            agent_message = ChatMessage(
                role='agent',
                content=json.dumps(response),
                agent_type=agent_type,
                project_id=project_id
            )
            db.session.add(agent_message)
            db.session.commit()
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling chat query: {str(e)}")
            
            # Add error message to chat
            try:
                error_message = ChatMessage(
                    role='system',
                    content=f"Error processing your query: {str(e)}",
                    agent_type='controller',
                    project_id=project_id
                )
                db.session.add(error_message)
                db.session.commit()
            except:
                pass
                
            return {
                'message': f"I encountered an error while processing your query: {str(e)}. Please try again or rephrase your question."
            }
    
    def _classify_query(self, query_text):
        """
        Classify the type of query to route to the appropriate agent
        
        Args:
            query_text (str): The user's query text
        
        Returns:
            tuple: Query type and agent type
        """
        query_text_lower = query_text.lower()
        
        # Check for paper search
        if any(keyword in query_text_lower for keyword in ['find papers', 'search for', 'find research', 'papers about', 'articles on']):
            return 'paper_search', 'retrieval'
        
        # Check for paper summary
        if any(keyword in query_text_lower for keyword in ['summarize', 'summary of', 'tldr', 'explain paper']):
            return 'paper_summary', 'summarization'
        
        # Check for hypothesis generation
        if any(keyword in query_text_lower for keyword in ['generate hypothesis', 'hypotheses', 'what if', 'suggest hypothesis']):
            return 'generate_hypothesis', 'hypothesis'
        
        # Check for experiment design
        if any(keyword in query_text_lower for keyword in ['design experiment', 'experimental design', 'methodology', 'how to test']):
            return 'design_experiment', 'experiment'
        
        # Check for TensorFlow analysis (main focus)
        if any(keyword in query_text_lower for keyword in ['tensorflow', 'ml', 'machine learning', 'analyze with tf', 'neural network', 
                                                          'deep learning', 'predict', 'classify', 'embedding', 'trends', 'tensorflow analysis']):
            return 'tensorflow_analysis', 'tensorflow'
        
        # Check for research gap identification using TensorFlow
        if any(keyword in query_text_lower for keyword in ['research gaps', 'identify gaps', 'what\'s missing', 'research opportunities',
                                                         'potential research', 'unexplored areas']):
            return 'research_gaps', 'tensorflow'
        
        # Check for citation or impact prediction
        if any(keyword in query_text_lower for keyword in ['predict citations', 'paper impact', 'citation prediction', 'impact score', 
                                                         'influential papers', 'paper ranking']):
            return 'impact_prediction', 'tensorflow'
        
        # Check for paper classification
        if any(keyword in query_text_lower for keyword in ['classify papers', 'categorize', 'classify research', 'paper categories', 
                                                         'research topics', 'topic modeling']):
            return 'paper_classification', 'tensorflow'
        
        # Check for research impact assessment
        if any(keyword in query_text_lower for keyword in ['research impact', 'field impact', 'research importance', 'significance of research', 
                                                         'evaluate research', 'field assessment']):
            return 'research_impact', 'tensorflow'
        
        # Default to general query
        return 'general', 'assistant'
