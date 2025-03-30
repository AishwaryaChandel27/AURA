"""
Routes package for AURA Research Assistant
"""

from flask import Blueprint

# Import route blueprints
from routes.main_routes import main_bp
from routes.api_routes import api_bp

# List of all blueprints to register with the app
all_blueprints = [main_bp, api_bp]