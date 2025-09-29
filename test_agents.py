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
    """Test the Project Minerva agent system using proper ADK Runner pattern."""
    try:
        # Import the agent system
        from app.agent import minerva_analysis_agent, StartupInfo
        from google.adk.runners import InMemoryRunner
        from google.genai import types as genai_types
        import uuid
        
        logger.info("Successfully imported agent system")
        
        import json
        
        # Create test startup data (using new string-based format)
        test_startup = StartupInfo(
            company_info=json.dumps({
                "name": "TestAI Startup",
                "description": "AI-powered testing platform for developers",
                "industry": "ai_ml",
                "funding_stage": "seed",
                "location": "San Francisco, CA",
                "employee_count": 5,
                "funding_raised": 500000,
                "funding_seeking": 2000000
            }),
            founders=json.dumps([
                {
                    "name": "John Doe",
                    "email": "john@testai.com",
                    "role": "CEO",
                    "bio": "Former Google engineer with 10 years experience in AI/ML"
                }
            ]),
            documents=json.dumps([]),
            metadata=json.dumps({
                "competitive_advantages": ["Advanced AI algorithms", "Strong team"],
                "traction_highlights": ["1000+ beta users", "$10K MRR"]
            })
        )
        
        logger.info("Created test startup data")
        
        # Use proper ADK Runner pattern
        startup_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4())
        
        # Create runner (it creates its own session service internally)
        runner = InMemoryRunner(
            agent=minerva_analysis_agent,
            app_name="minerva_analysis_test"
        )
        
        # Create a session with state using the runner's session service
        session = await runner.session_service.create_session(
            app_name="minerva_analysis_test",
            user_id=f"test-user-{startup_id}",
            session_id=analysis_id,
            state={
                "startup_info": test_startup.model_dump(),
                "analysis_id": analysis_id,
                "startup_id": startup_id
            }
        )
        
        # Create user message with startup data
        user_message = genai_types.Content(
            parts=[genai_types.Part(text=f"Please analyze this startup submission: {test_startup.model_dump_json()}")]
        )
        
        logger.info("Starting agent analysis...")
        
        # Run the analysis and collect events
        try:
            events = []
            result = None
            
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=user_message
            ):
                events.append(event)
                event_id = getattr(event, 'event_id', getattr(event, 'id', 'unknown'))
                logger.info(f"Received event from {event.author}: {event_id}")
                
                # Try to extract structured result from event content
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            # Try to parse JSON from the text
                            try:
                                import json
                                # Look for JSON-like content
                                text = part.text.strip()
                                if text.startswith('{') and text.endswith('}'):
                                    parsed = json.loads(text)
                                    if isinstance(parsed, dict) and 'overall_score' in parsed:
                                        result = parsed
                                        break
                            except (json.JSONDecodeError, ValueError):
                                continue
            
            # Get final session state
            final_session = await runner.session_service.get_session(session.id)
            final_state = final_session.state if final_session else {}
            
            logger.info("Agent analysis completed successfully!")
            logger.info(f"Total events received: {len(events)}")
            logger.info(f"Result type: {type(result)}")
            
            if isinstance(result, dict):
                logger.info(f"Overall score: {result.get('overall_score', 'N/A')}")
                logger.info(f"Recommendation: {result.get('investment_recommendation', 'N/A')}")
                logger.info(f"Agent analyses: {list(result.get('agent_analyses', {}).keys())}")
            else:
                logger.info("No structured result found, but agent workflow completed")
            
            # Check session state for callback results
            agent_results = final_state.get("agent_results", {})
            if agent_results:
                logger.info(f"Agent results in session state: {list(agent_results.keys())}")
            
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
