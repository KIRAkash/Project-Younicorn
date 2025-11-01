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

"""Project Younicorn AI-powered startup due diligence analysis agent system."""

import datetime
import logging
from typing import Dict, Any, List

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import google_search
from pydantic import BaseModel, Field, ConfigDict

# from .config import config, prompts
from app.agents import (
    files_analysis_agent,
    team_agent,
    market_agent,
    product_agent,
    competition_agent,
    synthesis_agent,
)

logger = logging.getLogger(__name__)


# --- Structured Output Models ---
class StartupInfo(BaseModel):
    """Input model for startup submission data."""
    company_info: str = Field(description="Company information as JSON string")
    founders: str = Field(description="Founder information as JSON string")
    attachments: str = Field(default="[]", description="Extracted text from uploaded files as JSON string")
    metadata: str = Field(default="{}", description="Additional metadata as JSON string")
    
    # Reanalysis fields
    is_reanalysis: bool = Field(default=False, description="Whether this is a reanalysis")
    investor_notes: str = Field(default="", description="Specific notes/instructions from investor")
    answered_questions: str = Field(default="[]", description="Questions answered by founders as JSON string")



# --- Main Workflow ---
parallel_analysis = ParallelAgent(
    name="parallel_specialist_analysis",
    description="Runs specialist agents in parallel for comprehensive analysis",
    sub_agents=[
        team_agent.team_analyst,
        market_agent.market_analyst,
        product_agent.product_analyst,
        competition_agent.competition_analyst
    ]
)

minerva_analysis_agent = SequentialAgent(
    name="minerva_analysis_workflow",
    description="Complete Project Minerva startup due diligence analysis workflow",
    sub_agents=[
        files_analysis_agent.files_analysis_agent,  # First: Analyze all submitted files
        parallel_analysis,  # Second: Parallel specialist analysis
        synthesis_agent.synthesis_agent  # Third: Final synthesis
    ]
)




