"""Reanalysis routes for Project Younicorn API."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from ..models.requests import ReanalysisRequest
from ..utils import get_current_user_from_token
from ..services.reanalysis_service import reanalysis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/startups", tags=["reanalysis"])


@router.post("/{startup_id}/reanalyze")
async def trigger_reanalysis(
    startup_id: str,
    request: ReanalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Trigger reanalysis for a startup with investor notes.
    Only investors can trigger reanalysis.
    
    Args:
        startup_id: Unique identifier for the startup
        request: ReanalysisRequest containing investor_notes
        current_user: Current authenticated user
    
    Returns:
        Dictionary with analysis_id, message, and status
    """
    try:
        # Check if user is an investor
        if current_user.get('role') != 'investor':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only investors can trigger reanalysis"
            )
        
        # Trigger reanalysis
        result = await reanalysis_service.trigger_reanalysis(
            startup_id=startup_id,
            investor_notes=request.investor_notes,
            investor_id=current_user.get('uid') or current_user.get('id')
        )
        
        logger.info(f"Reanalysis triggered for startup {startup_id} by investor {current_user.get('uid')}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering reanalysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger reanalysis: {str(e)}"
        )
