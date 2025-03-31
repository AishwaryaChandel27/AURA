# AURA: AI-Driven Autonomous Research Assistant

<p align="center">
  <img src="generated-icon.png" alt="AURA Logo" width="200">
</p>

AURA is an AI-powered autonomous research assistant with a multi-agent system that retrieves academic papers, summarizes findings, generates hypotheses, and designs experiments using Flask and TensorFlow.

## 🚀 Features

- **Paper Retrieval**: Search and access research papers from arXiv and Semantic Scholar
- **TensorFlow Analysis**: Analyze papers and text using TensorFlow
  - Topic Classification: Identify research fields and topics in text
  - Sentiment Analysis: Determine the sentiment of research text
  - Paper Clustering: Group related papers based on content
- **Hypothesis Generation**: Generate research hypotheses based on analyzed papers
- **Experiment Design**: Create experiment designs to test hypotheses
- **Interactive Chat**: Discuss research topics with an AI assistant

## 🧠 Multi-Agent Architecture

AURA employs a multi-agent architecture with specialized components:

- **Data Retrieval Agent**: Searches and retrieves papers from academic sources
- **Summarization Agent**: Creates concise summaries of research papers
- **Hypothesis Agent**: Generates hypotheses based on research findings
- **Experiment Agent**: Designs experiments to test hypotheses
- **TensorFlow Agent**: Performs machine learning analysis on papers and research text

## 📋 Requirements

- Python 3.11+
- Flask 3.1.0+
- SQLAlchemy 2.0.40+
- TensorFlow 2.19.0+
- OpenAI API Key (for advanced features)
- Additional dependencies listed in pyproject.toml

## 🔧 Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/aura-research-assistant.git
   cd aura-research-assistant
   ```

2. Set up a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -e .
   ```

4. Set up environment variables
   ```bash
   # Required for OpenAI features
   export OPENAI_API_KEY="your_openai_api_key"
   ```

5. Create database
   ```bash
   # From Python shell
   from app import db
   db.create_all()
   ```

## 🚀 Usage

1. Start the application
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```
   
2. Open your browser and navigate to `http://localhost:5000`

## 📊 TensorFlow Features

AURA harnesses TensorFlow for various research tasks:

- **Text Analysis**
  - Topic Classification: Identify research fields from text
  - Sentiment Analysis: Analyze sentiment of research content
  
- **Paper Analysis**
  - Topic Modeling: Identify main topics across a corpus of papers
  - Research Trend Identification: Detect emerging trends in research fields
  - Paper Clustering: Group related papers based on content similarity

## 📝 API Endpoints

- `/api/health`: Health check endpoint
- `/api/analyze`: Analyze papers using TensorFlow
- `/api/analyze/text`: Analyze text using TensorFlow
- `/api/generate`: Generate text using OpenAI (requires API key)

## 📂 Project Structure

```
├── agents/                  # Multi-agent system components
│   ├── agent_controller.py  # Coordinates agent workflow
│   ├── data_retrieval_agent.py
│   ├── experiment_agent.py
│   ├── hypothesis_agent.py
│   ├── summarization_agent.py
│   └── tensorflow_agent.py
├── routes/                  # Flask application routes
│   ├── api_routes.py        # API endpoints
│   └── main_routes.py       # Web UI routes
├── services/                # Service layer components
│   ├── arxiv_service.py     # arXiv integration
│   ├── export_service.py    # Data export
│   ├── memory_service.py    # Long-term memory
│   ├── openai_service.py    # OpenAI integration
│   ├── semantic_scholar_service.py
│   └── tensorflow_service.py # TensorFlow operations
├── static/                  # Static assets
│   ├── css/
│   └── js/
├── templates/               # HTML templates
├── app.py                   # Flask application setup
├── config.py                # Configuration
├── main.py                  # Main entry point
└── models.py                # Database models
```

## 🔒 Security Notes

- AURA requires an OpenAI API key for certain features
- API keys should be kept secure and not committed to version control
- User authentication is not implemented in the current version

## 🌐 Deployment

### Render Deployment

AURA is configured for easy deployment on Render.com:

1. Fork or clone this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: Choose a name for your deployment
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`
5. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SESSION_SECRET`: Random string for session security
   - `DATABASE_URL` (optional): If using a hosted database

The application will be automatically deployed and available at your Render URL.

### Other Hosting Options

For detailed information on other deployment options, see the [INSTALLATION.md](INSTALLATION.md) file.

## 🤝 Contributing

Contributions to AURA are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.