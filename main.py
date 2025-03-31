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
    # Get port from environment variable (for Render compatibility)
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app
    app.run(host="0.0.0.0", port=port, debug=True)