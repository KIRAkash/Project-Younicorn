"""Authentication routes for Project Minerva API."""

import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from ..models import LoginRequest, UserRegistrationRequest, LoginResponse, UserResponse
from ..utils import get_current_user_from_token
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest) -> LoginResponse:
    """Login endpoint."""
    # Check demo credentials
    user_data = settings.demo_users.get(credentials.email)
    
    if user_data and user_data["password"] == credentials.password:
        # Generate mock token based on role
        token = f"{user_data['role']}-token"
        
        user_response = UserResponse(
            id=user_data["id"],
            email=credentials.email,
            name=user_data["name"],
            role=user_data["role"]
        )
        
        return LoginResponse(token=token, user=user_response)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/register")
async def register(user_data: UserRegistrationRequest) -> Dict[str, Any]:
    """Register endpoint."""
    return {"message": "Registration successful", "user_id": str(uuid.uuid4())}

@router.post("/logout")
async def logout() -> Dict[str, Any]:
    """Logout endpoint."""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> UserResponse:
    """Get current user endpoint."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"]
    )
