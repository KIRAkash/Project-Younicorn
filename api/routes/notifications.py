"""
Notifications API routes.
Handles real-time notifications for users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from api.models.responses import NotificationResponse
from api.services import fs_client
from api.utils.firebase_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get notifications for the current user.
    
    Args:
        unread_only: If True, only return unread notifications
        limit: Maximum number of notifications to return (default 50)
    """
    try:
        notifications = fs_client.get_notifications(
            user_id=current_user['uid'],
            unread_only=unread_only,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(notifications)} notifications for user {current_user['uid']}")
        return notifications
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )


@router.get("/unread/count")
async def get_unread_count(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get count of unread notifications for the current user."""
    try:
        count = fs_client.get_unread_count(current_user['uid'])
        
        return {"count": count}
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a notification as read."""
    try:
        # Get notification to verify ownership
        notification = fs_client.db.collection('notifications').document(notification_id).get()
        
        if not notification.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {notification_id} not found"
            )
        
        notification_data = notification.to_dict()
        
        # Verify user owns this notification
        if notification_data.get('user_id') != current_user['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark your own notifications as read"
            )
        
        # Mark as read
        fs_client.mark_notification_read(notification_id)
        
        logger.info(f"Notification {notification_id} marked as read")
        return {"success": True, "message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark all notifications as read for the current user."""
    try:
        count = fs_client.mark_all_notifications_read(current_user['uid'])
        
        logger.info(f"Marked {count} notifications as read for user {current_user['uid']}")
        return {"success": True, "count": count, "message": f"Marked {count} notifications as read"}
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a notification."""
    try:
        # Get notification to verify ownership
        notification = fs_client.db.collection('notifications').document(notification_id).get()
        
        if not notification.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {notification_id} not found"
            )
        
        notification_data = notification.to_dict()
        
        # Verify user owns this notification
        if notification_data.get('user_id') != current_user['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own notifications"
            )
        
        # Delete notification
        fs_client.db.collection('notifications').document(notification_id).delete()
        
        logger.info(f"Notification {notification_id} deleted")
        return {"success": True, "message": "Notification deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )
