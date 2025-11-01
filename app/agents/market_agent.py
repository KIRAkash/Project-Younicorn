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

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field
import datetime
from .config import config, prompts
from .callbacks import (
    collect_analysis_sources_callback,
    track_agent_execution_callback,
)


class MarketSizing(BaseModel):
    """Market sizing analysis model."""
    
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
    
    # Questions for founders
    questions: list[str] = Field(default=[], description="Relevant questions for founders based on analysis - addressing information gaps, contradictions, clarifications, or additional info needed")


market_agent = LlmAgent(
    model=config.specialist_model,
    name="market_agent",
    description="Analyzes market size, trends, timing, and opportunity validation",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.market_agent_prompt}
    """,
    output_schema=MarketAnalysis,
    output_key="market_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        collect_analysis_sources_callback
    ],
)

market_spy = LlmAgent(
    model=config.specialist_model,
    name="market_spy",
    description="Searches for additional information about the startup's market using Google search",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.market_spy_prompt}
    """,
    tools=[google_search]
)

market_analyst = SequentialAgent(
    name="market_analyst",
    sub_agents=[
        market_spy,
        market_agent
    ],
    description="Analyzes market size, trends, timing, and opportunity validation. Runs the spy agent to gather additional market information from internet and then runs the market agent to analyze the market size, trends, timing, and opportunity validation."
)
