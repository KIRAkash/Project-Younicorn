"""Response models for Project Minerva API."""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    role: str

class LoginResponse(BaseModel):
    """Login response model."""
    token: str
    user: UserResponse

class StartupResponse(BaseModel):
    """Startup response model."""
    id: str
    company_info: Dict[str, Any]
    founders: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    submission_timestamp: datetime
    submitted_by: str
    status: str

class AnalysisResponse(BaseModel):
    """Analysis response model."""
    id: str
    startup_id: str
    status: str
    overall_score: Optional[float] = None
    team_score: Optional[float] = None
    market_score: Optional[float] = None
    product_score: Optional[float] = None
    competition_score: Optional[float] = None
    investment_recommendation: Optional[str] = None
    confidence_level: Optional[float] = None
    executive_summary: Optional[str] = None
    investment_memo: Optional[str] = None
    agent_analyses: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response model."""
    total_startups: int
    total_analyses: int
    pending_analyses: int
    completed_analyses: int
    average_score: float
    recent_activity: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
