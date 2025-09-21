#!/usr/bin/env python3
"""Test script for Project Minerva agent system."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_system():
    """Test the Project Minerva agent system."""
    try:
        # Import the agent system
        from app.agent import minerva_analysis_agent, StartupInfo
        from google.adk.agents.callback_context import CallbackContext
        
        logger.info("Successfully imported agent system")
        
        # Create test startup data
        test_startup = StartupInfo(
            company_info={
                "name": "TestAI Startup",
                "description": "AI-powered testing platform for developers",
                "industry": "ai_ml",
                "funding_stage": "seed",
                "location": "San Francisco, CA",
                "employee_count": 5,
                "funding_raised": 500000,
                "funding_seeking": 2000000
            },
            founders=[
                {
                    "name": "John Doe",
                    "email": "john@testai.com",
                    "role": "CEO",
                    "bio": "Former Google engineer with 10 years experience in AI/ML"
                }
            ],
            documents=[],
            metadata={
                "competitive_advantages": ["Advanced AI algorithms", "Strong team"],
                "traction_highlights": ["1000+ beta users", "$10K MRR"]
            }
        )
        
        logger.info("Created test startup data")
        
        # Create callback context
        callback_context = CallbackContext(invocation_context=object())
        callback_context.state = {
            "analysis_id": "test-analysis-123",
            "startup_id": "test-startup-123"
        }
        
        logger.info("Starting agent analysis...")
        
        # Run the analysis (with timeout for testing)
        try:
            result = await asyncio.wait_for(
                minerva_analysis_agent.run_async(
                    input_data=test_startup.dict(),
                    callback_context=callback_context
                ),
                timeout=300  # 5 minute timeout
            )
            
            logger.info("Agent analysis completed successfully!")
            logger.info(f"Result type: {type(result)}")
            
            if isinstance(result, dict):
                logger.info(f"Overall score: {result.get('overall_score', 'N/A')}")
                logger.info(f"Recommendation: {result.get('investment_recommendation', 'N/A')}")
                logger.info(f"Agent analyses: {list(result.get('agent_analyses', {}).keys())}")
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("Agent analysis timed out")
            return False
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed")
        return False
        
    except Exception as e:
        logger.error(f"Error testing agent system: {e}")
        return False

def main():
    """Main test function."""
    logger.info("Testing Project Minerva Agent System")
    logger.info("=" * 50)
    
    success = asyncio.run(test_agent_system())
    
    if success:
        logger.info("✅ Agent system test PASSED")
        sys.exit(0)
    else:
        logger.error("❌ Agent system test FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
