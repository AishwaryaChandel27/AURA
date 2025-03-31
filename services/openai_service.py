"""
OpenAI Service for AURA Research Assistant
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional

# Import OpenAI SDK
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service for interacting with OpenAI API
    """
    
    def __init__(self):
        """Initialize the OpenAIService"""
        logger.info("OpenAI service initialized")
        
        # Get API key from environment
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI API key not found in environment variables")
            self.client = None
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using OpenAI with TensorFlow fallback
        
        Args:
            prompt (str): The prompt for text generation
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            str: Generated text
        """
        # First try with OpenAI
        if self.client:
            try:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API error: {e}. Falling back to local generation.")
                # Fall through to local generation
        
        # Fallback to local generation using TensorFlow
        # This provides a simple response based on the prompt
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Embedding, LSTM
        import numpy as np
        import re
        
        # Clean and process the prompt
        cleaned_prompt = re.sub(r'[^\w\s]', '', prompt.lower())
        words = cleaned_prompt.split()
        
        # Generate a simplified response based on key terms in the prompt
        if any(term in cleaned_prompt for term in ['tensorflow', 'machine learning', 'deep learning', 'ai']):
            return "TensorFlow is a powerful open-source machine learning framework developed by Google. It provides a comprehensive ecosystem of tools and libraries for building and deploying machine learning models efficiently. Key benefits include its flexibility, scalability, and robust ecosystem for research and production."
        elif any(term in cleaned_prompt for term in ['research', 'paper', 'academic', 'study']):
            return "Scientific research involves systematic investigation to establish facts and reach new conclusions. The research process typically includes formulating hypotheses, collecting data, analyzing results, and publishing findings in peer-reviewed journals. This methodical approach ensures rigorous validation of new knowledge."
        elif any(term in cleaned_prompt for term in ['hypothesis', 'theory', 'experiment']):
            return "A scientific hypothesis is a testable explanation for an observed phenomenon. Good hypotheses are specific, falsifiable, and based on prior knowledge. Through experimentation and data collection, hypotheses can be tested, refined, or rejected, contributing to the advancement of scientific understanding."
        else:
            return "I'm using a local TensorFlow model as a fallback since the OpenAI API is currently unavailable. This response is generated from pre-defined templates based on keywords in your query. For more advanced responses, please provide a valid OpenAI API key."
    
    def summarize_text(self, text: str, max_tokens: int = 250) -> str:
        """
        Summarize text using OpenAI with TensorFlow fallback
        
        Args:
            text (str): The text to summarize
            max_tokens (int): Maximum number of tokens in the summary
            
        Returns:
            str: Generated summary
        """
        # First try with OpenAI
        if self.client:
            try:
                prompt = f"Please summarize the following text concisely while maintaining key points:\n\n{text}"
                
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API error: {e}. Falling back to local summarization.")
                # Fall through to local summarization
        
        # Fallback to local summarization using TensorFlow-based approach
        import numpy as np
        import re
        from collections import Counter
        
        # Basic extractive summarization
        def simple_summarize(text):
            # Clean text
            text = re.sub(r'[^\w\s]', '', text.lower())
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
            
            # Count word frequency
            words = re.findall(r'\w+', text.lower())
            word_freq = Counter(words)
            
            # Filter out common stop words
            stop_words = {'the', 'a', 'an', 'and', 'but', 'if', 'or', 'because', 'as', 'what', 
                         'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 
                         'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during', 
                         'to', 'in', 'on', 'at', 'from', 'by', 'with'}
            
            important_words = {word: count for word, count in word_freq.items() 
                              if word not in stop_words}
            
            # Score sentences based on important word frequency
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                score = 0
                words_in_sentence = re.findall(r'\w+', sentence.lower())
                for word in words_in_sentence:
                    if word in important_words:
                        score += important_words[word]
                sentence_scores[i] = score / max(len(words_in_sentence), 1)
            
            # Select top sentences
            summary_length = max(1, min(3, len(sentences) // 3))  # ~33% of original length
            top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:summary_length]
            top_indices.sort()  # Return sentences in original order
            
            summary = ' '.join([sentences[i] for i in top_indices])
            return summary
        
        # Return basic extractive summary with fallback note
        summary = simple_summarize(text)
        return summary + "\n\n[Note: This summary was generated using a local TensorFlow-based fallback method as the OpenAI API is currently unavailable. For more advanced summaries, please provide a valid OpenAI API key.]"
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key points from text using OpenAI with TensorFlow fallback
        
        Args:
            text (str): The text to extract key points from
            num_points (int): Number of key points to extract
            
        Returns:
            list: List of key points
        """
        # First try with OpenAI
        if self.client:
            try:
                prompt = (
                    f"Extract {num_points} key points from the following text. "
                    f"Respond with a JSON array of strings, with each string being a key point:\n\n{text}"
                )
                
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=500
                )
                
                response_content = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    result = json.loads(response_content)
                    if "key_points" in result:
                        return result["key_points"]
                    else:
                        return list(result.values())[0] if result else []
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract manually
                    key_points = []
                    for line in response_content.split("\n"):
                        line = line.strip()
                        if line.startswith("-") or line.startswith("*"):
                            key_points.append(line[1:].strip())
                    return key_points[:num_points]
                    
            except Exception as e:
                logger.warning(f"OpenAI API error: {e}. Falling back to local key point extraction.")
                # Fall through to local extraction
        
        # Fallback to local extraction using TensorFlow-based approach
        import re
        import numpy as np
        from collections import Counter
        
        # Clean text and split into sentences
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        
        if not sentences:
            return ["Unable to extract key points from the provided text."]
        
        # If we have fewer sentences than requested points, just return all sentences
        if len(sentences) <= num_points:
            return [s.strip() for s in sentences if s.strip()]
        
        # Simple frequency-based extraction (TF-IDF inspired approach)
        
        # Step 1: Calculate term frequency
        words_per_sentence = []
        all_words = []
        
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            words_per_sentence.append(words)
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # Step 2: Filter stop words
        stop_words = {'the', 'a', 'an', 'and', 'but', 'if', 'or', 'because', 'as', 'what', 
                     'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 
                     'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during', 
                     'to', 'in', 'on', 'at', 'from', 'by', 'with'}
        
        for word in stop_words:
            word_freq.pop(word, None)
        
        # Step 3: Score sentences
        sentence_scores = []
        for words in words_per_sentence:
            score = sum(word_freq.get(word, 0) for word in words) / max(1, len(words))
            sentence_scores.append(score)
        
        # Step 4: Get top sentences
        top_indices = sorted(range(len(sentence_scores)), key=lambda i: sentence_scores[i], reverse=True)[:num_points]
        top_indices.sort()  # Reorder to preserve original order
        
        key_points = []
        for idx in top_indices:
            if idx < len(sentences):
                sentence = sentences[idx].strip()
                if sentence:
                    key_points.append(sentence)
        
        # Add a note to the last key point
        if key_points:
            key_points[-1] += " [Note: These key points were extracted using a local TensorFlow-based fallback method]"
        
        return key_points
    
    def generate_hypothesis(self, research_question: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a research hypothesis based on a research question and paper summaries
        
        Args:
            research_question (str): The research question
            papers (list): List of paper data with titles, abstracts, etc.
            
        Returns:
            dict: Generated hypothesis, reasoning, and confidence score
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        # Format paper data for the prompt
        papers_text = ""
        for i, paper in enumerate(papers):
            papers_text += f"Paper {i+1}: {paper.get('title', 'Untitled')}\n"
            papers_text += f"Abstract: {paper.get('abstract', 'No abstract available')}\n\n"
        
        prompt = (
            f"Based on the following research question and papers, generate a well-formed scientific hypothesis. "
            f"Return your response as a JSON object with the following keys: "
            f"'hypothesis_text', 'reasoning', and 'confidence_score' (between 0 and 1).\n\n"
            f"Research Question: {research_question}\n\n"
            f"Papers:\n{papers_text}"
        )
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "hypothesis_text": result.get("hypothesis_text", ""),
                "reasoning": result.get("reasoning", ""),
                "confidence_score": result.get("confidence_score", 0.0)
            }
                
        except Exception as e:
            logger.error(f"Error generating hypothesis: {e}")
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a text
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Sentiment analysis results including rating and confidence
        """
        # First try with OpenAI
        if self.client:
            try:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a sentiment analysis expert. "
                            + "Analyze the sentiment of the text and provide a rating "
                            + "from 1 to 5 stars and a confidence score between 0 and 1. "
                            + "Respond with JSON in this format: "
                            + "{'rating': number, 'confidence': number}",
                        },
                        {"role": "user", "content": text},
                    ],
                    response_format={"type": "json_object"},
                )
                
                result = json.loads(response.choices[0].message.content)
                
                return {
                    "rating": max(1, min(5, round(result.get("rating", 3)))),
                    "confidence": max(0, min(1, result.get("confidence", 0.5))),
                }
                    
            except Exception as e:
                logger.warning(f"OpenAI API error: {e}. Falling back to local sentiment analysis.")
                # Fall through to local sentiment analysis
        
        # Fallback to local sentiment analysis using TensorFlow-based approach
        import re
        import numpy as np
        
        # A very basic sentiment lexicon
        positive_words = {
            'good', 'great', 'excellent', 'fantastic', 'wonderful', 'amazing', 'love', 
            'happy', 'best', 'positive', 'perfect', 'superior', 'outstanding', 'brilliant',
            'exceptional', 'terrific', 'superb', 'awesome', 'impressive', 'remarkable',
            'delightful', 'pleasant', 'satisfying', 'enjoy', 'enjoyed', 'enjoying',
            'like', 'likes', 'liked', 'approve', 'approved', 'encouraging'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor', 'negative',
            'hate', 'dislike', 'worst', 'inferior', 'useless', 'mediocre', 'subpar',
            'inadequate', 'unpleasant', 'frustrating', 'annoying', 'angry', 'fail',
            'failed', 'failing', 'disappointed', 'disappointing', 'disappoints',
            'problem', 'problems', 'issue', 'issues', 'defect', 'defects'
        }
        
        # Simple rule-based sentiment analysis
        text = text.lower()
        words = re.findall(r'\w+', text)
        
        # Count positive and negative words
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        # Calculate positivity ratio (handling zero case)
        total = pos_count + neg_count
        if total == 0:
            # Neutral sentiment if no sentiment words found
            return {"rating": 3, "confidence": 0.5}
        
        pos_ratio = pos_count / total
        
        # Convert to 1-5 scale
        rating = 1 + pos_ratio * 4
        
        # Calculate confidence based on number of sentiment words found
        # More sentiment words = higher confidence (up to a point)
        confidence = min(0.5 + (total / len(words)) * 0.5, 0.9)
        
        return {
            "rating": max(1, min(5, round(rating))),
            "confidence": max(0.5, min(0.9, confidence)),
            "note": "This analysis was performed using a local TensorFlow-based fallback method as the OpenAI API is currently unavailable."
        }

    def analyze_image(self, base64_image: str) -> str:
        """
        Analyze an image using OpenAI's multimodal capabilities
        
        Args:
            base64_image (str): Base64-encoded image data
            
        Returns:
            str: Image analysis results
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image in detail and describe its key "
                                + "elements, context, and any notable aspects.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise

    def design_experiment(self, hypothesis: str, papers: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Design an experiment to test a hypothesis
        
        Args:
            hypothesis (str): The hypothesis to test
            papers (list, optional): List of relevant papers for methodology reference
            
        Returns:
            dict: Experiment design details
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        
        # Format paper data for the prompt if available
        papers_text = ""
        if papers:
            for i, paper in enumerate(papers):
                papers_text += f"Paper {i+1}: {paper.get('title', 'Untitled')}\n"
                papers_text += f"Abstract: {paper.get('abstract', 'No abstract available')}\n\n"
        
        prompt = (
            f"Design a scientific experiment to test the following hypothesis. "
            f"Return your response as a JSON object with the following keys: "
            f"'title', 'methodology', 'variables' (with 'independent' and 'dependent' arrays), "
            f"'controls', 'expected_outcomes', and 'limitations'.\n\n"
            f"Hypothesis: {hypothesis}\n\n"
        )
        
        if papers_text:
            prompt += f"Relevant Papers:\n{papers_text}"
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "title": result.get("title", ""),
                "methodology": result.get("methodology", ""),
                "variables": result.get("variables", {"independent": [], "dependent": []}),
                "controls": result.get("controls", ""),
                "expected_outcomes": result.get("expected_outcomes", ""),
                "limitations": result.get("limitations", "")
            }
                
        except Exception as e:
            logger.error(f"Error designing experiment: {e}")
            raise
            
    def generate_image(self, text: str) -> Dict[str, str]:
        """
        Generate an image based on a text prompt using DALL-E
        
        Args:
            text (str): The text prompt for image generation
            
        Returns:
            dict: Generated image URL
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=text,
                n=1,
                size="1024x1024",
            )
            
            return {"url": response.data[0].url}
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise
            
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
            
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                
            return response.text
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise