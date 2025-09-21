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

"""Startup-related data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class FundingStage(str, Enum):
    """Funding stage enumeration."""
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    LATER_STAGE = "later_stage"


class Industry(str, Enum):
    """Industry enumeration."""
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    EDTECH = "edtech"
    ENTERPRISE_SOFTWARE = "enterprise_software"
    CONSUMER_APPS = "consumer_apps"
    ECOMMERCE = "ecommerce"
    AI_ML = "ai_ml"
    BLOCKCHAIN = "blockchain"
    CYBERSECURITY = "cybersecurity"
    CLIMATE_TECH = "climate_tech"
    BIOTECH = "biotech"
    HARDWARE = "hardware"
    OTHER = "other"


class DocumentType(str, Enum):
    """Document type enumeration."""
    PITCH_DECK = "pitch_deck"
    BUSINESS_PLAN = "business_plan"
    FINANCIAL_MODEL = "financial_model"
    PRODUCT_DEMO = "product_demo"
    MARKET_RESEARCH = "market_research"
    TEAM_BIOS = "team_bios"
    LEGAL_DOCS = "legal_docs"
    OTHER = "other"


class StartupStatus(str, Enum):
    """Startup status enumeration."""
    SUBMITTED = "submitted"
    ANALYZING = "analyzing"
    COMPLETED = "completed"


class FounderInfo(BaseModel):
    """Founder information model."""
    name: str = Field(..., description="Founder's full name")
    email: str = Field(..., description="Founder's email address")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    role: str = Field(..., description="Role in the company (e.g., CEO, CTO)")
    bio: Optional[str] = Field(None, description="Brief biography")
    previous_experience: Optional[List[str]] = Field(
        default_factory=list, description="Previous work experience"
    )
    education: Optional[List[str]] = Field(
        default_factory=list, description="Educational background"
    )


class CompanyInfo(BaseModel):
    """Company information model."""
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Company description")
    website_url: Optional[HttpUrl] = Field(None, description="Company website")
    industry: Industry = Field(..., description="Primary industry")
    funding_stage: FundingStage = Field(..., description="Current funding stage")
    location: str = Field(..., description="Company location")
    founded_date: Optional[datetime] = Field(None, description="Company founding date")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    revenue_run_rate: Optional[float] = Field(
        None, description="Annual revenue run rate in USD"
    )
    funding_raised: Optional[float] = Field(
        None, description="Total funding raised in USD"
    )
    funding_seeking: Optional[float] = Field(
        None, description="Amount of funding seeking in USD"
    )


class StartupDocument(BaseModel):
    """Startup document model."""
    id: UUID = Field(default_factory=uuid4, description="Document ID")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Type of document")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    storage_path: str = Field(..., description="Storage path in cloud storage")
    upload_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Upload timestamp"
    )
    processed: bool = Field(default=False, description="Whether document is processed")
    extracted_text: Optional[str] = Field(
        None, description="Extracted text content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class StartupMetadata(BaseModel):
    """Additional startup metadata."""
    key_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Key business metrics"
    )
    competitive_advantages: List[str] = Field(
        default_factory=list, description="Claimed competitive advantages"
    )
    target_market: Optional[str] = Field(None, description="Target market description")
    business_model: Optional[str] = Field(None, description="Business model description")
    traction_highlights: List[str] = Field(
        default_factory=list, description="Key traction points"
    )
    use_of_funds: Optional[str] = Field(
        None, description="Planned use of funding"
    )
    exit_strategy: Optional[str] = Field(None, description="Exit strategy")


class StartupSubmission(BaseModel):
    """Main startup submission model."""
    id: UUID = Field(default_factory=uuid4, description="Submission ID")
    company_info: CompanyInfo = Field(..., description="Company information")
    founders: List[FounderInfo] = Field(..., description="Founder information")
    documents: List[StartupDocument] = Field(
        default_factory=list, description="Uploaded documents"
    )
    metadata: StartupMetadata = Field(
        default_factory=StartupMetadata, description="Additional metadata"
    )
    
    # Submission tracking
    submitted_by: UUID = Field(..., description="User ID who submitted")
    submission_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Submission timestamp"
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    
    # Analysis tracking
    analysis_requested: bool = Field(
        default=False, description="Whether analysis has been requested"
    )
    analysis_started: Optional[datetime] = Field(
        None, description="Analysis start timestamp"
    )
    analysis_completed: Optional[datetime] = Field(
        None, description="Analysis completion timestamp"
    )
    
    # Status
    status: str = Field(default="submitted", description="Submission status")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
