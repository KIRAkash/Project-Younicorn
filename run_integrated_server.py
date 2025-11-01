#!/usr/bin/env python3
"""Startup script for the integrated Project Younicorn server."""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up environment variables
os.environ.setdefault("PYTHONPATH", str(project_root))
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("BIGQUERY_DATASET", "minerva_dataset")
os.environ.setdefault("BIGQUERY_LOCATION", "US")

# Setup Google Cloud credentials using the service account key
service_account_key_path = project_root / "minerva-key.json"
if service_account_key_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_key_path)
    
    # Set project ID from the service account key
    try:
        import json
        with open(service_account_key_path, 'r') as f:
            key_data = json.load(f)
            project_id = key_data.get("project_id")
            if project_id:
                os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main startup function."""
    try:
        logger.info("Starting Project Younicorn Integrated Server...")
        logger.info(f"Project root: {project_root}")
        logger.info(f"Python path: {sys.path[:3]}")
        
        # Import and run the FastAPI app
        import uvicorn
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
