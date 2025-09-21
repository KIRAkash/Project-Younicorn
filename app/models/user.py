# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""User and team-related data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    """User role enumeration."""
    FOUNDER = "founder"
    INVESTOR = "investor"
    ANALYST = "analyst"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class User(BaseModel):
    """User model."""
    id: UUID = Field(default_factory=uuid4, description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User's full name")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(default=UserStatus.PENDING, description="User status")
    
    # Profile information
    company: Optional[str] = Field(None, description="Company/organization")
    title: Optional[str] = Field(None, description="Job title")
    bio: Optional[str] = Field(None, description="User biography")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    
    # Authentication
    hashed_password: str = Field(..., description="Hashed password")
    is_verified: bool = Field(default=False, description="Email verification status")
    verification_token: Optional[str] = Field(None, description="Email verification token")
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Account creation timestamp"
    )
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    
    # Preferences
    email_notifications: bool = Field(default=True, description="Email notifications enabled")
    timezone: str = Field(default="UTC", description="User timezone")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class TeamRole(str, Enum):
    """Team role enumeration."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamMember(BaseModel):
    """Team member model."""
    user_id: UUID = Field(..., description="User ID")
    team_id: UUID = Field(..., description="Team ID")
    role: TeamRole = Field(..., description="Team role")
    joined_at: datetime = Field(
        default_factory=datetime.utcnow, description="Join timestamp"
    )
    invited_by: Optional[UUID] = Field(None, description="User who invited this member")
    
    # Permissions
    can_invite_members: bool = Field(default=False, description="Can invite new members")
    can_manage_analyses: bool = Field(default=True, description="Can manage analyses")
    can_export_data: bool = Field(default=False, description="Can export data")


class Team(BaseModel):
    """Team/organization model."""
    id: UUID = Field(default_factory=uuid4, description="Team ID")
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    
    # Team settings
    max_members: int = Field(default=10, description="Maximum team members")
    subscription_tier: str = Field(default="basic", description="Subscription tier")
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Team creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    
    # Members (populated separately)
    members: List[TeamMember] = Field(
        default_factory=list, description="Team members"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User's full name")
    password: str = Field(..., min_length=8, description="User password")
    role: UserRole = Field(..., description="User role")
    company: Optional[str] = Field(None, description="Company/organization")
    title: Optional[str] = Field(None, description="Job title")


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = Field(None, description="User's full name")
    company: Optional[str] = Field(None, description="Company/organization")
    title: Optional[str] = Field(None, description="Job title")
    bio: Optional[str] = Field(None, description="User biography")
    email_notifications: Optional[bool] = Field(None, description="Email notifications")
    timezone: Optional[str] = Field(None, description="User timezone")


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Authentication token model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: UUID = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
