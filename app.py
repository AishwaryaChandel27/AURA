"""
Main Flask application for AURA Research Assistant
"""

import os
import logging
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure the secret key
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-aura-secret-key")
    
    # Create instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Configure the SQLite database with absolute path
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'aura.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize the app with the extension
    db.init_app(app)
    
    @app.template_filter('format_date')
    def format_date_filter(date):
        """Format a date for display"""
        if not date:
            return "Unknown"
        return date.strftime("%b %d, %Y")
    
    # Register utility functions with Jinja templates
    @app.context_processor
    def utility_processor():
        """Add utility functions to templates"""
        def format_date(date):
            if not date:
                return "Unknown"
            return date.strftime("%b %d, %Y")
        
        return dict(format_date=format_date)
    
    # Import and register blueprints
    with app.app_context():
        from routes.main_routes import main_bp
        from routes.api_routes import api_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix="/api")
        
        # Create database tables
        import models  # noqa
        db.create_all()
        
        logger.info("Database tables created")
    
    return app