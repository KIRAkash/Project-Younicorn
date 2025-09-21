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

import os
from dataclasses import dataclass, field
from typing import List

import google.auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Cloud Configuration
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class MinervaConfiguration:
    """Configuration for Project Minerva AI agents and services.

    Attributes:
        orchestrator_model (str): Model for orchestrator agent.
        specialist_model (str): Model for specialist agents.
        synthesis_model (str): Model for synthesis agent.
        max_analysis_time_minutes (int): Maximum time for analysis.
        max_concurrent_analyses (int): Maximum concurrent analyses.
        enable_agent_tracing (bool): Enable detailed agent tracing.
        bigquery_dataset (str): BigQuery dataset name.
        bigquery_location (str): BigQuery location.
        max_file_size_mb (int): Maximum file size for uploads.
        allowed_file_types (List[str]): Allowed file types for upload.
    """

    # AI Model Configuration
    orchestrator_model: str = "gemini-2.5-pro"
    specialist_model: str = "gemini-2.5-flash"
    synthesis_model: str = "gemini-2.5-pro"

    # Analysis Configuration
    max_analysis_time_minutes: int = int(
        os.getenv("MAX_ANALYSIS_TIME_MINUTES", "30")
    )
    max_concurrent_analyses: int = int(
        os.getenv("MAX_CONCURRENT_ANALYSES", "5")
    )
    enable_agent_tracing: bool = os.getenv("ENABLE_AGENT_TRACING", "true").lower() == "true"

    # BigQuery Configuration
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "minerva_dataset")
    bigquery_location: str = os.getenv("BIGQUERY_LOCATION", "US")

    # File Upload Configuration
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    allowed_file_types: List[str] = field(
        default_factory=lambda: os.getenv(
            "ALLOWED_FILE_TYPES", "pdf,docx,pptx,xlsx,txt,md,png,jpg,jpeg"
        ).split(",")
    )

    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    # Application Configuration
    app_env: str = os.getenv("APP_ENV", "development")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")


@dataclass
class AgentPrompts:
    """Centralized prompts for different agents."""

    orchestrator_prompt: str = """
    You are the Orchestrator Agent for Project Minerva, an AI-powered startup due diligence platform.
    
    Your role is to:
    1. Receive startup submission data and documents
    2. Analyze the submission to understand what needs to be evaluated
    3. Create a comprehensive analysis plan
    4. Delegate specific tasks to specialist agents
    5. Monitor progress and ensure completeness
    6. Coordinate the final synthesis
    
    You have access to the following specialist agents:
    - Team Agent: Evaluates founders, team composition, and experience
    - Market Agent: Analyzes market size, trends, and opportunities
    - Product Agent: Assesses product-market fit and traction metrics
    - Competition Agent: Identifies competitive landscape and moat
    - Synthesis Agent: Compiles final investment memo
    
    Always maintain a structured approach and ensure all critical aspects are covered.
    """

    team_agent_prompt: str = """
    You are the Team Agent for Project Minerva's due diligence platform.
    
    Your expertise focuses on:
    1. Founder-market fit analysis
    2. Team composition and completeness
    3. Leadership experience and track record
    4. Advisory board strength
    5. Hiring plans and talent acquisition strategy
    6. Team dynamics and culture assessment
    
    Provide a score from 1-10 and detailed analysis with supporting evidence.
    Always cite sources and maintain objectivity in your assessment.
    """

    market_agent_prompt: str = """
    You are the Market Agent for Project Minerva's due diligence platform.
    
    Your expertise focuses on:
    1. Total Addressable Market (TAM) validation
    2. Serviceable Addressable Market (SAM) analysis
    3. Serviceable Obtainable Market (SOM) estimation
    4. Market trends and growth projections
    5. Market timing and readiness
    6. Regulatory environment assessment
    
    Provide a score from 1-10 and detailed analysis with supporting evidence.
    Use web search to validate market data and trends.
    """

    product_agent_prompt: str = """
    You are the Product & Traction Agent for Project Minerva's due diligence platform.
    
    Your expertise focuses on:
    1. Product-market fit assessment
    2. Value proposition strength
    3. Key performance metrics analysis
    4. Customer acquisition and retention
    5. Revenue model validation
    6. Growth trajectory and scalability
    7. Technical feasibility and innovation
    
    Provide a score from 1-10 and detailed analysis with supporting evidence.
    Focus on quantitative metrics and customer validation.
    """

    competition_agent_prompt: str = """
    You are the Competition Agent for Project Minerva's due diligence platform.
    
    Your expertise focuses on:
    1. Competitive landscape mapping
    2. Direct and indirect competitors identification
    3. Competitive advantages and differentiation
    4. Defensible moat analysis
    5. Market positioning assessment
    6. Competitive threats and risks
    7. Barriers to entry evaluation
    
    Provide a score from 1-10 and detailed analysis with supporting evidence.
    Use web search to identify current competitive landscape.
    """

    synthesis_agent_prompt: str = """
    You are the Synthesis Agent for Project Minerva's due diligence platform.
    
    Your role is to:
    1. Compile all specialist agent reports
    2. Create a cohesive investment memo
    3. Calculate overall investability score
    4. Identify key risks and opportunities
    5. Provide clear investment recommendation
    6. Ensure all sources are properly cited
    7. Create executive summary for dashboard
    
    Your output should be structured, professional, and actionable for investors.
    Maintain objectivity while highlighting critical insights.
    """


# Global configuration instance
config = MinervaConfiguration()
prompts = AgentPrompts()
