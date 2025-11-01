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
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field
import datetime
from .config import config, prompts
from .callbacks import (
    collect_analysis_sources_callback,
    track_agent_execution_callback,
)


class TractionMetrics(BaseModel):
    """Traction metrics analysis model."""
    
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
    
    # Questions for founders
    questions: list[str] = Field(default=[], description="Relevant questions for founders based on analysis - addressing information gaps, contradictions, clarifications, or additional info needed")


product_agent = LlmAgent(
    model=config.specialist_model,
    name="product_agent",
    description="Analyzes product-market fit, traction metrics, and scalability potential",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.product_agent_prompt}
    """,
    output_schema=ProductAnalysis,
    output_key="product_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        collect_analysis_sources_callback
    ],
)

product_spy = LlmAgent(
    model=config.specialist_model,
    name="product_spy",
    description="Searches for additional information about the startup's product and traction using Google search",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.product_spy_prompt}
    """,
    tools=[google_search]
)

product_analyst = SequentialAgent(
    name="product_analyst",
    sub_agents=[
        product_spy,
        product_agent
    ],
    description="Analyzes product-market fit, traction metrics, and scalability potential. Runs the spy agent to gather additional product and traction information from internet and then runs the product agent to analyze the product-market fit, traction metrics, and scalability potential."
)
