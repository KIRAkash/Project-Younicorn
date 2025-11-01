"""
Firebase Authentication routes for Project Younicorn API.

Provides endpoints for user registration, role management, and user info using Firebase Auth.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr

from ..utils.firebase_auth import (
    create_user_with_role,
    set_user_role,
    get_user_role,
    get_current_user,
    require_investor,
    UserRole
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/firebase-auth", tags=["firebase-authentication"])


class FirebaseRegisterRequest(BaseModel):
    """Firebase user registration request."""
    email: EmailStr
    password: str
    role: str
    display_name: str | None = None


class SetRoleRequest(BaseModel):
    """Set user role request."""
    uid: str
    role: str


@router.post("/register")
async def register(request: FirebaseRegisterRequest) -> Dict[str, Any]:
    """
    Register a new user with email/password and role.
    
    Request body:
    - email: User email
    - password: User password
    - role: User role ('investor' or 'founder')
    - display_name: Optional display name
    """
    try:
        # Validate role
        if request.role not in [UserRole.INVESTOR, UserRole.FOUNDER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid role. Must be "{UserRole.INVESTOR}" or "{UserRole.FOUNDER}"'
            )
        
        # Create user
        uid = create_user_with_role(
            email=request.email,
            password=request.password,
            role=request.role,
            display_name=request.display_name
        )
        
        if uid:
            return {
                'success': True,
                'uid': uid,
                'email': request.email,
                'role': request.role,
                'message': 'User created successfully'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to create user'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Requires: Authorization header with Firebase ID token
    """
    return {
        'uid': current_user['uid'],
        'email': current_user['email'],
        'role': current_user['role']
    }


@router.post("/set-role")
async def set_role(
    request: SetRoleRequest,
    current_user: Dict[str, Any] = Depends(require_investor)
) -> Dict[str, Any]:
    """
    Set role for a user (investor only).
    
    Request body:
    - uid: User ID
    - role: User role ('investor' or 'founder')
    
    Requires: Authorization header with Firebase ID token (investor role)
    """
    try:
        # Validate role
        if request.role not in [UserRole.INVESTOR, UserRole.FOUNDER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid role. Must be "{UserRole.INVESTOR}" or "{UserRole.FOUNDER}"'
            )
        
        success = set_user_role(request.uid, request.role)
        
        if success:
            return {
                'success': True,
                'uid': request.uid,
                'role': request.role,
                'message': 'Role updated successfully'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to update role'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set role error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/get-role/{uid}")
async def get_role(
    uid: str,
    current_user: Dict[str, Any] = Depends(require_investor)
) -> Dict[str, Any]:
    """
    Get role for a user (investor only).
    
    Requires: Authorization header with Firebase ID token (investor role)
    """
    try:
        role = get_user_role(uid)
        
        if role:
            return {
                'uid': uid,
                'role': role
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found or role not set'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get role error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return user info.
    
    Requires: Authorization header with Firebase ID token
    """
    return {
        'valid': True,
        'uid': current_user['uid'],
        'email': current_user['email'],
        'role': current_user['role']
    }
