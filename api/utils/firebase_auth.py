"""
Firebase Authentication utilities for FastAPI.

This module provides authentication and authorization functionality using Firebase Auth.
Supports both email/password and Google OAuth authentication.
Implements role-based access control with two roles: 'investor' and 'founder'.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    # Check if already initialized
    firebase_admin.get_app()
    logger.info("Firebase Admin SDK already initialized")
except ValueError:
    # Initialize with default credentials or service account
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized with Application Default Credentials")
    except Exception as e:
        logger.warning(f"Could not initialize Firebase with default credentials: {e}")
        # Try to initialize with service account key if available
        key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if key_path and os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK initialized with service account: {key_path}")
        else:
            logger.warning("Firebase Admin SDK not initialized - auth will not work")


class UserRole:
    """User role constants."""
    INVESTOR = "investor"
    FOUNDER = "founder"


# HTTP Bearer token security
security = HTTPBearer()


async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify Firebase ID token from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials from request
        
    Returns:
        Decoded token with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Extract token from Bearer scheme
        id_token = credentials.credentials
        
        # Verify token with Firebase
        decoded_token = auth.verify_id_token(id_token)
        
        # Get user role from custom claims
        role = decoded_token.get('role')
        
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'role': role,
            'token': decoded_token
        }
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user(user_data: Dict[str, Any] = Depends(verify_firebase_token)) -> Dict[str, Any]:
    """
    Get current authenticated user.
    
    Args:
        user_data: Verified user data from token
        
    Returns:
        User information dict
    """
    return user_data


async def require_role(required_role: str, user_data: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Verify user has required role.
    
    Args:
        required_role: Required role (investor or founder)
        user_data: Current user data
        
    Returns:
        User data if authorized
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    user_role = user_data.get('role')
    
    if user_role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {required_role}, your role: {user_role}"
        )
    
    return user_data


async def require_investor(user_data: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require investor role."""
    return await require_role(UserRole.INVESTOR, user_data)


async def require_founder(user_data: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require founder role."""
    return await require_role(UserRole.FOUNDER, user_data)


def get_user_role(uid: str) -> Optional[str]:
    """
    Get user role from custom claims.
    
    Args:
        uid: Firebase user ID
        
    Returns:
        User role ('investor' or 'founder'), or None if not set
    """
    try:
        user = auth.get_user(uid)
        custom_claims = user.custom_claims or {}
        return custom_claims.get('role')
    except Exception as e:
        logger.error(f"Failed to get user role: {str(e)}")
        return None


def set_user_role(uid: str, role: str) -> bool:
    """
    Set user role in custom claims.
    
    Args:
        uid: Firebase user ID
        role: User role ('investor' or 'founder')
        
    Returns:
        True if successful, False otherwise
    """
    if role not in [UserRole.INVESTOR, UserRole.FOUNDER]:
        logger.error(f"Invalid role: {role}")
        return False
    
    try:
        auth.set_custom_user_claims(uid, {'role': role})
        logger.info(f"Set role '{role}' for user {uid}")
        return True
    except Exception as e:
        logger.error(f"Failed to set user role: {str(e)}")
        return False


def create_user_with_role(email: str, password: str, role: str, display_name: Optional[str] = None) -> Optional[str]:
    """
    Create a new user with specified role.
    
    Args:
        email: User email
        password: User password
        role: User role ('investor' or 'founder')
        display_name: Optional display name
        
    Returns:
        User ID if successful, None otherwise
    """
    if role not in [UserRole.INVESTOR, UserRole.FOUNDER]:
        logger.error(f"Invalid role: {role}")
        return None
    
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        
        # Set custom claims for role
        auth.set_custom_user_claims(user.uid, {'role': role})
        
        logger.info(f"Created user {user.uid} with role '{role}'")
        return user.uid
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        return None
