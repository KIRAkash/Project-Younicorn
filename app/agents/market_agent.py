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

"""Market analysis specialist agent."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

from ..config import config, prompts
from .callbacks import (
    collect_analysis_sources_callback,
    track_agent_execution_callback,
)


class MarketSizing(BaseModel):
    """Market sizing analysis model."""
    
    class Config:
        extra = "forbid"
    
    tam_usd: float = Field(..., description="Total Addressable Market in USD")
    sam_usd: float = Field(..., description="Serviceable Addressable Market in USD")
    som_usd: float = Field(..., description="Serviceable Obtainable Market in USD")
    
    tam_methodology: str = Field(..., description="Methodology used for TAM calculation")
    sam_methodology: str = Field(..., description="Methodology used for SAM calculation")
    som_methodology: str = Field(..., description="Methodology used for SOM calculation")
    
    market_growth_rate: float = Field(..., description="Annual market growth rate (%)")
    market_maturity: str = Field(..., description="Market maturity stage")


class MarketAnalysis(BaseModel):
    """Model for market analysis results."""
    
    class Config:
        extra = "forbid"
    
    overall_score: float = Field(..., ge=1, le=10, description="Overall market score (1-10)")
    
    # Detailed scoring
    market_size_score: float = Field(..., ge=1, le=10, description="Market size attractiveness score")
    market_growth_score: float = Field(..., ge=1, le=10, description="Market growth potential score")
    market_timing_score: float = Field(..., ge=1, le=10, description="Market timing score")
    market_accessibility_score: float = Field(..., ge=1, le=10, description="Market accessibility score")
    
    # Market sizing
    market_sizing: MarketSizing = Field(..., description="Detailed market sizing analysis")
    
    # Analysis sections
    executive_summary: str = Field(..., description="Executive summary of market analysis")
    market_definition: str = Field(..., description="Clear market definition and segmentation")
    market_trends: str = Field(..., description="Key market trends and drivers")
    market_timing: str = Field(..., description="Market timing and readiness analysis")
    regulatory_environment: str = Field(..., description="Regulatory environment assessment")
    
    # Key findings
    opportunities: list[str] = Field(default=[], description="Key market opportunities")
    challenges: list[str] = Field(default=[], description="Market challenges and barriers")
    trends_supporting: list[str] = Field(default=[], description="Trends supporting the business")
    trends_opposing: list[str] = Field(default=[], description="Trends that could oppose the business")
    
    # Supporting evidence
    supporting_evidence: list[str] = Field(default=[], description="Supporting evidence and data sources")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")


market_agent = LlmAgent(
    model=config.specialist_model,
    name="market_agent",
    description="Analyzes market size, trends, timing, and opportunity validation",
    instruction=f"""
    {prompts.market_agent_prompt}
    
    You are conducting comprehensive market analysis for investment due diligence. Your analysis should cover:
    
    **1. MARKET SIZING & VALIDATION**
    - Calculate Total Addressable Market (TAM) using multiple methodologies
    - Determine Serviceable Addressable Market (SAM) based on geographic and segment focus
    - Estimate Serviceable Obtainable Market (SOM) considering competitive landscape
    - Validate market size claims made by the startup
    - Cross-reference multiple data sources for accuracy
    
    **2. MARKET TRENDS & GROWTH ANALYSIS**
    - Identify key market trends and growth drivers
    - Analyze historical growth patterns and future projections
    - Assess market maturity and lifecycle stage
    - Evaluate technological, social, and economic factors
    - Identify emerging opportunities and threats
    
    **3. MARKET TIMING & READINESS**
    - Assess whether the market is ready for the solution
    - Evaluate adoption barriers and enablers
    - Analyze competitive timing and first-mover advantages
    - Review infrastructure readiness and ecosystem maturity
    - Consider regulatory and policy environment
    
    **4. MARKET ACCESSIBILITY & PENETRATION**
    - Evaluate barriers to market entry
    - Assess customer acquisition challenges and costs
    - Analyze distribution channels and go-to-market feasibility
    - Review network effects and scalability potential
    - Consider geographic expansion opportunities
    
    **RESEARCH METHODOLOGY**:
    - Use google_search to find industry reports, market research, and analyst coverage
    - Look up government statistics, trade association data, and academic studies
    - Research competitor financials and market share data
    - Find recent funding rounds and valuations in the space
    - Validate market size claims with multiple independent sources
    
    **MARKET SIZING APPROACHES**:
    - Top-down: Industry reports and analyst estimates
    - Bottom-up: Customer segments × average spend × adoption rates
    - Comparable: Similar markets and analogous industries
    - Cross-validation: Multiple methodologies for accuracy
    
    **SCORING CRITERIA**:
    - 9-10: Massive, fast-growing market with perfect timing and accessibility
    - 7-8: Large, growing market with good timing and reasonable accessibility
    - 5-6: Moderate market with decent growth and some challenges
    - 3-4: Small or declining market with significant barriers
    - 1-2: Negligible market or poor timing with major obstacles
    
    **OUTPUT REQUIREMENTS**:
    - Provide detailed analysis using the MarketAnalysis model
    - Include specific market sizing with clear methodologies
    - Support all claims with credible sources and data
    - Be realistic about market size and growth projections
    - Highlight both opportunities and challenges
    - Cite all sources used in your research
    """,
    # tools=[google_search],  # Disabled for parallel execution compatibility
    output_schema=MarketAnalysis,  # Changed to use output_schema as per ADK docs
    output_key="market_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        collect_analysis_sources_callback
    ],
)
