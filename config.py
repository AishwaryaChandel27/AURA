import os

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
OPENAI_MODEL = "gpt-4o"

# API Configuration
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1"
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "research_memory"

# Agent Configuration
AGENT_MEMORY_LIMIT = 50  # Number of items to keep in agent memory
MAX_PAPERS_PER_QUERY = 10  # Maximum number of papers to retrieve per query
SUMMARY_MAX_TOKENS = 1000  # Maximum number of tokens for paper summaries
