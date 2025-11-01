"""
Beacon AI Agent API Routes with Firestore-backed Persistent Sessions

Endpoints for the Beacon conversational AI assistant using ADK's stream_query
with Firestore for persistent conversation history.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..services.beacon_agent_service import beacon_agent_service
from .firebase_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/beacon", tags=["beacon"])


# Request/Response Models

class ChatRequest(BaseModel):
    """Request to chat with Beacon using persistent sessions."""
    startup_id: str = Field(..., description="Startup identifier")
    message: str = Field(..., description="User's message")
    session_id: str = Field(..., description="Unique session ID for conversation persistence")
    selected_section: str = Field("", description="Section context from analysis page (empty string if none)")


class ChatResponse(BaseModel):
    """Response from Beacon."""
    success: bool = Field(..., description="Whether the request succeeded")
    message: str = Field(default="", description="Agent's response message")
    tool_calls: list = Field(default_factory=list, description="Tools executed")
    finish_reason: Optional[str] = Field(None, description="Generation finish reason")
    error: Optional[str] = Field(None, description="Error message if failed")


# Endpoints

@router.post("/chat-stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Stream chat response with Beacon using Firestore-backed persistent sessions.
    
    This endpoint uses ADK's stream_query which automatically:
    - Fetches conversation history from Firestore
    - Saves new messages back to Firestore
    - Maintains conversation continuity across sessions
    
    **Features:**
    - Persistent conversation history (survives server restarts)
    - Real-time streaming responses
    - Automatic history management
    - No need to send conversation_history from frontend
    
    **Request:**
    ```json
    {
        "startup_id": "startup_123",
        "message": "What is the market size?",
        "session_id": "user123_startup123"  // Unique per user+startup
    }
    ```
    
    **Response (text/plain streaming):**
    ```
    Looking at the Market Analysis...
    The total addressable market is $2.5B...
    ```
    """
    try:
        user_id = current_user.get("uid")
        
        logger.info(f"Beacon streaming chat from user {user_id} for startup {request.startup_id}, session: {request.session_id}")
        
        # Stream generator
        async def stream_generator():
            try:
                async for event in beacon_agent_service.chat_stream(
                    user_id=user_id,
                    startup_id=request.startup_id,
                    message=request.message,
                    session_id=request.session_id,
                    selected_section=request.selected_section
                ):
                    if event["type"] == "content":
                        # Yield just the text content
                        yield event["data"]["text"]
                    elif event["type"] == "error":
                        yield f"\n\nError: {event['data']['error']}"
                        break
            except Exception as e:
                logger.error(f"Error in stream generator: {e}", exc_info=True)
                yield f"\n\nError: {str(e)}"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in chat-stream endpoint: {e}", exc_info=True)
        return StreamingResponse(
            iter([f"Error: {str(e)}"]),
            status_code=500,
            media_type="text/plain"
        )


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Non-streaming chat with Beacon using Firestore-backed persistent sessions.
    
    This endpoint provides backward compatibility for non-streaming clients.
    It still uses Firestore for conversation history persistence.
    
    **Features:**
    - Persistent conversation history
    - Complete response (waits for full generation)
    - Automatic history management
    
    **Request:**
    ```json
    {
        "startup_id": "startup_123",
        "message": "What is the market size?",
        "session_id": "user123_startup123"
    }
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "message": "Looking at the Market Analysis, the TAM is $2.5B...",
        "tool_calls": [],
        "finish_reason": "STOP"
    }
    ```
    """
    try:
        user_id = current_user.get("uid")
        
        logger.info(f"Beacon chat from user {user_id} for startup {request.startup_id}, session: {request.session_id}")
        
        result = await beacon_agent_service.chat(
            user_id=user_id,
            startup_id=request.startup_id,
            message=request.message,
            session_id=request.session_id,
            selected_section=request.selected_section
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Failed to process chat message")
            logger.error(f"Beacon service returned error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Beacon chat successful, message length: {len(result.get('message', ''))}")
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Beacon service.
    
    Returns the service status and configuration.
    """
    return {
        "status": "healthy",
        "service": "beacon",
        "agent": "beacon_agent (ADK + Firestore)",
        "session_persistence": "firestore",
        "streaming_supported": True,
        "features": [
            "persistent_conversations",
            "firestore_backed_history",
            "contextual_chat",
            "streaming_responses",
            "automatic_history_management",
            "multi_turn_conversation"
        ]
    }
