"""
Main entry point for AURA Research Assistant
"""

import os
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)