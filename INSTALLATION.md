# Detailed Installation Guide for AURA

This document provides detailed installation instructions for setting up the AURA Research Assistant on your local machine or server.

## Prerequisites

Before installing AURA, ensure you have the following prerequisites:

- **Python 3.11 or higher** (required by dependencies)
- **pip** (Python package installer)
- **git** (for cloning the repository)
- **OpenAI API key** (for advanced features)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/aura-research-assistant.git
cd aura-research-assistant
```

### 2. Set Up a Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with other Python projects.

**For Unix/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

AURA relies on several Python packages listed in pyproject.toml. Install them with:

```bash
pip install -e .
```

Alternatively, you can install the dependencies directly:

```bash
pip install flask flask-sqlalchemy gunicorn numpy openai scikit-learn sqlalchemy tensorflow
```

### 4. Set Up Environment Variables

AURA requires an OpenAI API key for certain features.

**For Unix/macOS:**
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

**For Windows:**
```bash
set OPENAI_API_KEY=your_openai_api_key
```

For persistent environment variables, consider adding them to your shell profile or creating a `.env` file.

### 5. Initialize the Database

AURA uses SQLite by default, which doesn't require additional setup.

```python
# From the Python shell
from app import db, create_app
app = create_app()
with app.app_context():
    db.create_all()
```

### 6. Run the Application

Start the application using Gunicorn (recommended for production):

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

Alternatively, for development:

```bash
python main.py
```

The application will be available at `http://localhost:5000`.

## Common Installation Issues

### 1. TensorFlow Installation

If you encounter issues with TensorFlow installation:

```bash
pip install tensorflow==2.10.0  # Or the latest stable version
```

### 2. Database Connection Issues

If you encounter database connection issues:

```bash
# Check the database URI in config.py or app.py
# Ensure the path exists and is writable
```

### 3. OpenAI API Authentication Errors

If you encounter OpenAI API authentication errors:

- Verify your API key is correct
- Check that the environment variable is properly set
- Ensure your account has sufficient credits

## Deployment Considerations

### Systemd Service (Linux)

For a persistent service on Linux systems, create a systemd service file:

```
[Unit]
Description=AURA Research Assistant
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/aura-research-assistant
Environment="OPENAI_API_KEY=your_openai_api_key"
ExecStart=/path/to/venv/bin/gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

A Dockerfile is included in the repository. Build and run the Docker container with:

```bash
docker build -t aura-research-assistant .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_openai_api_key aura-research-assistant
```

## Troubleshooting

If you encounter any issues during installation or deployment, please check the following:

1. Python version (3.11+ required)
2. Pip installation is up-to-date
3. Virtual environment is activated
4. All dependencies are correctly installed
5. Environment variables are properly set
6. Database initialization was successful

For further assistance, please open an issue on the GitHub repository.