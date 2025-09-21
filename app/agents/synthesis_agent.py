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

from ..config import config, prompts
from .callbacks import (
    track_agent_execution_callback,
    update_analysis_progress_callback,
)


class InvestmentRecommendation(BaseModel):
    """Investment recommendation model."""
    
    recommendation: str = Field(..., description="Investment recommendation: Strong Buy, Buy, Hold, Pass")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in recommendation (0-1)")
    rationale: str = Field(..., description="Detailed rationale for the recommendation")
    
    # Investment terms suggestions
    suggested_valuation_range: str = Field(..., description="Suggested valuation range")
    investment_size_recommendation: str = Field(..., description="Recommended investment size")
    key_terms: list[str] = Field(..., description="Key investment terms to negotiate")
    
    # Conditions and requirements
    investment_conditions: list[str] = Field(default_factory=list, description="Conditions for investment")
    due_diligence_requirements: list[str] = Field(default_factory=list, description="Additional due diligence needed")


class RiskAssessment(BaseModel):
    """Risk assessment model."""
    
    overall_risk_level: str = Field(..., description="Overall risk level: Low, Medium, High, Critical")
    
    # Risk categories
    team_risks: list[str] = Field(default_factory=list, description="Team-related risks")
    market_risks: list[str] = Field(default_factory=list, description="Market-related risks")
    product_risks: list[str] = Field(default_factory=list, description="Product-related risks")
    competitive_risks: list[str] = Field(default_factory=list, description="Competitive risks")
    execution_risks: list[str] = Field(default_factory=list, description="Execution risks")
    
    # Risk mitigation
    mitigation_strategies: list[str] = Field(..., description="Risk mitigation strategies")
    monitoring_requirements: list[str] = Field(..., description="Key metrics to monitor")


class OpportunityAssessment(BaseModel):
    """Opportunity assessment model."""
    
    overall_opportunity_level: str = Field(..., description="Overall opportunity level: Low, Medium, High, Exceptional")
    
    # Opportunity categories
    market_opportunities: list[str] = Field(..., description="Market opportunities")
    product_opportunities: list[str] = Field(..., description="Product development opportunities")
    expansion_opportunities: list[str] = Field(..., description="Market expansion opportunities")
    strategic_opportunities: list[str] = Field(..., description="Strategic partnership opportunities")
    
    # Value creation potential
    value_creation_drivers: list[str] = Field(..., description="Key value creation drivers")
    exit_scenarios: list[str] = Field(..., description="Potential exit scenarios")


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
    key_insights: list[str] = Field(..., description="Key insights from the analysis")
    
    # Investment recommendation
    investment_recommendation: InvestmentRecommendation = Field(..., description="Investment recommendation")
    
    # Risk and opportunity assessment
    risk_assessment: RiskAssessment = Field(..., description="Comprehensive risk assessment")
    opportunity_assessment: OpportunityAssessment = Field(..., description="Opportunity assessment")
    
    # Comparative analysis
    comparable_companies: list[str] = Field(default_factory=list, description="Comparable companies for benchmarking")
    competitive_positioning: str = Field(..., description="Competitive positioning summary")
    
    # Next steps
    next_steps: list[str] = Field(..., description="Recommended next steps")
    timeline: str = Field(..., description="Suggested timeline for decision making")
    
    # Quality metrics
    analysis_completeness: float = Field(..., ge=0, le=1, description="Analysis completeness score (0-1)")
    data_quality: float = Field(..., ge=0, le=1, description="Overall data quality score (0-1)")
    confidence_level: float = Field(..., ge=0, le=1, description="Overall confidence in analysis (0-1)")


synthesis_agent = LlmAgent(
    model=config.synthesis_model,
    name="synthesis_agent",
    description="Synthesizes specialist analysis into final investment recommendations",
    instruction=f"""
    {prompts.synthesis_agent_prompt}
    
    You are the final synthesis agent responsible for compiling all specialist analyses into a comprehensive investment memo and recommendation. Your task is to:
    
    **1. INTEGRATE ALL ANALYSES**
    - Review and synthesize findings from all specialist agents:
      * Orchestrator's analysis plan and priorities
      * Team agent's founder and team assessment
      * Market agent's market sizing and opportunity analysis
      * Product agent's traction and scalability assessment
      * Competition agent's competitive landscape analysis
    
    **2. CALCULATE OVERALL INVESTABILITY SCORE**
    - Weight the component scores appropriately:
      * Team: 25% (execution capability is critical)
      * Market: 25% (market opportunity size and timing)
      * Product: 30% (product-market fit and traction)
      * Competition: 20% (competitive position and defensibility)
    - Provide clear rationale for the overall score
    
    **3. DEVELOP INVESTMENT THESIS**
    - Create a compelling and clear investment thesis
    - Highlight the key value proposition and opportunity
    - Address why this startup can succeed in this market
    - Explain the potential for significant returns
    
    **4. COMPREHENSIVE RISK ASSESSMENT**
    - Identify and categorize all major risks
    - Assess likelihood and potential impact of each risk
    - Provide mitigation strategies and monitoring requirements
    - Highlight any deal-breaking risks or red flags
    
    **5. OPPORTUNITY ASSESSMENT**
    - Identify key value creation opportunities
    - Assess upside potential and growth scenarios
    - Evaluate strategic options and expansion possibilities
    - Consider exit scenarios and potential returns
    
    **6. INVESTMENT RECOMMENDATION**
    - Provide clear investment recommendation (Strong Buy, Buy, Hold, Pass)
    - Suggest appropriate valuation range and investment size
    - Outline key investment terms and conditions
    - Specify any additional due diligence requirements
    
    **7. EXECUTIVE SUMMARY**
    - Create a concise executive summary for busy investors
    - Highlight the most critical points and decision factors
    - Include key metrics, scores, and recommendation
    - Make it actionable and decision-oriented
    
    **SYNTHESIS PRINCIPLES**:
    - Maintain objectivity and balance positive and negative findings
    - Ensure consistency across all analyses and recommendations
    - Highlight any conflicting findings or areas of uncertainty
    - Provide evidence-based conclusions with proper citations
    - Consider the investor's perspective and decision-making needs
    
    **QUALITY ASSURANCE**:
    - Verify that all key investment criteria have been addressed
    - Ensure recommendations are supported by evidence
    - Check for logical consistency across all sections
    - Validate that sources are properly cited and traceable
    - Assess completeness and identify any gaps in analysis
    
    **OUTPUT REQUIREMENTS**:
    - Provide comprehensive synthesis using the SynthesisResult model
    - Create a professional investment memo suitable for investment committee
    - Include clear, actionable recommendations with supporting rationale
    - Ensure all claims are supported by evidence from specialist analyses
    - Maintain professional tone appropriate for institutional investors
    """,
    output_schema=SynthesisResult,  # Changed to use output_schema as per ADK docs
    output_key="synthesis_result",
    after_agent_callback=[
        track_agent_execution_callback,
        update_analysis_progress_callback
    ],
)
