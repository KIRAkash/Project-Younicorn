"""Authentication utilities for Project Younicorn API."""

from typing import Dict, Any
from fastapi import Depends
from .firebase_auth import get_current_user

# Re-export Firebase auth function for backward compatibility
async def get_current_user_from_token(user_data: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated user using Firebase authentication.
    This function now delegates to Firebase auth for real authentication.
    """
    return user_data
