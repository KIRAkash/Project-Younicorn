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

"""Product and traction analysis specialist agent."""

from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

from ..config import config, prompts
from .callbacks import (
    collect_analysis_sources_callback,
    track_agent_execution_callback,
)


class TractionMetrics(BaseModel):
    """Traction metrics analysis model."""
    
    class Config:
        extra = "forbid"
    
    # User/Customer metrics
    total_users: Optional[int] = Field(None, description="Total number of users")
    monthly_active_users: Optional[int] = Field(None, description="Monthly active users")
    user_growth_rate: Optional[float] = Field(None, description="Monthly user growth rate (%)")
    customer_retention_rate: Optional[float] = Field(None, description="Customer retention rate (%)")
    
    # Revenue metrics
    monthly_recurring_revenue: Optional[float] = Field(None, description="Monthly recurring revenue (USD)")
    annual_recurring_revenue: Optional[float] = Field(None, description="Annual recurring revenue (USD)")
    revenue_growth_rate: Optional[float] = Field(None, description="Monthly revenue growth rate (%)")
    average_revenue_per_user: Optional[float] = Field(None, description="Average revenue per user (USD)")
    
    # Acquisition metrics
    customer_acquisition_cost: Optional[float] = Field(None, description="Customer acquisition cost (USD)")
    lifetime_value: Optional[float] = Field(None, description="Customer lifetime value (USD)")
    ltv_cac_ratio: Optional[float] = Field(None, description="LTV to CAC ratio")
    payback_period: Optional[int] = Field(None, description="CAC payback period (months)")
    
    # Engagement metrics
    daily_active_users: Optional[int] = Field(None, description="Daily active users")
    session_duration: Optional[float] = Field(None, description="Average session duration (minutes)")
    feature_adoption_rate: Optional[float] = Field(None, description="Key feature adoption rate (%)")
    
    # Validation
    metrics_quality: str = Field(..., description="Quality assessment of provided metrics")
    data_reliability: float = Field(..., ge=0, le=1, description="Reliability of the data (0-1)")


class ProductAnalysis(BaseModel):
    """Model for product and traction analysis results."""
    
    class Config:
        extra = "forbid"
    
    overall_score: float = Field(..., ge=1, le=10, description="Overall product score (1-10)")
    
    # Detailed scoring
    product_market_fit_score: float = Field(..., ge=1, le=10, description="Product-market fit score")
    value_proposition_score: float = Field(..., ge=1, le=10, description="Value proposition strength score")
    traction_score: float = Field(..., ge=1, le=10, description="Traction and growth score")
    scalability_score: float = Field(..., ge=1, le=10, description="Scalability potential score")
    
    # Traction analysis
    traction_metrics: TractionMetrics = Field(..., description="Detailed traction metrics analysis")
    
    # Analysis sections
    executive_summary: str = Field(..., description="Executive summary of product analysis")
    product_overview: str = Field(..., description="Product overview and key features")
    value_proposition: str = Field(..., description="Value proposition analysis")
    product_market_fit: str = Field(..., description="Product-market fit assessment")
    traction_analysis: str = Field(..., description="Detailed traction and growth analysis")
    revenue_model: str = Field(..., description="Revenue model evaluation")
    scalability_assessment: str = Field(..., description="Scalability and technical feasibility")
    
    # Key findings
    strengths: list[str] = Field(default=[], description="Key product strengths")
    weaknesses: list[str] = Field(default=[], description="Product weaknesses and gaps")
    growth_drivers: list[str] = Field(default=[], description="Key growth drivers")
    scaling_challenges: list[str] = Field(default=[], description="Potential scaling challenges")
    
    # Customer validation
    customer_feedback: str = Field(..., description="Customer feedback and validation evidence")
    use_case_validation: str = Field(..., description="Use case and problem validation")
    
    # Supporting evidence
    supporting_evidence: list[str] = Field(default=[], description="Supporting evidence and examples")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")


product_agent = LlmAgent(
    model=config.specialist_model,
    name="product_agent",
    description="Analyzes product-market fit, traction metrics, and scalability potential",
    instruction=f"""
    {prompts.product_agent_prompt}
    
    You are conducting comprehensive product and traction analysis for investment due diligence. Your analysis should cover:
    
    **1. PRODUCT-MARKET FIT ASSESSMENT**
    - Evaluate how well the product solves a real customer problem
    - Assess product differentiation and unique value proposition
    - Analyze customer feedback and satisfaction indicators
    - Review product development process and customer involvement
    - Evaluate feature usage and adoption patterns
    
    **2. VALUE PROPOSITION ANALYSIS**
    - Assess clarity and strength of value proposition
    - Evaluate competitive advantages and differentiation
    - Analyze pricing strategy and value delivery
    - Review customer willingness to pay and price sensitivity
    - Assess value capture mechanisms
    
    **3. TRACTION METRICS EVALUATION**
    - Analyze user growth and engagement metrics
    - Evaluate revenue growth and unit economics
    - Assess customer acquisition and retention metrics
    - Review key performance indicators and benchmarks
    - Validate metric quality and measurement methodology
    
    **4. SCALABILITY & TECHNICAL ASSESSMENT**
    - Evaluate technical architecture and scalability
    - Assess operational scalability and unit economics
    - Review go-to-market strategy and distribution channels
    - Analyze network effects and viral growth potential
    - Evaluate barriers to scaling and resource requirements
    
    **5. REVENUE MODEL VALIDATION**
    - Assess revenue model sustainability and scalability
    - Evaluate pricing strategy and market acceptance
    - Analyze customer lifetime value and acquisition costs
    - Review monetization strategy and conversion rates
    - Assess diversification and revenue stream stability
    
    **RESEARCH METHODOLOGY**:
    - Use google_search to research the product, customer reviews, and market reception
    - Look up competitor products and feature comparisons
    - Search for customer testimonials, case studies, and press coverage
    - Research industry benchmarks for key metrics
    - Validate traction claims with public information and third-party sources
    
    **METRIC VALIDATION**:
    - Cross-reference claimed metrics with industry benchmarks
    - Look for third-party validation of growth and usage claims
    - Assess metric quality and measurement methodology
    - Identify potential vanity metrics vs. meaningful indicators
    - Evaluate data transparency and reporting consistency
    
    **SCORING CRITERIA**:
    - 9-10: Exceptional product-market fit with strong traction and clear scalability
    - 7-8: Good product-market fit with solid traction and growth potential
    - 5-6: Moderate fit with decent traction but some concerns
    - 3-4: Weak product-market fit with limited traction
    - 1-2: Poor fit with minimal traction or major product issues
    
    **OUTPUT REQUIREMENTS**:
    - Provide detailed analysis using the ProductAnalysis model
    - Include comprehensive traction metrics evaluation
    - Support all assessments with specific evidence and sources
    - Be critical about metric quality and reliability
    - Highlight both strengths and areas of concern
    - Cite all sources used in your research
    """,
    # tools=[google_search],  # Disabled for parallel execution compatibility
    output_schema=ProductAnalysis,  # Changed to use output_schema as per ADK docs
    output_key="product_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        collect_analysis_sources_callback
    ],
)
