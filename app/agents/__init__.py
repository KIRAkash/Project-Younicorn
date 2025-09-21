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

"""Multi-agent system for Project Minerva due diligence analysis.

This module is deprecated. The new unified agent system is in app.agent.
"""

# Import from the new unified agent system
from ..agent import (
    minerva_analysis_agent,
    StartupInfo,
    AgentAnalysis,
    FinalAnalysis,
    collect_analysis_sources_callback,
    track_agent_execution_callback,
    store_agent_analysis_callback
)

__all__ = [
    "minerva_analysis_agent",
    "StartupInfo",
    "AgentAnalysis", 
    "FinalAnalysis",
    "collect_analysis_sources_callback",
    "track_agent_execution_callback",
    "store_agent_analysis_callback",
]
