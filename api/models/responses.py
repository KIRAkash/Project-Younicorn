"""Response models for Project Younicorn API."""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    role: str
    profile_icon_url: Optional[str] = None  # Signed URL for profile icon

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

# ==================== Q&A Response Models ====================

class AnswerResponse(BaseModel):
    """Answer embedded in question response."""
    answered_by: str
    answered_by_name: str
    answer_text: str
    attachments: List[Dict[str, Any]] = []
    answered_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class QuestionResponse(BaseModel):
    """Question response model with embedded answer."""
    id: str
    startup_id: str
    asked_by: str
    asked_by_name: str
    asked_by_role: str
    question_text: str
    category: str
    priority: str
    status: str
    is_ai_generated: bool
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    answer: Optional[AnswerResponse] = None

class BulkAnswerResult(BaseModel):
    """Result for a single answer in bulk submission."""
    question_id: str
    success: bool
    error: Optional[str] = None
    question: Optional[QuestionResponse] = None


class BulkAnswerResponse(BaseModel):
    """Response for bulk answer submission."""
    total: int
    successful: int
    failed: int
    results: List[BulkAnswerResult]
    reanalysis_triggered: bool = False
    message: str


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: str
    user_id: str
    type: str
    title: str
    message: str
    related_id: str
    related_type: str
    read: bool
    created_at: datetime

class ActivityResponse(BaseModel):
    """Activity feed response model."""
    id: str
    startup_id: str
    user_id: str
    user_name: str
    activity_type: str
    description: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
