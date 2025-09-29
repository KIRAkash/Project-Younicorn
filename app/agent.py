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

"""Project Minerva AI-powered startup due diligence analysis agent system."""

import datetime
import logging
from typing import Dict, Any, List

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import google_search
from pydantic import BaseModel, Field

from .config import config, prompts

logger = logging.getLogger(__name__)


# --- Structured Output Models ---
class StartupInfo(BaseModel):
    """Input model for startup submission data."""
    class Config:
        extra = "forbid"  # Disable additionalProperties
    
    company_info: str = Field(description="Company information as JSON string")
    founders: str = Field(description="Founder information as JSON string")
    documents: str = Field(default="[]", description="Supporting documents as JSON string")
    metadata: str = Field(default="{}", description="Additional metadata as JSON string")


class AgentAnalysis(BaseModel):
    """Output model for individual agent analysis."""
    class Config:
        extra = "forbid"  # Disable additionalProperties
    
    agent_name: str = Field(description="Name of the analyzing agent")
    score: float = Field(description="Numerical score from 1-10")
    summary: str = Field(description="Executive summary of findings")
    detailed_analysis: str = Field(description="Comprehensive analysis")
    key_findings: List[str] = Field(description="Key insights and findings")
    risks: List[str] = Field(default=[], description="Identified risks")
    opportunities: List[str] = Field(default=[], description="Identified opportunities")
    sources: List[str] = Field(default=[], description="Sources used in analysis")


class FinalAnalysis(BaseModel):
    """Final synthesis of all agent analyses."""
    class Config:
        extra = "forbid"  # Disable additionalProperties
    
    overall_score: float = Field(description="Overall investment score from 1-10")
    investment_recommendation: str = Field(description="INVEST, PASS, or WATCH recommendation")
    confidence_level: float = Field(description="Confidence in recommendation (0-1)")
    executive_summary: str = Field(description="High-level executive summary")
    investment_memo: str = Field(description="Detailed investment memo")
    agent_summaries: str = Field(description="Summary of individual agent analyses as text")
    key_insights: List[str] = Field(description="Top insights across all analyses")
    risk_factors: List[str] = Field(description="Primary risk factors")
    growth_opportunities: List[str] = Field(description="Key growth opportunities")
    next_steps: List[str] = Field(description="Recommended next steps")


# --- Callback Functions ---
def collect_analysis_sources_callback(callback_context: CallbackContext) -> None:
    """Collects sources from agent analysis for citation tracking."""
    try:
        # Safely access session and state
        if not hasattr(callback_context, '_invocation_context') or not callback_context._invocation_context:
            logger.debug("No invocation context available for source collection")
            return
            
        session = getattr(callback_context._invocation_context, 'session', None)
        if not session:
            logger.debug("No session available for source collection")
            return
            
        url_to_citation = callback_context.state.get("url_to_citation", {})
        sources = callback_context.state.get("sources", {})
        citation_counter = len(url_to_citation) + 1
        
        # Check if session has events
        if not hasattr(session, 'events') or not session.events:
            logger.debug("No session events available for source collection")
            return
        
        for event in session.events:
            if not (hasattr(event, 'grounding_metadata') and event.grounding_metadata and 
                   hasattr(event.grounding_metadata, 'grounding_chunks') and event.grounding_metadata.grounding_chunks):
                continue
                
            for chunk in event.grounding_metadata.grounding_chunks:
                if not hasattr(chunk, 'web') or not chunk.web:
                    continue
                    
                url = chunk.web.uri
                title = chunk.web.title if chunk.web.title != chunk.web.domain else chunk.web.domain
                
                if url not in url_to_citation:
                    citation_id = f"cite-{citation_counter}"
                    url_to_citation[url] = citation_id
                    sources[citation_id] = {
                        "id": citation_id,
                        "title": title,
                        "url": url,
                        "domain": chunk.web.domain
                    }
                    citation_counter += 1
        
        callback_context.state["url_to_citation"] = url_to_citation
        callback_context.state["sources"] = sources
        logger.debug(f"Collected {len(sources)} sources for citation tracking")
    except Exception as e:
        logger.warning(f"Error in collect_analysis_sources_callback: {e}")


def track_agent_execution_callback(callback_context: CallbackContext) -> None:
    """Tracks agent execution progress and stores results."""
    try:
        # Safely access session and context
        if not hasattr(callback_context, '_invocation_context') or not callback_context._invocation_context:
            logger.debug("No invocation context available for execution tracking")
            return
            
        session = getattr(callback_context._invocation_context, 'session', None)
        agent_name = getattr(callback_context._invocation_context, 'agent_name', 'unknown')
        
        # Initialize tracking state
        if "execution_trace" not in callback_context.state:
            callback_context.state["execution_trace"] = []
        if "agent_results" not in callback_context.state:
            callback_context.state["agent_results"] = {}
        
        # Track execution
        execution_trace = callback_context.state["execution_trace"]
        events_count = 0
        if session and hasattr(session, 'events') and session.events:
            events_count = len(session.events)
            
        execution_trace.append({
            "agent": agent_name,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "status": "completed",
            "events_count": events_count
        })
        
        callback_context.state["execution_trace"] = execution_trace
        logger.info(f"Agent {agent_name} execution tracked")
    except Exception as e:
        logger.warning(f"Error in track_agent_execution_callback: {e}")


def store_agent_analysis_callback(callback_context: CallbackContext) -> None:
    """Stores individual agent analysis results."""
    try:
        # Safely access session and context
        if not hasattr(callback_context, '_invocation_context') or not callback_context._invocation_context:
            logger.debug("No invocation context available for result storage")
            return
            
        session = getattr(callback_context._invocation_context, 'session', None)
        agent_name = getattr(callback_context._invocation_context, 'agent_name', 'unknown')
        
        # Get the latest output from the session
        if session and hasattr(session, 'events') and session.events:
            latest_event = session.events[-1]
            if hasattr(latest_event, 'content') and latest_event.content:
                agent_results = callback_context.state.get("agent_results", {})
                agent_results[agent_name] = {
                    "agent_name": agent_name,
                    "content": latest_event.content,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
                callback_context.state["agent_results"] = agent_results
                logger.info(f"Stored analysis results for {agent_name}")
    except Exception as e:
        logger.warning(f"Error in store_agent_analysis_callback: {e}")


# --- Agent Definitions ---
team_agent = LlmAgent(
    model=config.specialist_model,
    name="team_agent",
    description="Analyzes founding team, leadership, and organizational structure",
    output_key="team_analysis",  # Store result in session state
    instruction=prompts.team_agent_prompt + f"""
    
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    
    Startup Information: {{startup_info}}
    
    Analyze the above startup information focusing on the team aspects including:
    - Founder backgrounds and experience
    - Team composition and completeness
    - Leadership track record
    - Advisory board strength
    
    Base your analysis on the provided startup information and your knowledge.
    Provide structured output following the AgentAnalysis schema with:
    - agent_name: "team_agent"
    - score: numerical score from 1-10
    - summary: executive summary of findings
    - detailed_analysis: comprehensive analysis
    - key_findings: list of key insights
    - risks: identified risks
    - opportunities: identified opportunities
    - sources: list of sources used
    """,
    # tools=[google_search],  # Disabled: Google search tool not compatible with Gemini 1.x in parallel execution
    # output_schema=AgentAnalysis,  # Temporarily disabled due to Gemini API additionalProperties issue
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=collect_analysis_sources_callback
)

market_agent = LlmAgent(
    model=config.specialist_model,
    name="market_agent",
    description="Analyzes market opportunity, size, and competitive landscape",
    output_key="market_analysis",  # Store result in session state
    instruction=prompts.market_agent_prompt + f"""
    
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    
    Startup Information: {{startup_info}}
    
    Analyze the market opportunity for the above startup including:
    - Total Addressable Market (TAM) validation
    - Serviceable Addressable Market (SAM) analysis
    - Market trends and growth projections
    - Market timing and readiness
    
    Base your analysis on the provided startup information and your knowledge of market trends.
    Provide structured output following the AgentAnalysis schema with agent_name: "market_agent".
    """,
    # tools=[google_search],  # Disabled: Google search tool not compatible with Gemini 1.x in parallel execution
    # output_schema=AgentAnalysis,  # Temporarily disabled due to Gemini API additionalProperties issue
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=collect_analysis_sources_callback
)

product_agent = LlmAgent(
    model=config.specialist_model,
    name="product_agent",
    description="Evaluates product-market fit, traction, and growth metrics",
    output_key="product_analysis",  # Store result in session state
    instruction=prompts.product_agent_prompt + f"""
    
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    
    Startup Information: {{startup_info}}
    
    Analyze the product and traction metrics for the above startup including:
    - Product-market fit assessment
    - Value proposition strength
    - Key performance metrics analysis
    - Customer acquisition and retention
    - Revenue model validation
    
    Base your analysis on the provided startup information and your knowledge.
    Provide structured output following the AgentAnalysis schema with agent_name: "product_agent".
    """,
    # tools=[google_search],  # Disabled: Google search tool not compatible with Gemini 1.x in parallel execution
    # output_schema=AgentAnalysis,  # Temporarily disabled due to Gemini API additionalProperties issue
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=collect_analysis_sources_callback
)

competition_agent = LlmAgent(
    model=config.specialist_model,
    name="competition_agent",
    description="Maps competitive landscape and assesses differentiation",
    output_key="competition_analysis",  # Store result in session state
    instruction=prompts.competition_agent_prompt + f"""
    
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    
    Startup Information: {{startup_info}}
    
    Analyze the competitive landscape for the above startup including:
    - Direct and indirect competitors identification
    - Competitive advantages and differentiation
    - Defensible moat analysis
    - Market positioning assessment
    - Competitive threats and risks
    
    Base your analysis on the provided startup information and your knowledge of competitive landscapes.
    Provide structured output following the AgentAnalysis schema with agent_name: "competition_agent".
    """,
    # tools=[google_search],  # Disabled: Google search tool not compatible with Gemini 1.x in parallel execution
    # output_schema=AgentAnalysis,  # Temporarily disabled due to Gemini API additionalProperties issue
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=collect_analysis_sources_callback
)

synthesis_agent = LlmAgent(
    model=config.synthesis_model,
    name="synthesis_agent",
    description="Synthesizes all analyses into final investment recommendation",
    instruction=prompts.synthesis_agent_prompt + f"""
    
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    
    Startup Information: {{startup_info}}
    
    Team Analysis: {{team_analysis?}}
    Market Analysis: {{market_analysis?}}
    Product Analysis: {{product_analysis?}}
    Competition Analysis: {{competition_analysis?}}
    
    Synthesize all the individual agent analyses above into a comprehensive final analysis including:
    - Overall investment score (1-10) based on individual agent scores
    - Clear investment recommendation (INVEST, PASS, or WATCH)
    - Confidence level in the recommendation (0-1)
    - Executive summary of key findings
    - Detailed investment memo
    - Key insights across all analyses
    - Primary risk factors
    - Growth opportunities
    - Recommended next steps
    
    Provide structured output following the FinalAnalysis schema.
    """,
    # output_schema=FinalAnalysis,  # Temporarily disabled due to Gemini API additionalProperties issue
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    after_agent_callback=store_agent_analysis_callback
)

# --- Main Workflow ---
parallel_analysis = ParallelAgent(
    name="parallel_specialist_analysis",
    description="Runs specialist agents in parallel for comprehensive analysis",
    sub_agents=[
        team_agent,
        market_agent,
        product_agent,
        competition_agent
    ]
)

minerva_analysis_agent = SequentialAgent(
    name="minerva_analysis_workflow",
    description="Complete Project Minerva startup due diligence analysis workflow",
    sub_agents=[
        parallel_analysis,
        synthesis_agent
    ]
)

# Export for API usage
__all__ = [
    "minerva_analysis_agent",
    "StartupInfo",
    "AgentAnalysis", 
    "FinalAnalysis",
    "collect_analysis_sources_callback",
    "track_agent_execution_callback",
    "store_agent_analysis_callback"
]
