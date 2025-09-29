"""Request models for Project Minerva API."""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class LoginRequest(BaseModel):
    """User login request model."""
    email: str
    password: str

class StartupSubmissionRequest(BaseModel):
    """Startup submission request model."""
    company_info: Dict[str, Any]
    founders: List[Dict[str, Any]]
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserRegistrationRequest(BaseModel):
    """User registration request model."""
    email: str
    password: str
    name: str
    role: str = "founder"  # founder or investor
