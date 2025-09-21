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

"""Competition and competitive landscape analysis specialist agent."""

from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

from ..config import config, prompts
from .callbacks import (
    collect_analysis_sources_callback,
    track_agent_execution_callback,
)


class Competitor(BaseModel):
    """Individual competitor analysis model."""
    
    name: str = Field(..., description="Competitor name")
    category: str = Field(..., description="Direct, indirect, or substitute competitor")
    description: str = Field(..., description="Brief description of the competitor")
    
    # Company details
    funding_raised: Optional[float] = Field(None, description="Total funding raised (USD)")
    valuation: Optional[float] = Field(None, description="Last known valuation (USD)")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    founded_year: Optional[int] = Field(None, description="Year founded")
    
    # Market position
    market_share: Optional[float] = Field(None, description="Estimated market share (%)")
    revenue_estimate: Optional[float] = Field(None, description="Estimated annual revenue (USD)")
    customer_count: Optional[int] = Field(None, description="Estimated customer count")
    
    # Competitive analysis
    strengths: list[str] = Field(..., description="Key competitive strengths")
    weaknesses: list[str] = Field(..., description="Key competitive weaknesses")
    differentiation: str = Field(..., description="How they differentiate from the startup")
    threat_level: str = Field(..., description="Threat level: Low, Medium, High, Critical")


class CompetitiveAdvantage(BaseModel):
    """Competitive advantage analysis model."""
    
    advantage_type: str = Field(..., description="Type of competitive advantage")
    description: str = Field(..., description="Detailed description of the advantage")
    sustainability: str = Field(..., description="How sustainable is this advantage")
    defensibility: float = Field(..., ge=1, le=10, description="Defensibility score (1-10)")
    evidence: list[str] = Field(..., description="Evidence supporting this advantage")


class CompetitionAnalysis(BaseModel):
    """Model for competition analysis results."""
    
    overall_score: float = Field(..., ge=1, le=10, description="Overall competitive position score (1-10)")
    
    # Detailed scoring
    competitive_landscape_score: float = Field(..., ge=1, le=10, description="Competitive landscape favorability score")
    differentiation_score: float = Field(..., ge=1, le=10, description="Product differentiation score")
    moat_strength_score: float = Field(..., ge=1, le=10, description="Defensive moat strength score")
    market_positioning_score: float = Field(..., ge=1, le=10, description="Market positioning score")
    
    # Competitive landscape
    direct_competitors: list[Competitor] = Field(..., description="Direct competitors analysis")
    indirect_competitors: list[Competitor] = Field(..., description="Indirect competitors analysis")
    substitute_threats: list[Competitor] = Field(..., description="Substitute threats analysis")
    
    # Competitive advantages
    competitive_advantages: list[CompetitiveAdvantage] = Field(..., description="Identified competitive advantages")
    
    # Analysis sections
    executive_summary: str = Field(..., description="Executive summary of competition analysis")
    competitive_landscape: str = Field(..., description="Overall competitive landscape assessment")
    market_positioning: str = Field(..., description="Startup's market positioning analysis")
    differentiation_analysis: str = Field(..., description="Product/service differentiation analysis")
    moat_analysis: str = Field(..., description="Defensive moat and barriers to entry analysis")
    competitive_threats: str = Field(..., description="Key competitive threats and risks")
    
    # Key findings
    key_differentiators: list[str] = Field(..., description="Key differentiating factors")
    competitive_risks: list[str] = Field(..., description="Major competitive risks")
    barriers_to_entry: list[str] = Field(..., description="Barriers to entry for new competitors")
    switching_costs: str = Field(..., description="Customer switching costs analysis")
    
    # Strategic recommendations
    competitive_strategy: str = Field(..., description="Recommended competitive strategy")
    positioning_recommendations: list[str] = Field(..., description="Market positioning recommendations")
    
    # Supporting evidence
    supporting_evidence: list[str] = Field(..., description="Supporting evidence and sources")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")


competition_agent = LlmAgent(
    model=config.specialist_model,
    name="competition_agent",
    description="Analyzes competitive landscape, moat strength, and market positioning",
    instruction=f"""
    {prompts.competition_agent_prompt}
    
    You are conducting comprehensive competitive analysis for investment due diligence. Your analysis should cover:
    
    **1. COMPETITIVE LANDSCAPE MAPPING**
    - Identify and analyze direct competitors (same solution, same market)
    - Evaluate indirect competitors (different solution, same problem)
    - Assess substitute threats (alternative ways to solve the problem)
    - Map competitive positioning and market share distribution
    - Analyze competitive dynamics and market structure
    
    **2. COMPETITOR DEEP DIVE**
    For each major competitor, analyze:
    - Company background, funding, and financial health
    - Product features, pricing, and go-to-market strategy
    - Market share, customer base, and growth trajectory
    - Strengths, weaknesses, and strategic positioning
    - Recent developments, partnerships, and strategic moves
    
    **3. DIFFERENTIATION ANALYSIS**
    - Evaluate the startup's unique value proposition
    - Assess product/service differentiation vs. competitors
    - Analyze pricing strategy and value positioning
    - Review brand positioning and market perception
    - Evaluate customer acquisition and retention advantages
    
    **4. DEFENSIVE MOAT ASSESSMENT**
    - Identify and evaluate competitive advantages:
      * Network effects and platform dynamics
      * Proprietary technology and intellectual property
      * Brand strength and customer loyalty
      * Regulatory advantages and compliance barriers
      * Data advantages and learning effects
      * Supply chain and distribution advantages
      * Cost advantages and economies of scale
    
    **5. BARRIERS TO ENTRY ANALYSIS**
    - Assess barriers preventing new competitors from entering
    - Evaluate switching costs for customers
    - Analyze capital requirements and resource barriers
    - Review regulatory and compliance requirements
    - Assess technical complexity and expertise requirements
    
    **RESEARCH METHODOLOGY**:
    - Use google_search to research competitors, their products, and market positioning
    - Look up recent funding rounds, valuations, and financial information
    - Search for competitive analysis reports and industry studies
    - Research patent filings, partnerships, and strategic announcements
    - Find customer reviews and comparisons between products
    - Analyze job postings and hiring patterns for competitive intelligence
    
    **COMPETITIVE INTELLIGENCE SOURCES**:
    - Company websites, product pages, and pricing information
    - Funding databases (Crunchbase, PitchBook) for financial data
    - Industry reports and analyst coverage
    - Customer review sites and comparison platforms
    - Social media presence and marketing strategies
    - Patent databases and intellectual property filings
    - News coverage and press releases
    
    **SCORING CRITERIA**:
    - 9-10: Strong competitive position with sustainable advantages and high barriers
    - 7-8: Good competitive position with some defensible advantages
    - 5-6: Moderate position with limited differentiation
    - 3-4: Weak position with significant competitive threats
    - 1-2: Poor position with little differentiation and strong competition
    
    **OUTPUT REQUIREMENTS**:
    - Provide detailed analysis using the CompetitionAnalysis model
    - Include comprehensive competitor profiles with specific data
    - Assess competitive advantages with evidence and sustainability
    - Support all claims with credible sources and research
    - Be objective about competitive threats and risks
    - Provide actionable strategic recommendations
    - Cite all sources used in your research
    """,
    tools=[google_search],
    output_schema=CompetitionAnalysis,  # Changed to use output_schema as per ADK docs
    output_key="competition_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        collect_analysis_sources_callback
    ],
)
