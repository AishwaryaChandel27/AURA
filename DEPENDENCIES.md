# AURA Dependencies

This document provides detailed information about the dependencies used in the AURA Research Assistant project.

## Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flask | >=3.1.0 | Web framework for building the application |
| flask-sqlalchemy | >=3.1.1 | SQLAlchemy integration for Flask |
| gunicorn | >=23.0.0 | WSGI HTTP server for deploying the application |
| numpy | >=2.1.3 | Numerical computing for data manipulation |
| openai | >=1.69.0 | OpenAI API client for AI capabilities |
| scikit-learn | >=1.6.1 | Machine learning algorithms |
| sqlalchemy | >=2.0.40 | SQL toolkit and ORM |
| tensorflow | >=2.19.0 | Machine learning framework |

## Primary Package Purposes

### Web Framework

- **Flask**: A lightweight WSGI web application framework that provides the foundation for AURA's web interface and API endpoints.
- **Flask-SQLAlchemy**: An extension for Flask that adds support for SQLAlchemy, simplifying database operations.
- **Gunicorn**: A Python WSGI HTTP server for production deployment of the application.

### Data Science & AI

- **NumPy**: A fundamental package for scientific computing with Python, used for numerical operations throughout the application.
- **OpenAI**: Client library for interacting with OpenAI's API, enabling advanced AI capabilities like text generation and summarization.
- **scikit-learn**: A machine learning library that provides efficient tools for data analysis and modeling, used for classification and clustering tasks.
- **TensorFlow**: An open-source machine learning framework for building and training neural networks, used for advanced analysis of research papers.

### Database & ORM

- **SQLAlchemy**: A SQL toolkit and Object-Relational Mapping (ORM) library for Python, providing a set of high-level API for communicating with relational databases.

## Secondary Dependencies

These are dependencies used by the primary packages:

| Package | Purpose |
|---------|---------|
| click | Command-line interface creation |
| itsdangerous | Securely signing data |
| Jinja2 | Template engine for HTML rendering |
| MarkupSafe | String handling for HTML safety |
| Werkzeug | WSGI web application library |
| requests | HTTP library for API calls |
| tqdm | Progress bar utility |
| typing-extensions | Type hint extensions |
| aiohttp | Asynchronous HTTP client/server |
| h5py | Binary data format for TensorFlow models |
| Pillow | Image processing capability |
| six | Python 2 and 3 compatibility |

## Development Dependencies

These packages are recommended for development but not required for production:

| Package | Purpose |
|---------|---------|
| black | Code formatting |
| flake8 | Code linting |
| isort | Import sorting |
| mypy | Static type checking |
| pytest | Testing framework |
| pytest-cov | Test coverage |

## Compatibility Notes

- **Python**: AURA requires Python 3.10 or higher
- **TensorFlow**: The application uses TensorFlow 2.x with CPU support by default. For GPU acceleration, additional setup is required.
- **OpenAI API**: The application is compatible with the OpenAI API as of March 2025.

## Dependency Management

Dependencies are managed through [Python poetry](https://python-poetry.org/) and defined in the `pyproject.toml` file.

To update dependencies:

```bash
pip install -U flask flask-sqlalchemy gunicorn numpy openai scikit-learn sqlalchemy tensorflow
```

To freeze current dependencies for reproducibility:

```bash
pip freeze > requirements.txt
```