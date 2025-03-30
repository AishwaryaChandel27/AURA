"""
Main Flask application for AURA Research Assistant
"""

import os
import logging
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy extension
db = SQLAlchemy(model_class=Base)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure the application
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///instance/aura.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Initialize extensions
    db.init_app(app)
    
    # Register template utilities
    @app.context_processor
    def utility_processor():
        """Add utility functions to templates"""
        def format_date(date):
            if date:
                return date.strftime("%b %d, %Y")
            return ""
        
        return dict(format_date=format_date)
    
    # Register blueprints
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        import models  # noqa: F401
        
        # Import and register blueprints
        from routes.main_routes import main_bp
        from routes.api_routes import api_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix="/api")
        
        # Create database tables
        db.create_all()
        
        logger.info("Flask application configured and database tables created")
    
    return app