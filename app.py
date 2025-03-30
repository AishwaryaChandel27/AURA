"""
Main Flask application for AURA Research Assistant
"""

import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

def create_app():
    """Create and configure the Flask application"""
    # Create Flask app
    app = Flask(__name__)
    
    # Configure the app
    app.secret_key = os.environ.get("SESSION_SECRET", "aura-research-assistant-dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///instance/aura.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize Flask extensions
    db.init_app(app)
    
    # Register blueprints
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        import models  # noqa: F401
        
        # Create tables
        db.create_all()
        logger.info("Database tables created")
    
    return app