"""Image upload routes for Project Younicorn API."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from pydantic import BaseModel

from ..utils import get_current_user_from_token
from ..services import gcs_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/images", tags=["images"])


class ImageUploadResponse(BaseModel):
    """Image upload response model."""
    gcs_path: str
    signed_url: str
    message: str


@router.post("/upload/profile-icon")
async def upload_profile_icon(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> ImageUploadResponse:
    """Upload profile icon (2MB max, jpg/png/webp).
    
    Security:
    - Requires Firebase authentication
    - Max 2MB file size
    - Only jpg, png, webp formats
    - Generates time-limited signed URL (7 days)
    """
    if not gcs_storage.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available"
        )
    
    try:
        # Read file content
        image_content = await file.read()
        
        # Validate file size (2MB limit)
        if len(image_content) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile icon must be less than 2MB"
            )
        
        # Upload to GCS
        user_id = current_user.get('uid') or current_user.get('id')
        gcs_path = gcs_storage.upload_profile_icon(user_id, image_content)
        
        if not gcs_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload image. Please check file format (jpg, png, webp)"
            )
        
        # Generate signed URL (valid for 7 days)
        signed_url = gcs_storage.get_signed_url(gcs_path, expiration_minutes=7*24*60)
        
        if not signed_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access URL"
            )
        
        logger.info(f"Profile icon uploaded for user {user_id}: {gcs_path}")
        
        return ImageUploadResponse(
            gcs_path=gcs_path,
            signed_url=signed_url,
            message="Profile icon uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile icon: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile icon: {str(e)}"
        )


@router.post("/upload/startup-logo")
async def upload_startup_logo(
    startup_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> ImageUploadResponse:
    """Upload startup logo (5MB max, jpg/png/webp/svg).
    
    Security:
    - Requires Firebase authentication
    - Max 5MB file size
    - jpg, png, webp, svg formats
    - Generates time-limited signed URL (7 days)
    """
    if not gcs_storage.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available"
        )
    
    try:
        # Read file content
        image_content = await file.read()
        
        # Validate file size (5MB limit)
        if len(image_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Startup logo must be less than 5MB"
            )
        
        # Upload to GCS
        gcs_path = gcs_storage.upload_startup_logo(startup_id, image_content)
        
        if not gcs_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload logo. Please check file format"
            )
        
        # Generate signed URL (valid for 7 days)
        signed_url = gcs_storage.get_signed_url(gcs_path, expiration_minutes=7*24*60)
        
        if not signed_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate access URL"
            )
        
        logger.info(f"Startup logo uploaded for startup {startup_id}: {gcs_path}")
        
        return ImageUploadResponse(
            gcs_path=gcs_path,
            signed_url=signed_url,
            message="Startup logo uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading startup logo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload startup logo: {str(e)}"
        )


@router.get("/signed-url")
async def get_signed_url(
    gcs_path: str,
    expiration_minutes: int = 60,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Dict[str, str]:
    """Get signed URL for image.
    
    Security:
    - Requires Firebase authentication
    - Generates time-limited URL
    """
    if not gcs_storage.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not available"
        )
    
    try:
        # Generate signed URL
        signed_url = gcs_storage.get_signed_url(gcs_path, expiration_minutes)
        
        if not signed_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found or failed to generate URL"
            )
        
        return {
            "signed_url": signed_url,
            "gcs_path": gcs_path,
            "expires_in_minutes": expiration_minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signed URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate signed URL: {str(e)}"
        )
