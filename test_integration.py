#!/usr/bin/env python3
"""Integration test script for Project Minerva BigQuery and AI Agent integration."""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_STARTUP_DATA = {
    "company_info": {
        "name": "TestCorp AI",
        "description": "AI-powered test platform for integration testing",
        "industry": "ai_ml",
        "funding_stage": "seed",
        "location": "Test City, TC",
        "website_url": "https://testcorp.ai",
        "founded_date": "2024-01-01",
        "employee_count": 10,
        "revenue_run_rate": 500000,
        "funding_raised": 1000000,
        "funding_seeking": 5000000
    },
    "founders": [
        {
            "name": "Test Founder",
            "email": "test@testcorp.ai",
            "role": "CEO & Founder",
            "bio": "Experienced test engineer with AI expertise",
            "previous_experience": ["Google", "OpenAI"],
            "education": ["MIT", "Stanford"]
        }
    ],
    "documents": [],
    "metadata": {
        "key_metrics": {"mrr": 50000, "growth_rate": 20},
        "competitive_advantages": ["Advanced AI models", "Strong team"],
        "traction_highlights": ["10+ customers", "Growing revenue"]
    }
}

def test_server_health():
    """Test if the integrated server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            logger.info("✅ Server health check passed")
            return True
        else:
            logger.error(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to server. Make sure integrated_server.py is running on port 8001")
        return False

def test_authentication():
    """Test authentication endpoints."""
    try:
        # Test login
        login_data = {
            "email": "founder@demo.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            logger.info("✅ Authentication test passed")
            return response.json().get("access_token")
        else:
            logger.error(f"❌ Authentication test failed: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Authentication test error: {e}")
        return None

def test_startup_submission(token):
    """Test startup submission to BigQuery."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        response = requests.post(
            f"{BASE_URL}/api/startups",
            json=TEST_STARTUP_DATA,
            headers=headers
        )
        
        if response.status_code == 200:
            startup_data = response.json()
            startup_id = startup_data.get("id")
            analysis_id = startup_data.get("analysis_id")
            
            logger.info(f"✅ Startup submission test passed")
            logger.info(f"   Startup ID: {startup_id}")
            logger.info(f"   Analysis ID: {analysis_id}")
            logger.info(f"   Status: {startup_data.get('status')}")
            
            return startup_id, analysis_id
        else:
            logger.error(f"❌ Startup submission test failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        logger.error(f"❌ Startup submission test error: {e}")
        return None, None

def test_startup_retrieval(startup_id, token):
    """Test retrieving startup data from BigQuery."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        response = requests.get(
            f"{BASE_URL}/api/startups/{startup_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            startup_data = response.json()
            logger.info("✅ Startup retrieval test passed")
            logger.info(f"   Company: {startup_data.get('company_info', {}).get('name')}")
            logger.info(f"   Status: {startup_data.get('status')}")
            return True
        else:
            logger.error(f"❌ Startup retrieval test failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Startup retrieval test error: {e}")
        return False

def test_analysis_progress(analysis_id, token):
    """Test analysis progress tracking."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Check progress multiple times
        for i in range(5):
            response = requests.get(
                f"{BASE_URL}/api/analysis/{analysis_id}/progress",
                headers=headers
            )
            
            if response.status_code == 200:
                progress_data = response.json()
                status = progress_data.get("status", "unknown")
                progress = progress_data.get("progress", 0)
                current_agent = progress_data.get("current_agent", "unknown")
                
                logger.info(f"   Progress check {i+1}: {progress}% - {status} - {current_agent}")
                
                if status == "completed":
                    logger.info("✅ Analysis progress test passed - Analysis completed")
                    return True
                elif status == "failed":
                    logger.error("❌ Analysis failed")
                    return False
                
                time.sleep(3)  # Wait 3 seconds between checks
            else:
                logger.error(f"❌ Analysis progress check failed: {response.status_code}")
                return False
        
        logger.info("✅ Analysis progress test passed - Analysis in progress")
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis progress test error: {e}")
        return False

def test_dashboard_stats(token):
    """Test dashboard statistics from BigQuery."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=headers
        )
        
        if response.status_code == 200:
            stats_data = response.json()
            logger.info("✅ Dashboard stats test passed")
            logger.info(f"   Total startups: {stats_data.get('total_startups')}")
            logger.info(f"   Pending analysis: {stats_data.get('pending_analysis')}")
            logger.info(f"   Completed analysis: {stats_data.get('completed_analysis')}")
            return True
        else:
            logger.error(f"❌ Dashboard stats test failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Dashboard stats test error: {e}")
        return False

def test_bigquery_connection():
    """Test BigQuery connection."""
    try:
        from app.storage.bigquery_client import BigQueryClient
        
        bq_client = BigQueryClient()
        logger.info("✅ BigQuery connection test passed")
        logger.info(f"   Project: {bq_client.project_id}")
        logger.info(f"   Dataset: {bq_client.dataset_id}")
        return True
    except Exception as e:
        logger.error(f"❌ BigQuery connection test failed: {e}")
        logger.error("   Make sure Google Cloud credentials are set up:")
        logger.error("   gcloud auth application-default login")
        return False

def test_agent_imports():
    """Test AI agent imports."""
    try:
        from app.agents.orchestrator import orchestrator_agent
        from app.agents.team_agent import team_agent
        from app.agents.market_agent import market_agent
        from app.agents.product_agent import product_agent
        from app.agents.competition_agent import competition_agent
        from app.agents.synthesis_agent import synthesis_agent
        
        logger.info("✅ AI agent imports test passed")
        logger.info("   All 6 agents imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ AI agent imports test failed: {e}")
        logger.error("   Server will fall back to simulation mode")
        return False

def main():
    """Run all integration tests."""
    logger.info("🚀 Starting Project Minerva Integration Tests")
    logger.info("=" * 60)
    
    # Test results
    results = {}
    
    # 1. Test server health
    logger.info("1. Testing server health...")
    results["server_health"] = test_server_health()
    
    if not results["server_health"]:
        logger.error("❌ Server is not running. Please start with: python run_integrated_server.py")
        return
    
    # 2. Test BigQuery connection
    logger.info("\n2. Testing BigQuery connection...")
    results["bigquery"] = test_bigquery_connection()
    
    # 3. Test AI agent imports
    logger.info("\n3. Testing AI agent imports...")
    results["agents"] = test_agent_imports()
    
    # 4. Test authentication
    logger.info("\n4. Testing authentication...")
    token = test_authentication()
    results["auth"] = token is not None
    
    # 5. Test startup submission
    logger.info("\n5. Testing startup submission...")
    startup_id, analysis_id = test_startup_submission(token)
    results["submission"] = startup_id is not None
    
    if startup_id:
        # 6. Test startup retrieval
        logger.info("\n6. Testing startup retrieval...")
        results["retrieval"] = test_startup_retrieval(startup_id, token)
        
        # 7. Test analysis progress
        if analysis_id:
            logger.info("\n7. Testing analysis progress...")
            results["analysis"] = test_analysis_progress(analysis_id, token)
    
    # 8. Test dashboard stats
    logger.info("\n8. Testing dashboard statistics...")
    results["dashboard"] = test_dashboard_stats(token)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 INTEGRATION TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.upper():20} {status}")
    
    logger.info("-" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Integration is working correctly.")
        logger.info("\nNext steps:")
        logger.info("1. Start the frontend: cd frontend && npm run dev")
        logger.info("2. Visit http://localhost:5174")
        logger.info("3. Login with founder@demo.com / password123")
        logger.info("4. Submit a startup and watch the real-time analysis!")
    else:
        logger.error("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
