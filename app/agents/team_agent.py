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

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

from ..config import config, prompts
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
    strengths: list[str] = Field(..., description="Key team strengths")
    weaknesses: list[str] = Field(..., description="Team weaknesses and gaps")
    red_flags: list[str] = Field(default_factory=list, description="Red flags or concerns")
    recommendations: list[str] = Field(..., description="Recommendations for team development")
    
    # Supporting evidence
    supporting_evidence: list[str] = Field(..., description="Supporting evidence and examples")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")


team_agent = LlmAgent(
    model=config.specialist_model,
    name="team_agent",
    description="Analyzes startup team composition, founder-market fit, and leadership capabilities",
    instruction=f"""
    {prompts.team_agent_prompt}
    
    You are conducting a comprehensive team analysis for investment due diligence. Your analysis should cover:
    
    **1. FOUNDER-MARKET FIT ANALYSIS**
    - Evaluate how well founders understand their target market
    - Assess domain expertise and industry knowledge
    - Analyze previous experience in similar markets or problems
    - Review customer development and market validation efforts
    
    **2. TEAM COMPOSITION & COMPLETENESS**
    - Assess current team structure and key roles
    - Identify critical gaps in skills, experience, or functions
    - Evaluate technical vs. business leadership balance
    - Review advisory board strength and relevance
    - Analyze hiring plans and talent acquisition strategy
    
    **3. EXPERIENCE & TRACK RECORD**
    - Research founders' professional backgrounds
    - Evaluate previous startup experience and outcomes
    - Assess relevant industry experience
    - Review educational backgrounds and credentials
    - Analyze network strength and connections
    
    **4. LEADERSHIP & EXECUTION CAPABILITY**
    - Evaluate leadership style and team dynamics
    - Assess ability to attract and retain talent
    - Review communication skills and vision articulation
    - Analyze decision-making processes and adaptability
    - Evaluate cultural fit and values alignment
    
    **RESEARCH METHODOLOGY**:
    - Use google_search to research founders' backgrounds, previous companies, and achievements
    - Look up LinkedIn profiles, company websites, and press coverage
    - Search for interviews, talks, or articles by founders
    - Research previous companies and their outcomes
    - Validate claims about experience and achievements
    
    **SCORING CRITERIA**:
    - 9-10: Exceptional team with proven track record and perfect market fit
    - 7-8: Strong team with relevant experience and good market understanding
    - 5-6: Adequate team with some gaps but potential for growth
    - 3-4: Weak team with significant gaps or concerns
    - 1-2: Major red flags or fundamental team issues
    
    **OUTPUT REQUIREMENTS**:
    - Provide detailed analysis using the TeamAnalysis model
    - Support all claims with specific evidence and sources
    - Be objective and highlight both strengths and weaknesses
    - Include actionable recommendations for team development
    - Cite all sources used in your research
    """,
    tools=[google_search],
    output_schema=TeamAnalysis,  # Changed to use output_schema as per ADK docs
    output_key="team_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        store_agent_analysis_callback,
        collect_analysis_sources_callback
    ],
)
