"""
Firestore-backed Session Service for ADK Agents

This service provides persistent session storage using Firestore,
allowing conversation history to be maintained across server restarts.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session
from google.adk.events import Event
from google.genai import types as genai_types # Use genai_types for Content/Part

logger = logging.getLogger(__name__)


class FirestoreSessionService(BaseSessionService):
    """
    Firestore-backed implementation of ADK's BaseSessionService.
    
    Stores session data and conversation history in Firestore,
    enabling persistent conversations across server restarts.
    """
    
    def __init__(self, firestore_client: firestore.Client, root_collection_name: str = "adk_chat_sessions"):
        """
        Initialize the Firestore session service.
        
        Args:
            firestore_client: Initialized Firestore client
            root_collection_name: Root collection name in Firestore for storing sessions
        """
        self.db = firestore_client
        self.root_collection = root_collection_name
        logger.info(f"FirestoreSessionService initialized with collection: {root_collection_name}")
    
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session in Firestore.
        """
        try:
            session_data = {
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
                "state": state or {},
                "history": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Store in Firestore
            doc_ref = self.db.collection(self.root_collection).document(session_id)
            doc_ref.set(session_data)
            
            logger.info(f"Created new session in Firestore: {session_id} for user: {user_id}")
            
            # Create and return Session object
            session = Session(
                id=session_id,
                app_name=app_name,
                user_id=user_id,
                state=state or {}
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}", exc_info=True)
            raise
    
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> Optional[Session]:
        """
        Retrieve an existing session from Firestore.
        """
        try:
            doc_ref = self.db.collection(self.root_collection).document(session_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            session_data = doc.to_dict()
            
            if session_data.get("user_id") != user_id:
                raise Exception(f"Session {session_id} does not belong to user {user_id}")
            
            logger.info(f"Retrieved session from Firestore: {session_id}")
            
            state = session_data.get("state", {})
            history_data = session_data.get("history", [])
            
            events_history: List[Event] = []
            for msg in history_data:
                
                # --- THIS IS THE FIX ---
                # 1. Get the role from the dict
                role = msg.get("role")
                # 2. Check if it's None (which get() doesn't default for)
                if role is None:
                    role = "user"  # Default to "user" if role is null or missing
                # --- END FIX ---

                content_text = msg.get("content", "")
                
                message_content = genai_types.Content(
                    role=role,
                    parts=[genai_types.Part(text=content_text)]
                )
                
                event = Event(
                    author=role,  # This 'role' is now guaranteed to be a string
                    content=message_content
                )
                
                events_history.append(event)
            
            logger.info(f"Loaded {len(events_history)} events from history")
            
            session = Session(
                id=session_id,
                app_name=session_data.get("app_name", app_name),
                user_id=user_id,
                state=state,
                events=events_history
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}", exc_info=True)
            raise
   
    async def append_event(
        self,
        *,
        session: Session,
        event: Event  # <-- 1. Use the correct type hint
    ) -> None:
        """
        Append an event (message) to the session history.
        
        This is called by the Runner to save each message turn.
        """
        try:
            # --- THIS IS THE FIX ---
            # 2. Update the in-memory session object FIRST.
            #    This is what the Runner uses for the *current* turn.
            if session.events is None:
                session.events = []
            session.events.append(event)
            # --- END FIX ---
            
            # 3. Now, persist the event to Firestore (your existing logic)
            if hasattr(event, 'content') and event.content:
                role = getattr(event.content, 'role', 'user')
                text_parts = []
                
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                
                if text_parts:
                    content = ' '.join(text_parts)
                    
                    doc_ref = self.db.collection(self.root_collection).document(session.id)
                    doc_ref.update({
                        "history": firestore.ArrayUnion([{
                            "role": role,
                            "content": content,
                            "timestamp": datetime.utcnow()
                        }]),
                        "updated_at": datetime.utcnow()
                    })
                    
                    logger.debug(f"Appended event to session {session.id}: {role}")
                    
        except Exception as e:
            logger.warning(f"Failed to append event to session {session.id if session else 'unknown'}: {e}")
            # Don't raise - this shouldn't break the conversation flow
   
    async def update_session(
        self,
        *,
        session: Session
    ) -> None:
        """
        Update a session in Firestore.
        """
        try:
            doc_ref = self.db.collection(self.root_collection).document(session.id)
            doc_ref.update({
                "state": session.state,
                "updated_at": datetime.utcnow()
            })
            
            logger.debug(f"Updated session {session.id}")
            
        except Exception as e:
            logger.error(f"Failed to update session {session.id}: {e}", exc_info=True)
            raise
    
    async def update_session_state(
        self,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """
        Update session state in Firestore.
        """
        try:
            doc_ref = self.db.collection(self.root_collection).document(session_id)
            doc_ref.update({
                "state": state,
                "updated_at": datetime.utcnow()
            })
            logger.info(f"Updated session state: {session_id}")
        except Exception as e:
            logger.error(f"Failed to update session state {session_id}: {e}", exc_info=True)
            raise
    
    async def list_sessions(
        self,
        *,
        app_name: str,
        user_id: str
    ):
        """
        List all sessions for a user.
        """
        try:
            from google.adk.sessions.base_session_service import ListSessionsResponse
            
            sessions_ref = self.db.collection(self.root_collection)
            query = sessions_ref.where("app_name", "==", app_name).where("user_id", "==", user_id)
            docs = query.stream()
            
            sessions = []
            for doc in docs:
                session_data = doc.to_dict()
                session = Session(
                    id=session_data.get("session_id"),
                    app_name=session_data.get("app_name"),
                    user_id=session_data.get("user_id"),
                    state=session_data.get("state", {})
                )
                sessions.append(session)
            
            logger.info(f"Listed {len(sessions)} sessions for user {user_id} in app {app_name}")
            return ListSessionsResponse(sessions=sessions)
            
        except Exception as e:
            logger.error(f"Failed to list sessions for user {user_id}: {e}", exc_info=True)
            from google.adk.sessions.base_session_service import ListSessionsResponse
            return ListSessionsResponse(sessions=[])
    
    async def delete_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str
    ) -> None:
        """
        Delete a session from Firestore.
        """
        try:
            doc_ref = self.db.collection(self.root_collection).document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                session_data = doc.to_dict()
                if session_data.get("user_id") == user_id:
                    doc_ref.delete()
                    logger.info(f"Deleted session: {session_id}")
                else:
                    logger.warning(f"Cannot delete session {session_id}: user_id mismatch")
            else:
                logger.warning(f"Session {session_id} not found for deletion")
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}", exc_info=True)
            raise
    
    async def add_message_to_history(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
Read-only method, not used by ADK Runner but kept for compatibility.
        """
        try:
            doc_ref = self.db.collection(self.root_collection).document(session_id)
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            
            doc_ref.update({
                "history": firestore.ArrayUnion([message]),
                "updated_at": datetime.utcnow()
            })
            
            logger.debug(f"Added message to session {session_id} history")
        except Exception as e:
            logger.error(f"Failed to add message to session {session_id}: {e}", exc_info=True)
            raise
    
    async def get_session_history(self, session_id: str) -> list:
        """
Read-only method, not used by ADK Runner but kept for compatibility.
        """
        try:
            doc_ref = self.db.collection(self.root_collection).document(session_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return []
            
            session_data = doc.to_dict()
            return session_data.get("history", [])
            
        except Exception as e:
            logger.error(f"Failed to get session history {session_id}: {e}", exc_info=True)
            return []