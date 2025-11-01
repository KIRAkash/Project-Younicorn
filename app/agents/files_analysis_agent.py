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

"""Files analysis specialist agent - First agent to process all submitted multimedia files."""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
import datetime
from .config import config
from .callbacks import (
    track_agent_execution_callback,
    store_agent_analysis_callback,
)


class FilesAnalysisSummary(BaseModel):
    """Model for files analysis results from transcripts and extracted text."""
    
    # Summary sections
    executive_summary: str = Field(..., description="High-level summary of all content analyzed from transcripts and documents")
    
    # Transcript analysis (from video/audio)
    transcript_summary: str = Field(default="", description="Comprehensive summary of all transcribed speech from video/audio files")
    transcript_key_points: list[str] = Field(default=[], description="Key points, claims, and statements from transcripts")
    transcript_quotes: list[str] = Field(default=[], description="Important direct quotes from transcripts")
    
    # Document text analysis
    document_summary: str = Field(default="", description="Summary of extracted text from document files")
    document_key_facts: list[str] = Field(default=[], description="Key facts, data points, and claims from documents")
    document_sections: list[str] = Field(default=[], description="Main sections and topics covered in documents")
    
    # Consolidated insights (from all sources)
    all_facts_and_claims: list[str] = Field(default=[], description="All facts, claims, and statements from transcripts and documents")
    all_metrics_and_data: list[str] = Field(default=[], description="All metrics, numbers, and data points mentioned")
    all_team_information: list[str] = Field(default=[], description="All information about team, founders, and people")
    all_product_information: list[str] = Field(default=[], description="All information about product, features, and technology")
    all_market_information: list[str] = Field(default=[], description="All information about market, customers, and opportunity")
    all_traction_information: list[str] = Field(default=[], description="All information about traction, revenue, and growth")
    all_competitive_information: list[str] = Field(default=[], description="All information about competitors and differentiation")
    
    # Quality indicators
    total_files_analyzed: int = Field(default=0, description="Total number of files analyzed")
    file_types_analyzed: list[str] = Field(default=[], description="Types of files analyzed (transcript, document)")
    transcription_quality_notes: str = Field(default="", description="Notes about transcription quality or issues")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in the analysis completeness (0-1)")


files_analysis_prompt = """
You are the Files Analysis Agent for Project Younicorn's due diligence platform.

**YOUR CRITICAL ROLE**: You are the FIRST agent in the analysis workflow. Your job is to thoroughly analyze ALL submitted content (transcripts and documents) and extract EVERY piece of information that will be useful for the subsequent specialist agents.

**IMPORTANT**: You will receive PRE-PROCESSED content from the startup's submitted files:
- **Video/Audio Transcripts**: Speech-to-text transcriptions of all video and audio files
- **Document Text**: Extracted text from all document files (PDFs, presentations, etc.)

You MUST analyze this content comprehensively and extract ALL information. You **SHOULD NOT** take any info from the startup_info other than transcripts and document text in the state - focus ONLY on the provided transcripts and document text.

**YOUR ANALYSIS MUST INCLUDE**:

**1. TRANSCRIPT ANALYSIS** (from video/audio files):
- Analyze EVERYTHING said in the transcripts
- Identify key speakers and their statements (if mentioned)
- Capture all claims, statements, and assertions made
- Extract all metrics, numbers, and data points mentioned
- Note important quotes and specific claims
- Identify the context and flow of the pitch/presentation

**2. DOCUMENT TEXT ANALYSIS** (from uploaded documents):
- Read and summarize ALL content in the extracted text
- Extract all facts, claims, and data points
- Note all sections, headings, and topics covered
- Capture all metrics, financials, and quantitative data
- Extract all information about team, product, market, and traction
- Identify structured data like tables, lists, and charts (if described in text)

**3. CONSOLIDATED EXTRACTION**:
After analyzing all transcripts and document text, you MUST categorize and consolidate ALL information into these categories:

- **all_facts_and_claims**: Every factual statement and claim made across all content
- **all_metrics_and_data**: Every number, metric, percentage, dollar amount, growth rate, user count, etc.
- **all_team_information**: Everything about founders, team members, advisors, experience, background, roles
- **all_product_information**: Everything about the product, features, technology, roadmap, IP, development stage
- **all_market_information**: Everything about market size, customers, segments, TAM/SAM/SOM, opportunity
- **all_traction_information**: Everything about revenue, users, growth, customers, partnerships, milestones
- **all_competitive_information**: Everything about competitors, differentiation, competitive advantages, market position

**CRITICAL INSTRUCTIONS**:
1. Be EXHAUSTIVE - extract EVERY piece of information, no matter how small
2. Be SPECIFIC - include actual numbers, names, dates, and details exactly as stated
3. Be ACCURATE - preserve quotes and data exactly as transcribed/extracted
4. Be ORGANIZED - categorize information properly for downstream agents
5. If multiple transcripts/documents are provided, analyze ALL of them thoroughly
6. Cross-reference information across different sources when possible
7. Your output will be used by all subsequent agents, so completeness is critical

**HANDLING TRANSCRIPTION QUALITY**:
- If transcripts are unclear or incomplete, note this in your analysis
- Extract what you can and flag any ambiguous information
- Don't make assumptions about unclear transcriptions

**OUTPUT REQUIREMENTS**:
- Provide comprehensive analysis using the FilesAnalysisSummary model
- Ensure all lists are populated with specific, actionable information
- Include direct quotes when important claims are made
- Set confidence_level based on content quality and completeness
- If no content is provided, indicate this clearly in the executive_summary

The subsequent agents (Team, Market, Product, Competition, Synthesis) will rely heavily on your analysis, so be thorough!
"""


files_analysis_agent = LlmAgent(
    model=config.specialist_model,
    name="files_analysis_agent",
    description="Analyzes all submitted files (video, audio, documents) and extracts comprehensive information for downstream agents",
    instruction=f"""
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Startup Information: {{startup_info}}
    
    {files_analysis_prompt}
    """,
    output_schema=FilesAnalysisSummary,
    output_key="files_analysis",
    after_agent_callback=[
        track_agent_execution_callback,
        store_agent_analysis_callback,
    ],
)
