from pydantic import BaseModel, Field
from typing import List, Dict, Any

from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
from .team_agent import team_agent
from .market_agent import market_agent
from .product_agent import product_agent
from .competition_agent import competition_agent

# --- Input and Output Schemas ---

class StartupInfo(BaseModel):
    """The initial startup information that kicks off the analysis."""
    company_info: Dict[str, Any] = Field(description="General information about the company.")
    founders: List[Dict[str, Any]] = Field(description="Information about the founders.")
    documents: List[Dict[str, Any]] = Field(description="A list of documents provided by the startup.")
    metadata: Dict[str, Any] = Field(description="Additional metadata about the startup.")

class SpecialistAnalysis(BaseModel):
    """Represents the analysis output of a single specialist agent."""
    agent_name: str = Field(description="The name of the agent that produced this analysis.")
    score: float = Field(description="The score assigned by the agent, from 0.0 to 10.0.")
    summary: str = Field(description="A concise summary of the agent's findings.")
    detailed_analysis: str = Field(description="The full, detailed analysis from the agent.")
    key_findings: List[str] = Field(description="A list of the most important findings.")

class FinalAnalysis(BaseModel):
    """Represents the final, synthesized analysis from all agents."""
    overall_score: float = Field(description="The final, weighted score for the startup.")
    investment_recommendation: str = Field(description="The final investment recommendation (e.g., INVEST, PASS).")
    executive_summary: str = Field(description="A high-level executive summary of the entire analysis.")
    agent_analyses: Dict[str, SpecialistAnalysis] = Field(description="A dictionary of all the individual agent analyses.")

# --- Agent Definitions ---

# Set the output schema for all specialist agents
team_agent.output_schema = SpecialistAnalysis
market_agent.output_schema = SpecialistAnalysis
product_agent.output_schema = SpecialistAnalysis
competition_agent.output_schema = SpecialistAnalysis

# Define the parallel execution of the specialist agents
parallel_analysis = ParallelAgent(
    sub_agents=[
        team_agent,
        market_agent,
        product_agent,
        competition_agent,
    ],
    name="parallel_specialist_analysis"
)

# Define the synthesis agent that collates the parallel results
synthesis_agent = LlmAgent(
    name="synthesis_agent",
    description="Synthesizes the analyses from all specialist agents into a final report.",
    instruction="""
    You are the final decision-maker. Your task is to synthesize the analyses from the team, market, product, and competition agents into a single, coherent, and final report.

    You will receive the structured output from each of the specialist agents. Your final output must be a single JSON object that conforms to the `FinalAnalysis` schema.
    """,
    output_schema=FinalAnalysis,
)

# Define the main sequential workflow
analysis_workflow = SequentialAgent(
    sub_agents=[
        parallel_analysis,
        synthesis_agent,
    ],
    name="startup_analysis_workflow"
)
