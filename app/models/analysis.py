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

"""Analysis-related data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent type enumeration."""
    ORCHESTRATOR = "orchestrator"
    TEAM = "team"
    MARKET = "market"
    PRODUCT = "product"
    COMPETITION = "competition"
    SYNTHESIS = "synthesis"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OpportunityLevel(str, Enum):
    """Opportunity level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCEPTIONAL = "exceptional"


class SourceCitation(BaseModel):
    """Source citation model for traceability."""
    id: str = Field(..., description="Citation ID")
    title: str = Field(..., description="Source title")
    url: Optional[HttpUrl] = Field(None, description="Source URL")
    domain: Optional[str] = Field(None, description="Source domain")
    document_name: Optional[str] = Field(None, description="Document name if internal")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt")
    confidence_score: Optional[float] = Field(
        None, description="Confidence score (0-1)"
    )


class AgentTrace(BaseModel):
    """Agent execution trace for transparency."""
    step_number: int = Field(..., description="Step number in execution")
    action: str = Field(..., description="Action taken")
    reasoning: Optional[str] = Field(None, description="Agent's reasoning")
    tool_used: Optional[str] = Field(None, description="Tool used if any")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Step timestamp"
    )
    duration_seconds: Optional[float] = Field(None, description="Step duration")


class AgentAnalysis(BaseModel):
    """Individual agent analysis result."""
    agent_type: AgentType = Field(..., description="Type of agent")
    score: float = Field(..., ge=1, le=10, description="Analysis score (1-10)")
    summary: str = Field(..., description="Executive summary")
    detailed_analysis: str = Field(..., description="Detailed analysis")
    key_findings: List[str] = Field(..., description="Key findings")
    supporting_evidence: List[str] = Field(..., description="Supporting evidence")
    sources: List[SourceCitation] = Field(
        default_factory=list, description="Source citations"
    )
    confidence_level: float = Field(
        ..., ge=0, le=1, description="Confidence in analysis (0-1)"
    )
    
    # Agent execution details
    execution_trace: List[AgentTrace] = Field(
        default_factory=list, description="Agent execution trace"
    )
    started_at: datetime = Field(
        default_factory=datetime.utcnow, description="Analysis start time"
    )
    completed_at: Optional[datetime] = Field(None, description="Analysis completion time")
    duration_seconds: Optional[float] = Field(None, description="Total duration")


class RiskOpportunity(BaseModel):
    """Risk or opportunity identification."""
    type: str = Field(..., description="Type: 'risk' or 'opportunity'")
    level: str = Field(..., description="Risk/opportunity level")
    title: str = Field(..., description="Brief title")
    description: str = Field(..., description="Detailed description")
    impact: str = Field(..., description="Potential impact")
    mitigation: Optional[str] = Field(None, description="Mitigation strategy for risks")
    sources: List[SourceCitation] = Field(
        default_factory=list, description="Supporting sources"
    )


class InvestabilityScore(BaseModel):
    """Overall investability scoring."""
    overall_score: float = Field(..., ge=1, le=10, description="Overall score (1-10)")
    team_score: float = Field(..., ge=1, le=10, description="Team score")
    market_score: float = Field(..., ge=1, le=10, description="Market score")
    product_score: float = Field(..., ge=1, le=10, description="Product score")
    competition_score: float = Field(..., ge=1, le=10, description="Competition score")
    
    # Weighted components
    score_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "team": 0.25,
            "market": 0.25,
            "product": 0.30,
            "competition": 0.20,
        },
        description="Score component weights"
    )
    
    # Qualitative assessment
    investment_recommendation: str = Field(
        ..., description="Investment recommendation (Strong Buy, Buy, Hold, Pass)"
    )
    confidence_level: float = Field(
        ..., ge=0, le=1, description="Confidence in recommendation"
    )


class AnalysisRequest(BaseModel):
    """Analysis request model."""
    id: UUID = Field(default_factory=uuid4, description="Request ID")
    startup_id: UUID = Field(..., description="Startup submission ID")
    requested_by: UUID = Field(..., description="User ID who requested analysis")
    priority: str = Field(default="normal", description="Analysis priority")
    requested_at: datetime = Field(
        default_factory=datetime.utcnow, description="Request timestamp"
    )
    special_instructions: Optional[str] = Field(
        None, description="Special analysis instructions"
    )


class AnalysisResult(BaseModel):
    """Complete analysis result model."""
    id: UUID = Field(default_factory=uuid4, description="Analysis ID")
    startup_id: UUID = Field(..., description="Startup submission ID")
    request_id: UUID = Field(..., description="Analysis request ID")
    
    # Analysis components
    agent_analyses: Dict[AgentType, AgentAnalysis] = Field(
        default_factory=dict, description="Individual agent analyses"
    )
    investability_score: Optional[InvestabilityScore] = Field(
        None, description="Overall investability scoring"
    )
    risks_opportunities: List[RiskOpportunity] = Field(
        default_factory=list, description="Identified risks and opportunities"
    )
    
    # Executive summary
    executive_summary: Optional[str] = Field(None, description="Executive summary")
    investment_memo: Optional[str] = Field(None, description="Full investment memo")
    key_insights: List[str] = Field(
        default_factory=list, description="Key insights"
    )
    
    # Analysis metadata
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING, description="Status")
    started_at: Optional[datetime] = Field(None, description="Analysis start time")
    completed_at: Optional[datetime] = Field(None, description="Analysis completion time")
    total_duration_seconds: Optional[float] = Field(None, description="Total duration")
    
    # Quality metrics
    overall_confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Overall confidence in analysis"
    )
    data_completeness: Optional[float] = Field(
        None, ge=0, le=1, description="Data completeness score"
    )
    
    # Versioning and updates
    version: int = Field(default=1, description="Analysis version")
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    updated_by: Optional[UUID] = Field(None, description="User who last updated")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
