#!/usr/bin/env python3
"""Test script to verify Google Cloud authentication and ADK dependencies."""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup service account credentials
service_account_key_path = project_root / "minerva-key.json"

if service_account_key_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_key_path)
    print(f"✅ Service account key found: {service_account_key_path}")
    
    # Read and display project info
    try:
        with open(service_account_key_path, 'r') as f:
            key_data = json.load(f)
            project_id = key_data.get("project_id")
            client_email = key_data.get("client_email")
            
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            
            print(f"📋 Project ID: {project_id}")
            print(f"📧 Service Account: {client_email}")
            
    except Exception as e:
        print(f"❌ Error reading service account key: {e}")
        sys.exit(1)
else:
    print(f"❌ Service account key not found at: {service_account_key_path}")
    sys.exit(1)

# Test Google Cloud authentication
try:
    print("\n🔐 Testing Google Cloud authentication...")
    
    import google.auth
    credentials, project = google.auth.default()
    print(f"✅ Authentication successful")
    print(f"📋 Authenticated project: {project}")
    print(f"🔑 Credentials type: {type(credentials).__name__}")
    
    # Test if credentials are valid
    if hasattr(credentials, 'valid') and not credentials.valid:
        if hasattr(credentials, 'refresh'):
            print("🔄 Refreshing credentials...")
            import google.auth.transport.requests
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            print("✅ Credentials refreshed")
    
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    print("   Make sure to run: gcloud auth application-default login")
    sys.exit(1)

# Test BigQuery access
try:
    print("\n📊 Testing BigQuery access...")
    
    from google.cloud import bigquery
    client = bigquery.Client()
    
    print(f"✅ BigQuery client created successfully")
    print(f"📋 BigQuery project: {client.project}")
    
    # List datasets
    datasets = list(client.list_datasets())
    print(f"📁 Found {len(datasets)} datasets")
    
    for dataset in datasets:
        print(f"   - {dataset.dataset_id}")
    
except Exception as e:
    print(f"❌ BigQuery access failed: {e}")
    print("   Make sure the service account has BigQuery permissions")

# Test Vertex AI access
try:
    print("\n🤖 Testing Vertex AI access...")
    
    # Set Vertex AI environment variables
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    # Try to import and initialize Vertex AI
    import vertexai
    vertexai.init(project=project_id, location="us-central1")
    
    print(f"✅ Vertex AI initialized successfully")
    print(f"📋 Vertex AI project: {project_id}")
    print(f"🌍 Vertex AI location: us-central1")
    
except Exception as e:
    print(f"❌ Vertex AI access failed: {e}")
    print("   Make sure the service account has Vertex AI permissions")

# Test ADK imports
try:
    print("\n🤖 Testing ADK imports...")
    from google.adk.runners import InMemoryRunner
    from google.adk.agents import SequentialAgent
    print("✅ ADK imports successful")
    print(f"   InMemoryRunner: {InMemoryRunner}")
    print(f"   SequentialAgent: {SequentialAgent}")
except Exception as e:
    print(f"❌ ADK imports failed: {e}")

# Test agent imports
try:
    print("\n🧠 Testing agent imports...")
    from app.agent import minerva_analysis_agent, StartupInfo
    print("✅ Agent imports successful")
    print(f"   Main agent type: {type(minerva_analysis_agent).__name__}")
    print(f"   StartupInfo model: {StartupInfo}")
except Exception as e:
    print(f"❌ Agent imports failed: {e}")
    print("   This may cause the server to fall back to simulation mode")

print("\n🎉 Authentication and dependency test completed!")
print("\nNext steps:")
print("1. Run: make dev-backend")
print("2. Run: uv run python test_integration.py")
print("3. The server should now use real AI agents with proper authentication")
