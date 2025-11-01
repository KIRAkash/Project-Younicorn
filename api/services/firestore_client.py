"""
Firestore client for real-time features.
Handles questions, notifications, and activity feed.
"""
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FirestoreClient:
    """Client for Firestore operations."""
    
    def __init__(self):
        """Initialize Firestore client."""
        self.db: Optional[firestore.Client] = None
        
    def initialize(self):
        """Initialize the Firestore client."""
        try:
            self.db = firestore.Client(database='younicorn-fs-db')
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise
    
    # ==================== Questions ====================
    
    def create_question(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new question.
        
        Args:
            data: Question data including startup_id, asked_by, question_text, etc.
            
        Returns:
            Created question document with ID
        """
        try:
            # Add timestamps
            data['created_at'] = firestore.SERVER_TIMESTAMP
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            data['answer'] = None  # No answer yet
            
            # Create document
            doc_ref = self.db.collection('questions').document()
            doc_ref.set(data)
            
            # Get the created document
            doc = doc_ref.get()
            result = doc.to_dict()
            result['id'] = doc.id
            
            logger.info(f"Created question {doc.id} for startup {data.get('startup_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            raise
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single question by ID.
        
        Args:
            question_id: Question document ID
            
        Returns:
            Question document or None if not found
        """
        try:
            doc = self.db.collection('questions').document(question_id).get()
            if doc.exists:
                result = doc.to_dict()
                result['id'] = doc.id
                return result
            return None
        except Exception as e:
            logger.error(f"Error getting question {question_id}: {e}")
            raise
    
    def update_question(self, question_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a question (e.g., add answer, change status).
        
        Args:
            question_id: Question document ID
            data: Fields to update
            
        Returns:
            Updated question document
        """
        try:
            # Add updated timestamp
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Update document
            doc_ref = self.db.collection('questions').document(question_id)
            doc_ref.update(data)
            
            # Get updated document
            doc = doc_ref.get()
            result = doc.to_dict()
            result['id'] = doc.id
            
            logger.info(f"Updated question {question_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating question {question_id}: {e}")
            raise
    
    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question.
        
        Args:
            question_id: Question document ID
            
        Returns:
            True if deleted successfully
        """
        try:
            self.db.collection('questions').document(question_id).delete()
            logger.info(f"Deleted question {question_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting question {question_id}: {e}")
            raise
    
    def get_questions_by_startup(
        self, 
        startup_id: str, 
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all questions for a startup, sorted by priority (high > medium > low) then by created_at.
        
        Args:
            startup_id: Startup ID
            status: Optional filter by status (pending, answered, clarification_needed)
            limit: Maximum number of questions to return
            
        Returns:
            List of question documents sorted by priority
        """
        try:
            query = self.db.collection('questions').where(
                filter=FieldFilter('startup_id', '==', startup_id)
            )
            
            if status:
                query = query.where(filter=FieldFilter('status', '==', status))
            
            # Get all questions first (we'll sort in memory for priority)
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            questions = []
            for doc in docs:
                question = doc.to_dict()
                question['id'] = doc.id
                questions.append(question)
            
            # Sort by priority (high > medium > low), then by created_at (newest first)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            questions.sort(
                key=lambda q: (
                    priority_order.get(q.get('priority', 'medium'), 1),  # Priority first
                    -(q.get('created_at').timestamp() if q.get('created_at') else 0)  # Then by date (newest first)
                )
            )
            
            logger.info(f"Retrieved and sorted {len(questions)} questions for startup {startup_id} by priority")
            return questions
            
        except Exception as e:
            logger.error(f"Error getting questions for startup {startup_id}: {e}")
            raise
    
    def get_questions_by_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all questions asked by a user, sorted by priority (high > medium > low) then by created_at.
        
        Args:
            user_id: User ID (investor)
            limit: Maximum number of questions to return
            
        Returns:
            List of question documents sorted by priority
        """
        try:
            query = self.db.collection('questions').where(
                filter=FieldFilter('asked_by', '==', user_id)
            ).order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            questions = []
            for doc in docs:
                question = doc.to_dict()
                question['id'] = doc.id
                questions.append(question)
            
            # Sort by priority (high > medium > low), then by created_at (newest first)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            questions.sort(
                key=lambda q: (
                    priority_order.get(q.get('priority', 'medium'), 1),  # Priority first
                    -(q.get('created_at').timestamp() if q.get('created_at') else 0)  # Then by date (newest first)
                )
            )
            
            logger.info(f"Retrieved and sorted {len(questions)} questions by user {user_id} by priority")
            return questions
            
        except Exception as e:
            logger.error(f"Error getting questions by user {user_id}: {e}")
            raise
    
    # ==================== Notifications ====================
    
    def create_notification(
        self,
        user_id: str,
        type: str,
        title: str,
        message: str,
        related_id: str,
        related_type: str
    ) -> Dict[str, Any]:
        """
        Create a notification for a user.
        
        Args:
            user_id: User ID to notify
            type: Notification type (new_question, question_answered, etc.)
            title: Notification title
            message: Notification message
            related_id: ID of related entity (question, startup, analysis)
            related_type: Type of related entity
            
        Returns:
            Created notification document
        """
        try:
            data = {
                'user_id': user_id,
                'type': type,
                'title': title,
                'message': message,
                'related_id': related_id,
                'related_type': related_type,
                'read': False,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref = self.db.collection('notifications').document()
            doc_ref.set(data)
            
            doc = doc_ref.get()
            result = doc.to_dict()
            result['id'] = doc.id
            
            logger.info(f"Created notification for user {user_id}: {type}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise
    
    def get_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
            
        Returns:
            List of notification documents
        """
        try:
            query = self.db.collection('notifications').where(
                filter=FieldFilter('user_id', '==', user_id)
            )
            
            if unread_only:
                query = query.where(filter=FieldFilter('read', '==', False))
            
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            notifications = []
            for doc in docs:
                notification = doc.to_dict()
                notification['id'] = doc.id
                notifications.append(notification)
            
            logger.info(f"Retrieved {len(notifications)} notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting notifications for user {user_id}: {e}")
            raise
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification document ID
            
        Returns:
            True if marked successfully
        """
        try:
            self.db.collection('notifications').document(notification_id).update({
                'read': True
            })
            logger.info(f"Marked notification {notification_id} as read")
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            raise
    
    def mark_all_notifications_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        try:
            query = self.db.collection('notifications').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).where(filter=FieldFilter('read', '==', False))
            
            docs = query.stream()
            count = 0
            for doc in docs:
                doc.reference.update({'read': True})
                count += 1
            
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            raise
    
    def get_unread_count(self, user_id: str) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        try:
            query = self.db.collection('notifications').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).where(filter=FieldFilter('read', '==', False))
            
            docs = list(query.stream())
            count = len(docs)
            
            logger.info(f"User {user_id} has {count} unread notifications")
            return count
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            raise
    
    # ==================== Activity Feed ====================
    
    def create_activity(
        self,
        startup_id: str,
        user_id: str,
        user_name: str,
        activity_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an activity feed entry.
        
        Args:
            startup_id: Startup ID
            user_id: User ID who performed the action
            user_name: User display name
            activity_type: Type of activity
            description: Activity description
            metadata: Optional additional metadata
            
        Returns:
            Created activity document
        """
        try:
            data = {
                'startup_id': startup_id,
                'user_id': user_id,
                'user_name': user_name,
                'activity_type': activity_type,
                'description': description,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'metadata': metadata or {}
            }
            
            doc_ref = self.db.collection('activity_feed').document()
            doc_ref.set(data)
            
            doc = doc_ref.get()
            result = doc.to_dict()
            result['id'] = doc.id
            
            logger.info(f"Created activity for startup {startup_id}: {activity_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating activity: {e}")
            raise
    
    def get_activity_by_startup(self, startup_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get activity feed for a startup.
        
        Args:
            startup_id: Startup ID
            limit: Maximum number of activities to return
            
        Returns:
            List of activity documents
        """
        try:
            query = self.db.collection('activity_feed').where(
                filter=FieldFilter('startup_id', '==', startup_id)
            ).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            activities = []
            for doc in docs:
                activity = doc.to_dict()
                activity['id'] = doc.id
                activities.append(activity)
            
            logger.info(f"Retrieved {len(activities)} activities for startup {startup_id}")
            return activities
            
        except Exception as e:
            logger.error(f"Error getting activity for startup {startup_id}: {e}")
            raise
    
    def get_activity_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get activity feed for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of activities to return
            
        Returns:
            List of activity documents
        """
        try:
            query = self.db.collection('activity_feed').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            activities = []
            for doc in docs:
                activity = doc.to_dict()
                activity['id'] = doc.id
                activities.append(activity)
            
            logger.info(f"Retrieved {len(activities)} activities for user {user_id}")
            return activities
            
        except Exception as e:
            logger.error(f"Error getting activity for user {user_id}: {e}")
            raise
    
    # ==================== Beacon Helper Methods ====================
    
    def get_startup(self, startup_id: str) -> Optional[Dict[str, Any]]:
        """
        Get startup data from Firestore.
        
        Args:
            startup_id: Startup document ID
            
        Returns:
            Startup document or None if not found
        """
        try:
            doc = self.db.collection('startups').document(startup_id).get()
            if doc.exists:
                result = doc.to_dict()
                result['id'] = doc.id
                return result
            return None
        except Exception as e:
            logger.error(f"Error getting startup {startup_id}: {e}")
            raise
    
    def get_questions(self, startup_id: str) -> List[Dict[str, Any]]:
        """
        Get all questions for a startup (alias for get_questions_by_startup).
        
        Args:
            startup_id: Startup identifier
            
        Returns:
            List of question documents
        """
        return self.get_questions_by_startup(startup_id)
    
    def add_question(self, startup_id: str, question_data: Dict[str, Any]) -> str:
        """
        Add a new question (alias for create_question).
        
        Args:
            startup_id: Startup identifier
            question_data: Question data
            
        Returns:
            Question document ID
        """
        question_data['startup_id'] = startup_id
        result = self.create_question(question_data)
        return result['id']
    
    # def add_note(self, startup_id: str, note_data: Dict[str, Any]) -> str:
    #     """
    #     Add a private investor note about a startup.
        
    #     Args:
    #         startup_id: Startup identifier
    #         note_data: Note data including note_text, note_type, created_by
            
    #     Returns:
    #         Note document ID
    #     """
    #     try:
    #         note_data['startup_id'] = startup_id
    #         note_data['created_at'] = firestore.SERVER_TIMESTAMP
    #         note_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
    #         doc_ref = self.db.collection('notes').document()
    #         doc_ref.set(note_data)
            
    #         logger.info(f"Created note {doc_ref.id} for startup {startup_id}")
    #         return doc_ref.id
            
    #     except Exception as e:
    #         logger.error(f"Error creating note: {e}")
    #         raise
    
    # def update_startup_status(self, startup_id: str, status_data: Dict[str, Any]) -> bool:
    #     """
    #     Update startup status in the investment pipeline.
        
    #     Args:
    #         startup_id: Startup identifier
    #         status_data: Status data including status, reason, updated_by
            
    #     Returns:
    #         True if successful
    #     """
    #     try:
    #         status_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
    #         # Update startup document
    #         self.db.collection('startups').document(startup_id).update(status_data)
            
    #         # Create activity log
    #         self.create_activity(
    #             startup_id=startup_id,
    #             user_id=status_data.get('updated_by', 'system'),
    #             action='status_updated',
    #             description=f"Status updated to {status_data['status']}: {status_data.get('reason', '')}",
    #             metadata={
    #                 'new_status': status_data['status'],
    #                 'reason': status_data.get('reason'),
    #                 'source': status_data.get('source', 'manual')
    #             }
    #         )
            
    #         logger.info(f"Updated status for startup {startup_id} to {status_data['status']}")
    #         return True
            
    #     except Exception as e:
    #         logger.error(f"Error updating startup status: {e}")
    #         raise


# Global instance
fs_client = FirestoreClient()
