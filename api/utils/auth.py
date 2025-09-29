"""Authentication utilities for Project Minerva API."""

from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, status
from ..config import settings

async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Mock function to get current user - in real app would decode JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        # Handle both "Bearer token" and just "token" formats
        if " " in authorization:
            token_type, token = authorization.split(" ", 1)
            if token_type.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
        else:
            # Direct token without "Bearer" prefix
            token = authorization
        
        # Mock token validation - in production, decode and validate JWT
        if token == "investor-token":
            return {
                "id": "investor-001",
                "email": "investor@demo.com",
                "name": "Demo Investor", 
                "role": "investor"
            }
        elif token == "founder-token":
            return {
                "id": "founder-001",
                "email": "founder@demo.com",
                "name": "Demo Founder",
                "role": "founder"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
