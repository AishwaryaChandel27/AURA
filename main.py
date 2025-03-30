"""
Main entry point for AURA Research Assistant
"""

from app import create_app

# Create the Flask application
app = create_app()

# This app instance is used by gunicorn
# The if block below is only used when running the app directly with python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)