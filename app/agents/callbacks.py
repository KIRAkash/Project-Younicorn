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

"""Callback functions for agent execution tracking and source collection."""

import datetime
import logging
from typing import Dict, List, Any

from google.adk.agents.callback_context import CallbackContext

from ..models.analysis import SourceCitation, AgentTrace

logger = logging.getLogger(__name__)


def collect_analysis_sources_callback(callback_context: CallbackContext) -> None:
    """Collects and organizes web-based research sources from agent events.

    This function processes the agent's session events to extract web source details
    and associated text segments with confidence scores. The aggregated source
    information is stored in callback_context.state for later use.

    Args:
        callback_context (CallbackContext): The context object providing access to
            the agent's session events and persistent state.
    """
    session = callback_context._invocation_context.session
    url_to_citation = callback_context.state.get("url_to_citation", {})
    sources = callback_context.state.get("sources", {})
    citation_counter = len(url_to_citation) + 1

    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue

        chunks_info = {}
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            if not chunk.web:
                continue

            url = chunk.web.uri
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )

            if url not in url_to_citation:
                citation_id = f"src-{citation_counter}"
                url_to_citation[url] = citation_id
                
                # Create SourceCitation object
                citation = SourceCitation(
                    id=citation_id,
                    title=title,
                    url=url,
                    domain=chunk.web.domain,
                )
                sources[citation_id] = citation.dict()
                citation_counter += 1

            chunks_info[idx] = url_to_citation[url]

        # Process grounding supports for confidence scores
        if event.grounding_metadata.grounding_supports:
            for support in event.grounding_metadata.grounding_supports:
                if support.grounding_chunk_indices:
                    for chunk_idx in support.grounding_chunk_indices:
                        if chunk_idx in chunks_info:
                            citation_id = chunks_info[chunk_idx]
                            if citation_id in sources:
                                # Add supported claim with confidence
                                claim = {
                                    "text": support.segment.text if support.segment else "",
                                    "confidence": getattr(support, "confidence", 0.8),
                                    "start_index": getattr(support.segment, "start_index", 0) if support.segment else 0,
                                    "end_index": getattr(support.segment, "end_index", 0) if support.segment else 0,
                                }
                                
                                if "supported_claims" not in sources[citation_id]:
                                    sources[citation_id]["supported_claims"] = []
                                sources[citation_id]["supported_claims"].append(claim)

    # Update callback state
    callback_context.state["url_to_citation"] = url_to_citation
    callback_context.state["sources"] = sources


def track_agent_execution_callback(callback_context: CallbackContext) -> None:
    """Tracks agent execution steps for transparency and debugging.

    This function creates a detailed trace of agent execution including
    reasoning, tool usage, and timing information.

    Args:
        callback_context (CallbackContext): The context object for tracking execution.
    """
    session = callback_context._invocation_context.session
    execution_trace = callback_context.state.get("execution_trace", [])
    
    # Get the current agent name
    agent_name = getattr(callback_context._invocation_context, "agent_name", "unknown")
    
    for event in session.events[-1:]:  # Process only the latest event
        if hasattr(event, "content") and event.content:
            step = AgentTrace(
                step_number=len(execution_trace) + 1,
                action=f"Generated response",
                reasoning=getattr(event, "thinking", None),
                tool_used=None,
                input_data={"agent": agent_name},
                output_data={"content_length": len(str(event.content))},
                timestamp=datetime.datetime.utcnow(),
            )
            execution_trace.append(step.dict())
        
        # Track tool usage
        if hasattr(event, "tool_calls") and event.tool_calls:
            for tool_call in event.tool_calls:
                step = AgentTrace(
                    step_number=len(execution_trace) + 1,
                    action=f"Used tool: {tool_call.name}",
                    reasoning=f"Tool called with parameters: {tool_call.args}",
                    tool_used=tool_call.name,
                    input_data=tool_call.args,
                    output_data=None,  # Will be filled when tool response is available
                    timestamp=datetime.datetime.utcnow(),
                )
                execution_trace.append(step.dict())

    callback_context.state["execution_trace"] = execution_trace


def update_analysis_progress_callback(callback_context: CallbackContext) -> None:
    """Updates analysis progress for real-time status tracking.

    This function tracks the progress of the overall analysis and updates
    the progress state for frontend consumption.

    Args:
        callback_context (CallbackContext): The context object for progress tracking.
    """
    session = callback_context._invocation_context.session
    progress = callback_context.state.get("analysis_progress", {
        "total_steps": 6,  # orchestrator + 4 specialists + synthesis
        "completed_steps": 0,
        "current_agent": "orchestrator",
        "status": "in_progress",
        "started_at": datetime.datetime.utcnow().isoformat(),
    })
    
    # Get current agent name
    agent_name = getattr(callback_context._invocation_context, "agent_name", "unknown")
    
    # Update current agent
    progress["current_agent"] = agent_name
    progress["last_updated"] = datetime.datetime.utcnow().isoformat()
    
    # Track completion based on agent type
    agent_completion_map = {
        "orchestrator_agent": 1,
        "team_agent": 2,
        "market_agent": 3,
        "product_agent": 4,
        "competition_agent": 5,
        "synthesis_agent": 6,
    }
    
    if agent_name in agent_completion_map:
        progress["completed_steps"] = agent_completion_map[agent_name]
        
        if agent_name == "synthesis_agent":
            progress["status"] = "completed"
            progress["completed_at"] = datetime.datetime.utcnow().isoformat()
    
    # Calculate progress percentage
    progress["progress_percentage"] = (progress["completed_steps"] / progress["total_steps"]) * 100
    
    callback_context.state["analysis_progress"] = progress
    
    logger.info(f"Analysis progress updated: {progress['progress_percentage']:.1f}% - {agent_name}")


def store_agent_analysis_callback(callback_context: CallbackContext) -> None:
    """Stores individual agent analysis results.

    This function captures and stores the analysis results from each specialist agent
    for later synthesis and dashboard display.

    Args:
        callback_context (CallbackContext): The context object for storing results.
    """
    session = callback_context._invocation_context.session
    agent_name = getattr(callback_context._invocation_context, "agent_name", "unknown")
    
    # Get the latest agent output
    latest_events = session.events[-5:]  # Look at recent events
    agent_output = None
    
    for event in reversed(latest_events):
        if hasattr(event, "content") and event.content:
            agent_output = str(event.content)
            break
    
    if agent_output:
        # Store agent-specific results
        agent_results = callback_context.state.get("agent_results", {})
        agent_results[agent_name] = {
            "output": agent_output,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "sources": callback_context.state.get("sources", {}),
            "execution_trace": callback_context.state.get("execution_trace", []),
        }
        callback_context.state["agent_results"] = agent_results
        
        logger.info(f"Stored analysis results for {agent_name}")


def collect_feedback_requests_callback(callback_context: CallbackContext) -> None:
    """Collects human-in-the-loop feedback requests from agents.

    This function identifies when agents request human feedback and stores
    these requests for frontend processing.

    Args:
        callback_context (CallbackContext): The context object for feedback tracking.
    """
    session = callback_context._invocation_context.session
    feedback_requests = callback_context.state.get("feedback_requests", [])
    
    # Look for feedback request patterns in agent outputs
    for event in session.events[-3:]:  # Check recent events
        if hasattr(event, "content") and event.content:
            content = str(event.content).lower()
            
            # Simple pattern matching for feedback requests
            feedback_patterns = [
                "need clarification",
                "requires human input",
                "please confirm",
                "feedback needed",
                "human review required",
            ]
            
            for pattern in feedback_patterns:
                if pattern in content:
                    feedback_request = {
                        "id": f"feedback-{len(feedback_requests) + 1}",
                        "agent": getattr(callback_context._invocation_context, "agent_name", "unknown"),
                        "question": str(event.content),
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "resolved": False,
                    }
                    feedback_requests.append(feedback_request)
                    break
    
    callback_context.state["feedback_requests"] = feedback_requests
