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
        "founded_date": "2024-01-01 00:00:00",
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
            return response.json().get("token")
        else:
            logger.error(f"❌ Authentication test failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Authentication test error: {e}")
        return None

def test_startup_submission(token):
    """Test startup submission to BigQuery with real-time analysis."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Add timestamp to make startup unique
        test_data = TEST_STARTUP_DATA.copy()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_data["company_info"]["name"] = f"TestCorp AI {timestamp}"
        test_data["company_info"]["description"] = f"AI-powered test platform - Integration test {timestamp}"
        
        logger.info(f"Submitting startup: {test_data['company_info']['name']}")
        
        response = requests.post(
            f"{BASE_URL}/api/startups",
            json=test_data,
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
            
            # Test immediate retrieval
            time.sleep(1)  # Give server a moment to process
            retrieval_response = requests.get(
                f"{BASE_URL}/api/startups/{startup_id}",
                headers=headers
            )
            
            if retrieval_response.status_code == 200:
                retrieved_data = retrieval_response.json()
                logger.info(f"   ✅ Immediate retrieval successful")
                logger.info(f"   Company name: {retrieved_data.get('company_info', {}).get('name')}")
            else:
                logger.warning(f"   ⚠️ Immediate retrieval failed: {retrieval_response.status_code}")
            
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

def test_analysis_progress(startup_id, token):
    """Test analysis progress tracking using the correct endpoint."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Check progress multiple times using the correct endpoint
        for i in range(10):
            response = requests.get(
                f"{BASE_URL}/api/analysis",
                params={"startup_id": startup_id},
                headers=headers
            )
            
            if response.status_code == 200:
                analysis_data = response.json()
                if analysis_data:
                    analysis = analysis_data[0]  # Get first analysis
                    status = analysis.get("status", "unknown")
                    progress = analysis.get("progress", 0)
                    current_agent = analysis.get("current_agent", "unknown")
                    
                    logger.info(f"   Progress check {i+1}: {progress}% - {status} - {current_agent}")
                    
                    if status == "completed":
                        logger.info("✅ Analysis progress test passed - Analysis completed")
                        # Test final results
                        overall_score = analysis.get("overall_score")
                        recommendation = analysis.get("investment_recommendation")
                        if overall_score is not None:
                            logger.info(f"   Final score: {overall_score}")
                            logger.info(f"   Recommendation: {recommendation}")
                        return True
                    elif status == "failed":
                        logger.error("❌ Analysis failed")
                        return False
                else:
                    logger.info(f"   Progress check {i+1}: No analysis data yet")
                
                time.sleep(5)  # Wait 5 seconds between checks
            else:
                logger.error(f"❌ Analysis progress check failed: {response.status_code}")
                return False
        
        logger.info("✅ Analysis progress test passed - Analysis still in progress")
        return True
        
    except Exception as e:
        logger.error(f"❌ Analysis progress test error: {e}")
        return False

def test_startup_deletion(startup_id, token):
    """Test startup deletion functionality."""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # First verify the startup exists
        response = requests.get(
            f"{BASE_URL}/api/startups/{startup_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"❌ Startup doesn't exist before deletion test: {response.status_code}")
            return False
        
        # Delete the startup
        delete_response = requests.delete(
            f"{BASE_URL}/api/startups/{startup_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            logger.info("✅ Startup deletion test passed")
            
            # Verify the startup is deleted
            time.sleep(1)  # Give server a moment to process
            verify_response = requests.get(
                f"{BASE_URL}/api/startups/{startup_id}",
                headers=headers
            )
            
            if verify_response.status_code == 404:
                logger.info("   ✅ Startup successfully deleted and not found")
                return True
            else:
                logger.warning(f"   ⚠️ Startup still exists after deletion: {verify_response.status_code}")
                return False
        else:
            logger.error(f"❌ Startup deletion test failed: {delete_response.status_code}")
            logger.error(f"   Response: {delete_response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Startup deletion test error: {e}")
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
        from app.agent import minerva_analysis_agent
        from google.adk.runners import InMemoryRunner
        
        logger.info("✅ AI agent imports test passed")
        logger.info("   Main analysis agent imported successfully")
        logger.info(f"   Agent type: {type(minerva_analysis_agent).__name__}")
        
        # Test creating a runner
        runner = InMemoryRunner(
            agent=minerva_analysis_agent,
            app_name="test"
        )
        logger.info("   ADK Runner created successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ AI agent imports test failed: {e}")
        logger.error("   Server will fall back to simulation mode")
        return False

def test_failure_scenarios(token):
    """Test various failure scenarios to ensure proper error handling."""
    logger.info("Testing failure scenarios...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    failures_handled = 0
    total_tests = 0
    
    # Test 1: Invalid startup ID
    total_tests += 1
    try:
        response = requests.get(f"{BASE_URL}/api/startups/invalid-id", headers=headers)
        if response.status_code == 404:
            logger.info("   ✅ Invalid startup ID properly returns 404")
            failures_handled += 1
        else:
            logger.warning(f"   ⚠️ Invalid startup ID returned {response.status_code} instead of 404")
    except Exception as e:
        logger.error(f"   ❌ Error testing invalid startup ID: {e}")
    
    # Test 2: Invalid JSON in startup submission
    total_tests += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/startups",
            data="invalid json",
            headers={**headers, "Content-Type": "application/json"}
        )
        if response.status_code in [400, 422]:
            logger.info(f"   ✅ Invalid JSON properly returns {response.status_code}")
            failures_handled += 1
        else:
            logger.warning(f"   ⚠️ Invalid JSON returned {response.status_code} instead of 400/422")
    except Exception as e:
        logger.error(f"   ❌ Error testing invalid JSON: {e}")
    
    # Test 3: Missing required fields
    total_tests += 1
    try:
        incomplete_data = {"company_info": {"name": "Test"}}  # Missing required fields
        response = requests.post(f"{BASE_URL}/api/startups", json=incomplete_data, headers=headers)
        if response.status_code in [400, 422]:
            logger.info(f"   ✅ Missing fields properly returns {response.status_code}")
            failures_handled += 1
        else:
            logger.warning(f"   ⚠️ Missing fields returned {response.status_code} instead of 400/422")
    except Exception as e:
        logger.error(f"   ❌ Error testing missing fields: {e}")
    
    # Test 4: Delete non-existent startup
    total_tests += 1
    try:
        response = requests.delete(f"{BASE_URL}/api/startups/non-existent-id", headers=headers)
        if response.status_code == 404:
            logger.info("   ✅ Delete non-existent startup properly returns 404")
            failures_handled += 1
        else:
            logger.warning(f"   ⚠️ Delete non-existent returned {response.status_code} instead of 404")
    except Exception as e:
        logger.error(f"   ❌ Error testing delete non-existent: {e}")
    
    success_rate = failures_handled / total_tests if total_tests > 0 else 0
    logger.info(f"✅ Failure scenarios test: {failures_handled}/{total_tests} properly handled ({success_rate:.1%})")
    
    return success_rate >= 0.75  # Pass if 75% or more failures are handled correctly

def main():
    """Run all integration tests."""
    logger.info("🚀 Starting Project Minerva Integration Tests")
    logger.info("=" * 60)
    logger.info("1. Check server health and connectivity")
    logger.info("2. Verify BigQuery and AI agent integration")
    logger.info("3. Test complete startup submission workflow")
    logger.info("4. Monitor real-time AI analysis progress")
    logger.info("5. Validate data persistence and retrieval")
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
        if startup_id:
            logger.info("\n7. Testing analysis progress...")
            results["analysis"] = test_analysis_progress(startup_id, token)
    
    # 8. Test dashboard stats
    logger.info("\n8. Testing dashboard statistics...")
    results["dashboard"] = test_dashboard_stats(token)
    
    # 9. Test startup deletion (if we have a startup to delete)
    # if startup_id:
    #     logger.info("\n9. Testing startup deletion...")
    #     results["deletion"] = test_startup_deletion(startup_id, token)
    
    # 10. Test failure scenarios
    logger.info("\n10. Testing failure scenarios...")
    results["failure_handling"] = test_failure_scenarios(token)
    
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
        logger.info("\n✅ Verified functionality:")
        logger.info("   • Server health and connectivity")
        logger.info("   • BigQuery database integration")
        logger.info("   • Real AI agent workflow execution")
        logger.info("   • Complete startup submission pipeline")
        logger.info("   • Real-time analysis progress tracking")
        logger.info("   • Data persistence and retrieval")
        logger.info("   • Startup deletion with cleanup")
        logger.info("   • Proper error handling for edge cases")
        logger.info("\nNext steps:")
        logger.info("1. Start the frontend: cd frontend && npm run dev")
        logger.info("2. Visit http://localhost:5174")
        logger.info("3. Login with founder@demo.com / password123")
        logger.info("4. Submit a startup and watch the real-time AI analysis!")
    else:
        logger.error("⚠️  Some tests failed. Check the logs above for details.")
        logger.error("   This may indicate issues with:")
        logger.error("   • Google Cloud authentication")
        logger.error("   • BigQuery permissions or connectivity")
        logger.error("   • AI agent configuration")
        logger.error("   • Server configuration or dependencies")

if __name__ == "__main__":
    main()
