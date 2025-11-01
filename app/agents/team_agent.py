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

"""Team analysis specialist agent."""

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field
import datetime
from .config import config, prompts
from .callbacks import (
    collect_analysis_sources_callback,
    track_agent_execution_callback,
    store_agent_analysis_callback,
)


class TeamAnalysis(BaseModel):
    """Model for team analysis results."""
    
    overall_score: float = Field(..., ge=1, le=10, description="Overall team score (1-10)")
    
    # Detailed scoring
    founder_market_fit_score: float = Field(..., ge=1, le=10, description="Founder-market fit score")
    team_completeness_score: float = Field(..., ge=1, le=10, description="Team completeness score")
    experience_score: float = Field(..., ge=1, le=10, description="Experience and track record score")
    leadership_score: float = Field(..., ge=1, le=10, description="Leadership capability score")
    
    # Analysis sections
    executive_summary: str = Field(..., description="Executive summary of team analysis")
    founder_analysis: str = Field(..., description="Detailed founder analysis")
    team_composition: str = Field(..., description="Team composition and gaps analysis")
    experience_assessment: str = Field(..., description="Experience and track record assessment")
    leadership_evaluation: str = Field(..., description="Leadership and culture evaluation")
    
    # Key findings
    strengths: list[str] = Field(default=[], description="Key team strengths")
    weaknesses: list[str] = Field(default=[], description="Team weaknesses and gaps")
    red_flags: list[str] = Field(default=[], description="Red flags or concerns")
    recommendations: list[str] = Field(default=[], description="Recommendations for team development")
    
    # Supporting evidence
    supporting_evidence: list[str] = Field(default=[], description="Supporting evidence and examples")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")
    
    # Questions for founders
    questions: list[str] = Field(default=[], description="Relevant questions for founders based on analysis - addressing information gaps, contradictions, clarifications, or additional info needed")


team_agent = LlmAgent(
    model=config.specialist_model,
    name="team_agent",
    description="Analyzes startup team composition, founder-market fit, and leadership capabilities",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.team_agent_prompt}
    """,
    output_schema=TeamAnalysis,
    output_key="team_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        store_agent_analysis_callback,
        collect_analysis_sources_callback
    ],
)

team_spy = LlmAgent(
    model=config.specialist_model,
    name="team_spy",
    description="Searches for additional information about the startup's team and founders using Google search",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    Files Analysis: {{files_analysis}}
    {prompts.team_spy_prompt}
    """,
    tools=[google_search]
)

team_analyst = SequentialAgent(
    name="team_analyst",
    sub_agents=[
        team_spy,
        team_agent
    ],
    description="Analyzes startup team composition, founder-market fit, and leadership capabilities. Runs the spy agent to gather additional information about the team from internet and then runs the team agent to analyze the team composition, founder-market fit, and leadership capabilities."
)
