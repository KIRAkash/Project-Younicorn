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

"""Synthesis agent for compiling final investment memo and recommendations."""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Literal
import datetime
from .config import config, prompts
from .callbacks import (
    track_agent_execution_callback,
    update_analysis_progress_callback,
)


class FounderQuestion(BaseModel):
    """Structured question for founders."""
    
    question_text: str = Field(..., description="The question text to ask the founder")
    category: Literal["team", "market", "product", "financials", "business_model"] = Field(..., description="Category of the question")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority level of the question")


class InvestmentRecommendation(BaseModel):
    """Investment recommendation model."""
    
    recommendation: str = Field(..., description="Investment recommendation: Strong Buy, Buy, Hold, Pass")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in recommendation (0-1)")
    rationale: str = Field(..., description="Detailed rationale for the recommendation")
    
    # Investment terms suggestions
    suggested_valuation_range: str = Field(..., description="Suggested valuation range")
    investment_size_recommendation: str = Field(..., description="Recommended investment size")
    key_terms: list[str] = Field(default=[], description="Key investment terms to negotiate")
    
    # Conditions and requirements
    investment_conditions: list[str] = Field(default=[], description="Conditions for investment")
    due_diligence_requirements: list[str] = Field(default=[], description="Additional due diligence needed")


class RiskAssessment(BaseModel):
    """Risk assessment model."""
    
    
    overall_risk_level: str = Field(..., description="Overall risk level: Low, Medium, High, Critical")
    
    # Risk categories
    team_risks: list[str] = Field(default=[], description="Team-related risks")
    market_risks: list[str] = Field(default=[], description="Market-related risks")
    product_risks: list[str] = Field(default=[], description="Product-related risks")
    competitive_risks: list[str] = Field(default=[], description="Competitive risks")
    execution_risks: list[str] = Field(default=[], description="Execution risks")
    
    # Risk mitigation
    mitigation_strategies: list[str] = Field(default=[], description="Risk mitigation strategies")
    monitoring_requirements: list[str] = Field(default=[], description="Key metrics to monitor")


class OpportunityAssessment(BaseModel):
    """Opportunity assessment model."""
    
    overall_opportunity_level: str = Field(..., description="Overall opportunity level: Low, Medium, High, Exceptional")
    
    # Opportunity categories
    market_opportunities: list[str] = Field(default=[], description="Market opportunities")
    product_opportunities: list[str] = Field(default=[], description="Product development opportunities")
    expansion_opportunities: list[str] = Field(default=[], description="Market expansion opportunities")
    strategic_opportunities: list[str] = Field(default=[], description="Strategic partnership opportunities")
    
    # Value creation potential
    value_creation_drivers: list[str] = Field(default=[], description="Key value creation drivers")
    exit_scenarios: list[str] = Field(default=[], description="Potential exit scenarios")


class SynthesisResult(BaseModel):
    """Model for synthesis agent results."""
    
    # Overall scoring
    overall_investability_score: float = Field(..., ge=1, le=10, description="Overall investability score (1-10)")
    
    # Component scores (from specialist agents)
    team_score: float = Field(..., ge=1, le=10, description="Team analysis score")
    market_score: float = Field(..., ge=1, le=10, description="Market analysis score")
    product_score: float = Field(..., ge=1, le=10, description="Product analysis score")
    competition_score: float = Field(..., ge=1, le=10, description="Competition analysis score")
    
    # Executive summary
    executive_summary: str = Field(..., description="Executive summary for investors")
    investment_thesis: str = Field(..., description="Clear investment thesis")
    
    # Detailed analysis
    investment_memo: str = Field(..., description="Complete investment memorandum")
    key_insights: list[str] = Field(default=[], description="Key insights from the analysis")
    
    # Investment recommendation
    investment_recommendation: InvestmentRecommendation = Field(..., description="Investment recommendation")
    
    # Risk and opportunity assessment
    risk_assessment: RiskAssessment = Field(..., description="Comprehensive risk assessment")
    opportunity_assessment: OpportunityAssessment = Field(..., description="Opportunity assessment")
    
    # Comparative analysis
    comparable_companies: list[str] = Field(default=[], description="Comparable companies for benchmarking")
    competitive_positioning: str = Field(..., description="Competitive positioning summary")
    
    # Next steps
    next_steps: list[str] = Field(default=[], description="Recommended next steps")
    timeline: str = Field(..., description="Suggested timeline for decision making")
    
    # Quality metrics
    analysis_completeness: float = Field(..., ge=0, le=1, description="Analysis completeness score (0-1)")
    data_quality: float = Field(..., ge=0, le=1, description="Overall data quality score (0-1)")
    confidence_level: float = Field(..., ge=0, le=1, description="Overall confidence in analysis (0-1)")
    
    # Questions for founders
    questions: list[FounderQuestion] = Field(default=[], description="5-10 unique and most relevant questions for founders, synthesized from individual agent questions")


synthesis_agent = LlmAgent(
    model=config.synthesis_model,
    name="synthesis_agent",
    description="Synthesizes specialist analysis into final investment recommendations",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    {prompts.synthesis_agent_prompt}
    """,
    output_schema=SynthesisResult,
    output_key="synthesis_result",
    after_agent_callback=[
        track_agent_execution_callback,
        update_analysis_progress_callback
    ],
)
