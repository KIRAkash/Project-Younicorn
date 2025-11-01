"""Configuration settings for Project Younicorn API."""

import os
import json
import logging
from pathlib import Path
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.service_account_key_path = self.project_root / "minerva-key.json"
        
        # Initialize Google Cloud credentials
        self._setup_google_cloud_credentials()
        
        # API Configuration
        self.api_title = "Project Younicorn Integrated API"
        self.api_description = "AI-Powered Startup Due Diligence Platform with BigQuery Integration"
        self.api_version = "1.0.0"
        
        # CORS Configuration
        self.cors_origins = [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
            "https://younicorn-frontend-926683458739.us-central1.run.app"
        ]
        
        # BigQuery Configuration
        self.bigquery_dataset_id = "minerva_dataset"
        self.google_cloud_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        
        # Firestore Configuration
        self.firestore_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.firestore_database_id = "younicorn-fs-db"
        # Uses same service account as BigQuery (minerva-key.json)
        
        # GCS Configuration
        self.gcs_bucket_name = os.environ.get("GCS_BUCKET_NAME", "younicorns-uploads")
        
        # Demo Authentication
        self.demo_users = {
            "investor@demo.com": {
                "password": "password123",
                "role": "investor",
                "id": "investor-001",
                "name": "Demo Investor"
            },
            "founder@demo.com": {
                "password": "password123", 
                "role": "founder",
                "id": "founder-001",
                "name": "Demo Founder"
            }
        }
    
    def _setup_google_cloud_credentials(self):
        """Set up Google Cloud credentials from service account key."""
        if self.service_account_key_path.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(self.service_account_key_path)
            logger.info(f"Using service account key: {self.service_account_key_path}")
            
            # Set Google Cloud project from the service account key
            try:
                with open(self.service_account_key_path, 'r') as f:
                    key_data = json.load(f)
                    project_id = key_data.get("project_id")
                    if project_id:
                        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
                        self.google_cloud_project = project_id
                        logger.info(f"Set Google Cloud project: {project_id}")
            except Exception as e:
                logger.warning(f"Could not read service account key: {e}")
        else:
            logger.warning("Service account key not found, using default credentials")

# Global settings instance
settings = Settings()
