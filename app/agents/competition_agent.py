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
from google.adk.agents import LlmAgent,SequentialAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field
import datetime
from .config import config, prompts
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
    
    # Web presence
    public_url: Optional[str] = Field(None, description="Competitor's public website URL (e.g., 'doordash.com', 'uber.com')")
    public_logo_url: Optional[str] = Field(None, description="Competitor's logo URL using Google favicon service in this exact format: https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://<COMPANY_URL>&size=64 where <COMPANY_URL> is replaced with the competitor's domain")
    
    # Market position
    market_share: Optional[float] = Field(None, description="Estimated market share (%)")
    revenue_estimate: Optional[float] = Field(None, description="Estimated annual revenue (USD)")
    customer_count: Optional[int] = Field(None, description="Estimated customer count")
    
    # Competitive analysis
    strengths: list[str] = Field(default=[], description="Key competitive strengths")
    weaknesses: list[str] = Field(default=[], description="Key competitive weaknesses")
    differentiation: str = Field(..., description="How they differentiate from the startup")
    threat_level: str = Field(..., description="Threat level: Low, Medium, High, Critical")


class CompetitiveAdvantage(BaseModel):
    """Competitive advantage analysis model."""
    
    advantage_type: str = Field(..., description="Type of competitive advantage")
    description: str = Field(..., description="Detailed description of the advantage")
    sustainability: str = Field(..., description="How sustainable is this advantage")
    defensibility: float = Field(..., ge=1, le=10, description="Defensibility score (1-10)")
    evidence: list[str] = Field(default=[], description="Evidence supporting this advantage")


class CompetitionAnalysis(BaseModel):
    """Model for competition analysis results."""
    
    overall_score: float = Field(..., ge=1, le=10, description="Overall competitive position score (1-10)")
    
    # Detailed scoring
    competitive_landscape_score: float = Field(..., ge=1, le=10, description="Competitive landscape favorability score")
    differentiation_score: float = Field(..., ge=1, le=10, description="Product differentiation score")
    moat_strength_score: float = Field(..., ge=1, le=10, description="Defensive moat strength score")
    market_positioning_score: float = Field(..., ge=1, le=10, description="Market positioning score")
    
    # Competitive landscape
    direct_competitors: list[Competitor] = Field(default=[], description="Direct competitors analysis")
    indirect_competitors: list[Competitor] = Field(default=[], description="Indirect competitors analysis")
    substitute_threats: list[Competitor] = Field(default=[], description="Substitute threats analysis")
    
    # Competitive advantages
    competitive_advantages: list[CompetitiveAdvantage] = Field(default=[], description="Identified competitive advantages")
    
    # Analysis sections
    executive_summary: str = Field(..., description="Executive summary of competition analysis")
    competitive_landscape: str = Field(..., description="Overall competitive landscape assessment")
    market_positioning: str = Field(..., description="Startup's market positioning analysis")
    differentiation_analysis: str = Field(..., description="Product/service differentiation analysis")
    moat_analysis: str = Field(..., description="Defensive moat and barriers to entry analysis")
    competitive_threats: str = Field(..., description="Key competitive threats and risks")
    
    # Key findings
    key_differentiators: list[str] = Field(default=[], description="Key differentiating factors")
    competitive_risks: list[str] = Field(default=[], description="Major competitive risks")
    barriers_to_entry: list[str] = Field(default=[], description="Barriers to entry for new competitors")
    switching_costs: str = Field(..., description="Customer switching costs analysis")
    
    # Strategic recommendations
    competitive_strategy: str = Field(..., description="Recommended competitive strategy")
    positioning_recommendations: list[str] = Field(default=[], description="Market positioning recommendations")
    
    # Supporting evidence
    supporting_evidence: list[str] = Field(default=[], description="Supporting evidence and sources")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")
    
    # Questions for founders
    questions: list[str] = Field(default=[], description="Relevant questions for founders based on analysis - addressing information gaps, contradictions, clarifications, or additional info needed")


competition_agent = LlmAgent(
    model=config.specialist_model,
    name="competition_agent",
    description="Analyzes competitive landscape, moat strength, and market positioning",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.competition_agent_prompt}
    """,
    output_schema=CompetitionAnalysis,
    output_key="competition_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        collect_analysis_sources_callback
    ],
)

competition_spy = LlmAgent(
    model=config.specialist_model,
    name="competition_spy",
    description="Searches for additional information about the startup using Google search",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.competition_spy_prompt}
    """,
    tools=[google_search]
)


competition_analyst = SequentialAgent(
    name="competition_analyst",
    sub_agents=[
        competition_spy,
        competition_agent
    ],
    description="Analyzes competitive landscape, moat strength, and market positioning. Runs the spy agent to gather additional information about the startup from internet and then runs the competition agent to analyze the competitive landscape, moat strength, and market positioning."
)
