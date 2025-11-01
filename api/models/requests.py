"""Request models for Project Younicorn API."""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class SubmissionType(str, Enum):
    """Type of startup submission."""
    FORM = "form"
    VIDEO = "video"
    AUDIO = "audio"

class ProductStage(str, Enum):
    """Product development stage."""
    IDEA = "idea"
    PROTOTYPE = "prototype"
    MVP = "mvp"
    BETA = "beta"
    LIVE = "live"

class CompanyStructure(str, Enum):
    """Company legal structure."""
    PRIVATE_LIMITED = "private_limited"
    LLP = "llp"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    PUBLIC_LIMITED = "public_limited"
    OTHER = "other"

class LoginRequest(BaseModel):
    """User login request model."""
    email: str
    password: str

class DocumentUpload(BaseModel):
    """Document upload model with GCS support."""
    filename: str
    content_type: str
    data: str  # Base64 encoded file data
    size: Optional[int] = None
    gcs_path: Optional[str] = None  # GCS path after upload

class GCSFile(BaseModel):
    """GCS file reference model."""
    filename: str
    gcs_path: str
    content_type: str
    size: int
    file_type: str  # 'document', 'video', 'audio'

class AdvisorInfo(BaseModel):
    """Advisor information model."""
    name: str
    background: str
    expertise: str

class CompanyInfo(BaseModel):
    """Company information model with comprehensive fields."""
    # Basic Info
    name: str
    description: str
    website_url: Optional[str] = None
    logo_url: Optional[str] = None  # GCS path or signed URL for company logo
    industry: str
    funding_stage: str
    location: str
    founded_date: Optional[str] = None
    employee_count: Optional[int] = None
    
    # Product & Technology (Point 1)
    product_stage: ProductStage
    technology_stack: Optional[str] = None
    ip_patents: Optional[str] = None
    development_timeline: Optional[str] = None
    product_roadmap: Optional[str] = None
    
    # Market & Customer (Point 2)
    target_customer_profile: Optional[str] = None
    customer_acquisition_cost: Optional[float] = None  # INR
    lifetime_value: Optional[float] = None  # INR
    current_customer_count: Optional[int] = None
    customer_retention_rate: Optional[float] = None  # percentage
    geographic_markets: Optional[str] = None
    go_to_market_strategy: Optional[str] = None
    
    # Traction & Metrics (Point 3)
    monthly_recurring_revenue: Optional[float] = None  # INR
    annual_recurring_revenue: Optional[float] = None  # INR
    revenue_growth_rate: Optional[float] = None  # percentage
    user_growth_rate: Optional[float] = None  # percentage
    burn_rate: Optional[float] = None  # INR per month
    runway_months: Optional[int] = None
    key_performance_indicators: Optional[str] = None
    
    # Financial Details (Point 6)
    revenue_run_rate: Optional[float] = None  # INR
    funding_raised: Optional[float] = None  # INR
    funding_seeking: Optional[float] = None  # INR
    previous_funding_rounds: Optional[str] = None
    current_investors: Optional[str] = None
    use_of_funds: Optional[str] = None
    profitability_timeline: Optional[str] = None
    unit_economics: Optional[str] = None
    
    # Legal & Compliance (Point 8)
    company_structure: CompanyStructure
    incorporation_location: str
    regulatory_requirements: Optional[str] = None
    legal_issues: Optional[str] = None
    
    # Vision & Strategy (Point 9)
    mission_statement: Optional[str] = None
    five_year_vision: Optional[str] = None
    exit_strategy: Optional[str] = None
    social_impact: Optional[str] = None

class FounderInfo(BaseModel):
    """Founder information model."""
    name: str
    email: str
    linkedin_url: Optional[str] = None
    role: str
    bio: Optional[str] = None
    previous_experience: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    
    # Team & Advisors (Point 5)
    previous_exits: Optional[str] = None
    domain_expertise_years: Optional[int] = None
    key_achievements: Optional[str] = None

class StartupMetadata(BaseModel):
    """Startup metadata model."""
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    competitive_advantages: List[str] = Field(default_factory=list)
    traction_highlights: List[str] = Field(default_factory=list)
    
    # Team & Advisors (Point 5)
    advisory_board: Optional[List[AdvisorInfo]] = Field(default_factory=list)
    key_hires_planned: Optional[str] = None
    team_gaps: Optional[str] = None
    
    # Additional metadata
    main_competitors: Optional[List[str]] = Field(default_factory=list)
    market_size_tam: Optional[float] = None  # INR
    market_size_sam: Optional[float] = None  # INR
    market_size_som: Optional[float] = None  # INR
    unique_value_proposition: Optional[str] = None

class StartupSubmissionRequest(BaseModel):
    """Startup submission request model."""
    submission_type: SubmissionType = Field(default=SubmissionType.FORM)
    company_info: CompanyInfo
    founders: List[FounderInfo]
    documents: List[DocumentUpload] = Field(default_factory=list)
    metadata: StartupMetadata = Field(default_factory=StartupMetadata)
    gcs_files: List[GCSFile] = Field(default_factory=list)  # Files stored in GCS

class UserRegistrationRequest(BaseModel):
    """User registration request model."""
    email: str
    password: str
    name: str
    role: str = "founder"  # founder or investor

# ==================== Q&A Models ====================

class QuestionCategory(str, Enum):
    """Question category."""
    TEAM = "team"
    MARKET = "market"
    PRODUCT = "product"
    FINANCIALS = "financials"
    BUSINESS_MODEL = "business_model"

class QuestionPriority(str, Enum):
    """Question priority level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class QuestionRequest(BaseModel):
    """Request to create a new question."""
    startup_id: str
    question_text: str
    category: QuestionCategory
    priority: QuestionPriority = QuestionPriority.MEDIUM
    tags: List[str] = Field(default_factory=list)

class AnswerAttachment(BaseModel):
    """Attachment for an answer."""
    filename: str
    gcs_path: str
    size: int
    uploaded_at: Optional[str] = None

class AnswerRequest(BaseModel):
    """Request to answer a question."""
    answer_text: str
    attachments: List[AnswerAttachment] = Field(default_factory=list)

class QuestionUpdateRequest(BaseModel):
    """Request to update a question."""
    question_text: Optional[str] = None
    category: Optional[QuestionCategory] = None
    priority: Optional[QuestionPriority] = None
    tags: Optional[List[str]] = None


class ReanalysisRequest(BaseModel):
    """Request model for triggering reanalysis."""
    investor_notes: str = Field(
        ..., 
        description="Specific notes or focus areas for reanalysis",
        min_length=10,
        max_length=5000
    )


class BulkAnswerItem(BaseModel):
    """Single answer item in bulk submission."""
    question_id: str = Field(..., description="ID of the question being answered")
    answer_text: str = Field(..., description="Answer text")
    attachments: List[AnswerAttachment] = Field(default_factory=list, description="Optional attachments")


class BulkAnswerRequest(BaseModel):
    """Request to answer multiple questions at once."""
    answers: List[BulkAnswerItem] = Field(..., min_items=1, description="List of answers to submit")
