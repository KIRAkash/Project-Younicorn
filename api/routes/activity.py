"""
Activity Feed API routes.
Handles activity stream for startups and users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from api.models.responses import ActivityResponse
from api.services import fs_client
from api.utils.firebase_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/startup/{startup_id}", response_model=List[ActivityResponse])
async def get_startup_activity(
    startup_id: str,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get activity feed for a specific startup.
    
    Args:
        startup_id: Startup ID
        limit: Maximum number of activities to return (default 50)
    """
    try:
        activities = fs_client.get_activity_by_startup(
            startup_id=startup_id,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(activities)} activities for startup {startup_id}")
        return activities
        
    except Exception as e:
        logger.error(f"Error getting startup activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get startup activity: {str(e)}"
        )


@router.get("/me", response_model=List[ActivityResponse])
async def get_my_activity(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get activity feed for the current user.
    Shows all activities performed by the user.
    
    Args:
        limit: Maximum number of activities to return (default 50)
    """
    try:
        activities = fs_client.get_activity_by_user(
            user_id=current_user['uid'],
            limit=limit
        )
        
        logger.info(f"Retrieved {len(activities)} activities for user {current_user['uid']}")
        return activities
        
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity: {str(e)}"
        )
