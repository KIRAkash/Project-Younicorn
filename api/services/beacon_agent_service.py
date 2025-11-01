"""
Beacon AI Agent Service using Google ADK with Firestore-backed Sessions

This service implements the Beacon conversational AI agent using Google's
Agent Development Kit (ADK) with Firestore for persistent conversation history.
"""

import logging
import os
from typing import Dict, Any, List
from datetime import datetime

from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types as genai_types

from .bigquery_client import bq_client
from .firestore_client import fs_client
from .firestore_session_service import FirestoreSessionService
from .reanalysis_service import reanalysis_service
from ..config import settings

# Import the ADK-based Beacon agent
from app.agents.beacon_agent import beacon_agent

logger = logging.getLogger(__name__)


class BeaconAgentService:
    """Service for managing Beacon AI agent conversations using ADK with Firestore persistence."""
    
    def __init__(self):
        """Initialize the Beacon agent service with lazy initialization."""
        self.runner = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of the runner (called on first use)."""
        if self._initialized:
            return
        
        project_id = settings.google_cloud_project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if not project_id:
            logger.warning("No Google Cloud project configured. Beacon will not be available.")
            self._initialized = True
            return
        
        if not fs_client.db:
            logger.error("Firestore client not initialized. Cannot initialize Beacon.")
            self._initialized = True
            return
        
        try:
            # Initialize Firestore-backed session service
            logger.info(f"Initializing Beacon agent with Firestore sessions (project: {project_id})")
            
            # Create Firestore session service
            firestore_session_service = FirestoreSessionService(
                firestore_client=fs_client.db,
                root_collection_name="beacon_chat_sessions"
            )
            
            # Create in-memory artifact service (for temporary artifacts)
            artifact_service = InMemoryArtifactService()
            
            # Initialize ADK Runner with Firestore session service
            self.runner = Runner(
                agent=beacon_agent,
                app_name="beacon_chat",
                session_service=firestore_session_service,  # Firestore-backed sessions
                artifact_service=artifact_service  # In-memory artifacts
            )
            
            logger.info(f"Beacon agent initialized successfully with Firestore-backed sessions")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Beacon agent: {e}", exc_info=True)
            self._initialized = True
    
    def _build_session_state(
        self,
        user_id: str,
        startup_id: str,
        startup_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        questions_data: List[Dict[str, Any]],
        context_items: List[Dict[str, Any]],
        selected_section: str = ""
    ) -> Dict[str, Any]:
        """Build comprehensive session state for the agent."""
        import json
        
        state = {
            "user_id": user_id,
            "startup_id": startup_id,
            "current_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "startup_data": json.dumps(startup_data, indent=2, default=str),
            "analysis_data": json.dumps(analysis_data, indent=2, default=str),
            "questions_data": json.dumps(questions_data, indent=2, default=str),
            "context_items": json.dumps(context_items, indent=2, default=str),
            "selected_section": selected_section,  # Always include, even if empty string
        }
        
        return state
    
    async def chat_stream(
        self,
        user_id: str,
        startup_id: str,
        message: str,
        session_id: str,
        selected_section: str = ""
    ):
        """
        Stream chat response using Firestore-backed persistent sessions.
        
        This method uses ADK's stream_query which automatically:
        - Fetches conversation history from Firestore
        - Saves new messages back to Firestore
        - Maintains conversation continuity across sessions
        
        Args:
            user_id: User identifier
            startup_id: Startup identifier
            message: User's message
            session_id: Unique session identifier (from frontend)
            
        Yields:
            Streaming response chunks
        """
        # Ensure runner is initialized (lazy initialization)
        self._ensure_initialized()
        
        if not self.runner:
            raise Exception("Beacon AI service is not available")
        
        try:
            # Fetch startup and analysis data for session state
            startup_data = {}
            analysis_data = {}
            questions_data = []
            
            try:
                # Get startup data
                startup_query = f"""
                    SELECT *
                    FROM `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startups`
                    WHERE id = '{startup_id}'
                    LIMIT 1
                """
                startup_results = bq_client.query(startup_query)
                startup_data = next(iter(startup_results), {})
                
                # Get latest analysis
                analysis_query = f"""
                    SELECT *
                    FROM `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.analyses`
                    WHERE startup_id = '{startup_id}'
                    ORDER BY started_at DESC
                    LIMIT 1
                """
                analysis_results = bq_client.query(analysis_query)
                analysis_data = next(iter(analysis_results), {})
                
                # Get questions
                questions_data = fs_client.get_questions(startup_id)
                
            except Exception as e:
                logger.warning(f"Failed to fetch startup data: {e}")
            
            # Build session state (WITHOUT history - history is in events)
            session_state = self._build_session_state(
                user_id=user_id,
                startup_id=startup_id,
                startup_data=startup_data,
                analysis_data=analysis_data,
                questions_data=questions_data,
                context_items=[],
                selected_section=selected_section
            )
            
            # Get or create session in Firestore
            try:
                # This will return a Session object with .events populated
                existing_session = await self.runner.session_service.get_session(
                    app_name="beacon_chat",
                    user_id=user_id,
                    session_id=session_id
                )
            except Exception as e:
                logger.warning(f"Failed to get session, will create a new one. Error: {e}")
                existing_session = None
            
            if existing_session:
                logger.info(f"Updating existing Firestore session: {session_id}")
                
                # Just update the state. The Runner will use the .events
                # that were already loaded by get_session
                await self.runner.session_service.update_session_state(
                    session_id=session_id,
                    state=session_state
                )
            else:
                # Session doesn't exist, create new one
                logger.info(f"Creating new Firestore session: {session_id}")
                await self.runner.session_service.create_session(
                    app_name="beacon_chat",
                    user_id=user_id,
                    session_id=session_id,
                    state=session_state
                )
            
            # Stream response using ADK's run_async
            # This automatically handles conversation history from Firestore
            user_message = genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=message)]
            )
            
            # Stream events from the agent
            # The Runner automatically saves conversation history to Firestore
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                # Extract text content from event
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield {
                                "type": "content",
                                "data": {"text": part.text}
                            }
            
            # Send done event
            yield {
                "type": "done",
                "data": {
                    "finish_reason": "STOP"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Beacon chat stream: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": {"error": str(e)}
            }
    
    async def chat(
        self,
        user_id: str,
        startup_id: str,
        message: str,
        session_id: str,
        selected_section: str = ""
    ) -> Dict[str, Any]:
        """
        Non-streaming chat response (for backward compatibility).
        
        Args:
            user_id: User identifier
            startup_id: Startup identifier
            message: User's message
            session_id: Unique session identifier
            
        Returns:
            Complete response dictionary
        """
        accumulated_text = ""
        error = None
        
        try:
            async for event in self.chat_stream(user_id, startup_id, message, session_id, selected_section):
                if event["type"] == "content":
                    accumulated_text += event["data"]["text"]
                elif event["type"] == "error":
                    error = event["data"]["error"]
                    break
            
            if error:
                return {
                    "success": False,
                    "message": None,
                    "error": error,
                    "tool_calls": [],
                    "finish_reason": "ERROR"
                }
            
            return {
                "success": True,
                "message": accumulated_text,
                "tool_calls": [],
                "finish_reason": "STOP",
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error in Beacon chat: {e}", exc_info=True)
            return {
                "success": False,
                "message": None,
                "error": str(e),
                "tool_calls": [],
                "finish_reason": "ERROR"
            }


# Create singleton instance
beacon_agent_service = BeaconAgentService()
