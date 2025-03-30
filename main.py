"""
Main entry point for AURA Research Assistant
"""

import logging
from app import create_app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask application
app = create_app()

if __name__ == "__main__":
    # Run the Flask application
    logger.info("Starting AURA Research Assistant")
    app.run(host="0.0.0.0", port=5000, debug=True)