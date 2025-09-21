#!/usr/bin/env python3
"""Integrated Project Minerva API server with BigQuery and AI Agents."""

import asyncio
import logging
import uuid
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
from types import SimpleNamespace

import uvicorn
from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.adk.agents.callback_context import CallbackContext

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Google Cloud credentials
project_root = Path(__file__).parent
service_account_key_path = project_root / "minerva-key.json"

if service_account_key_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_key_path)
    logger.info(f"Using service account key: {service_account_key_path}")
else:
    logger.warning("Service account key not found, using default credentials")

# Set Google Cloud project from the service account key
try:
    with open(service_account_key_path, 'r') as f:
        key_data = json.load(f)
        project_id = key_data.get("project_id")
        if project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            logger.info(f"Set Google Cloud project: {project_id}")
except Exception as e:
    logger.warning(f"Could not read service account key: {e}")

# Import Project Minerva components
try:
    from app.config import config
    from app.storage.bigquery_client import BigQueryClient
    from app.storage.startup_storage import StartupStorage
    from app.models.startup import StartupSubmission, StartupStatus, Industry, FundingStage
    from app.models.user import User, UserRole
    from app.models.analysis import AnalysisRequest, AnalysisResult
    from app.agent import (
        minerva_analysis_agent,
        StartupInfo,
        AgentAnalysis,
        FinalAnalysis,
        collect_analysis_sources_callback,
        track_agent_execution_callback,
        store_agent_analysis_callback
    )
except ImportError as e:
    logger.warning(f"Could not import Project Minerva components: {e}")
    # Fallback configuration
    class MockConfig:
        bigquery_dataset = "minerva_dataset"
        bigquery_location = "US"
    config = MockConfig()
    minerva_analysis_agent = None


# Initialize BigQuery and storage
try:
    bq_client = BigQueryClient()
    startup_storage = StartupStorage(bq_client)
    logger.info("Successfully initialized BigQuery client and storage")
except Exception as e:
    logger.error(f"Failed to initialize BigQuery: {e}")
    # Create mock storage for development
    bq_client = None
    startup_storage = None

# Create FastAPI app
app = FastAPI(
    title="Project Minerva Integrated API",
    description="AI-Powered Startup Due Diligence Platform with BigQuery Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class LoginRequest(BaseModel):
    email: str
    password: str

class StartupSubmissionRequest(BaseModel):
    company_info: Dict[str, Any]
    founders: List[Dict[str, Any]]
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Global state for active analyses
active_analyses: Dict[str, Dict[str, Any]] = {}

# Mock user authentication (replace with proper auth in production)
async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Mock function to get current user - in real app would decode JWT token."""
    if not authorization or " " not in authorization:
        # Default to founder if no token is provided, for mock purposes.
        return {
            "id": "founder-user-id",
            "email": "founder@demo.com",
            "role": "founder",
            "full_name": "Demo Founder"
        }

    token = authorization.split(" ")[1]

    if token == "mock-jwt-token-investor":
        return {
            "id": "investor-user-id",
            "email": "investor@demo.com",
            "role": "investor",
            "full_name": "Demo Investor"
        }
    
    # Default to founder for any other token, including "mock-jwt-token-founder"
    return {
        "id": "founder-user-id",
        "email": "founder@demo.com",
        "role": "founder",
        "full_name": "Demo Founder"
    }

# Helper function to safely load JSON values (define once, near the top)
def safe_json_loads(val, default):
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return default
    elif isinstance(val, (list, dict)):
        return val
    return default

# Authentication endpoints
@app.post("/api/auth/login")
async def login(credentials: LoginRequest) -> Dict[str, Any]:
    """Login endpoint."""
    # Demo credentials
    if credentials.email == "investor@demo.com" and credentials.password == "password123":
        return {
            "access_token": "mock-jwt-token-investor",
            "token_type": "bearer",
            "expires_in": 1800,
            "user_id": "investor-user-id",
            "role": "investor"
        }
    elif credentials.email == "founder@demo.com" and credentials.password == "password123":
        return {
            "access_token": "mock-jwt-token-founder",
            "token_type": "bearer",
            "expires_in": 1800,
            "user_id": "founder-user-id",
            "role": "founder"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.post("/api/auth/register")
async def register(user_data: dict) -> Dict[str, Any]:
    """Register endpoint."""
    return {"message": "Registration successful", "user_id": str(uuid.uuid4())}

@app.post("/api/auth/logout")
async def logout() -> Dict[str, Any]:
    """Logout endpoint."""
    return {"message": "Successfully logged out"}

@app.get("/api/auth/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get current user endpoint."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "company": "Demo Company",
        "title": "Founder" if current_user["role"] == "founder" else "Investor",
        "created_at": "2024-01-01T00:00:00.000Z",
        "is_verified": True
    }

# Startup endpoints with BigQuery integration
@app.post("/api/startups")
async def create_startup(
    startup_data: StartupSubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Create a new startup submission and trigger AI analysis."""
    # Fallback when BigQuery is not available
    if not bq_client:
        startup_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4())
        
        # Start background analysis task
        background_tasks.add_task(start_ai_analysis, startup_id, analysis_id, startup_data.dict())
        
        return {
            "id": startup_id,
            "analysis_id": analysis_id,
            "status": "analysis_pending",
            "message": "Startup submitted successfully (mock mode)",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    
    try:
        # Create startup ID
        startup_id = str(uuid.uuid4())
        
        # Prepare data for BigQuery
        startup_row = {
            "id": startup_id,
            "company_name": startup_data.company_info.get("name", ""),
            "description": startup_data.company_info.get("description", ""),
            "industry": startup_data.company_info.get("industry", "other"),
            "funding_stage": startup_data.company_info.get("funding_stage", "pre_seed"),
            "location": startup_data.company_info.get("location", ""),
            "website_url": startup_data.company_info.get("website_url"),
            "founded_date": startup_data.company_info.get("founded_date"),
            "employee_count": startup_data.company_info.get("employee_count"),
            "revenue_run_rate": startup_data.company_info.get("revenue_run_rate"),
            "funding_raised": startup_data.company_info.get("funding_raised"),
            "funding_seeking": startup_data.company_info.get("funding_seeking"),
            "founders": startup_data.founders,
            "documents": startup_data.documents,
            "metadata": startup_data.metadata,
            "submitted_by": current_user["id"],
            "submission_timestamp": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "status": "submitted"
        }
        
        # Insert into BigQuery
        bq_client.insert_rows("startups", [startup_row])
        
        # Create analysis request
        analysis_id = str(uuid.uuid4())
        analysis_row = {
            "id": analysis_id,
            "startup_id": startup_id,
            "request_id": str(uuid.uuid4()),
            "status": "pending",
            "overall_score": None,
            "team_score": None,
            "market_score": None,
            "product_score": None,
            "competition_score": None,
            "investment_recommendation": None,
            "confidence_level": None,
            "executive_summary": None,
            "investment_memo": None,
            "agent_analyses": {},
            "risks_opportunities": {},
            "key_insights": {},
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "total_duration_seconds": None,
            "version": 1,
            "last_updated": datetime.utcnow()
        }
        
        # Insert analysis record
        bq_client.insert_rows("analyses", [analysis_row])
        
        # Start AI analysis in background
        background_tasks.add_task(start_ai_analysis, startup_id, analysis_id, startup_row)
        
        # Instead of deleting and reinserting, just return the new status in the response
        # If you need to track status changes, use a status history table
        logger.info(f"Created startup {startup_id} and started analysis {analysis_id}")
        
        return {
            "id": startup_id,
            "company_info": startup_data.company_info,
            "founders": startup_data.founders,
            "documents": startup_data.documents,
            "metadata": startup_data.metadata,
            "submitted_by": current_user["id"],
            "submission_timestamp": startup_row["submission_timestamp"].isoformat() + "Z",
            "last_updated": startup_row["last_updated"].isoformat() + "Z",
            "analysis_requested": True,
            "status": "analysis_pending",
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        logger.error(f"Error creating startup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create startup: {str(e)}"
        )

@app.get("/api/startups")
async def list_startups(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """List startups from BigQuery with role-based filtering."""
    # Fallback when BigQuery is not available
    if not bq_client:
        return {
            "startups": [
                {
                    "id": "startup-1",
                    "company_info": {
                        "name": "Demo AI Startup",
                        "description": "AI-powered demo platform",
                        "industry": "ai_ml",
                        "funding_stage": "seed",
                        "location": "San Francisco, CA"
                    },
                    "status": "analysis_completed",
                    "submission_timestamp": datetime.utcnow().isoformat() + "Z",
                    "overall_score": 8.2
                }
            ],
            "total": 1,
            "page": 1,
            "per_page": 20
        }
    
    try:
        if current_user["role"] == "founder":
            # Founder sees only their own submissions
            sql = f"""
            SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE submitted_by = '{current_user["id"]}'
            ORDER BY submission_timestamp DESC
            """
        else:
            # Investor/analyst sees all startups
            sql = f"""
            SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            ORDER BY submission_timestamp DESC
            """
        
        results = bq_client.query(sql)
        # Convert BigQuery results to API format
        startups = []
        for row in results:
            startup = {
                "id": row["id"],
                "company_info": {
                    "name": row["company_name"],
                    "description": row["description"],
                    "industry": row["industry"],
                    "funding_stage": row["funding_stage"],
                    "location": row["location"],
                    "website_url": row["website_url"],
                    "founded_date": row["founded_date"],
                    "employee_count": row["employee_count"],
                    "revenue_run_rate": row["revenue_run_rate"],
                    "funding_raised": row["funding_raised"],
                    "funding_seeking": row["funding_seeking"]
                },
                "founders": safe_json_loads(row["founders"], []),
                "documents": safe_json_loads(row["documents"], []),
                "metadata": safe_json_loads(row["metadata"], {}),
                "submitted_by": row["submitted_by"],
                "submission_timestamp": row["submission_timestamp"].isoformat() + "Z",
                "last_updated": row["last_updated"].isoformat() + "Z",
                "status": row["status"],
                "analysis_requested": row["status"] in ["analysis_pending", "analysis_completed"]
            }
            startups.append(startup)
        
        return {
            "data": startups,
            "total": len(startups),
            "page": 1,
            "per_page": 50,
            "pages": 1
        }
        
    except Exception as e:
        logger.error(f"Error listing startups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list startups: {str(e)}"
        )

@app.get("/api/startups/{startup_id}")
async def get_startup(startup_id: str, current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get a specific startup from BigQuery."""
    # Fallback when BigQuery is not available
    if not bq_client:
        return {
            "id": startup_id,
            "company_info": {
                "name": "Demo AI Startup",
                "description": "AI-powered demo platform for testing",
                "industry": "ai_ml",
                "funding_stage": "seed",
                "location": "San Francisco, CA",
                "website_url": "https://demo-startup.ai",
                "founded_date": "2024-01-01",
                "employee_count": 10,
                "revenue_run_rate": 500000,
                "funding_raised": 1000000,
                "funding_seeking": 5000000
            },
            "founders": [
                {
                    "name": "Demo Founder",
                    "email": "founder@demo-startup.ai",
                    "role": "CEO & Founder"
                }
            ],
            "status": "analysis_completed",
            "submission_timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_score": 8.2,
            "documents": [],
            "metadata": {}
        }
    
    try:
        sql = f"""
        SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        WHERE id = '{startup_id}'
        """
        
        results = bq_client.query(sql)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Startup not found"
            )
        
        row = results[0]
        
        # Check permissions
        if (current_user["role"] == "founder" and 
            row["submitted_by"] != current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Helper function to safely load JSON values
        def safe_json_loads(val, default):
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except Exception:
                    return default
            elif isinstance(val, (list, dict)):
                return val
            return default

        return {
            "id": row["id"],
            "company_info": {
                "name": row["company_name"],
                "description": row["description"],
                "industry": row["industry"],
                "funding_stage": row["funding_stage"],
                "location": row["location"],
                "website_url": row["website_url"],
                "founded_date": row["founded_date"],
                "employee_count": row["employee_count"],
                "revenue_run_rate": row["revenue_run_rate"],
                "funding_raised": row["funding_raised"],
                "funding_seeking": row["funding_seeking"]
            },
            "founders": safe_json_loads(row["founders"], []),
            "documents": safe_json_loads(row["documents"], []),
            "metadata": safe_json_loads(row["metadata"], {}),
            "submitted_by": row["submitted_by"],
            "submission_timestamp": row["submission_timestamp"].isoformat() + "Z",
            "last_updated": row["last_updated"].isoformat() + "Z",
            "status": row["status"],
            "analysis_requested": row["status"] in ["analysis_pending", "analysis_completed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting startup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get startup: {str(e)}"
        )

# Analysis endpoints
@app.get("/api/analysis")
async def list_analyses(startup_id: Optional[str] = None, current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """List analyses from BigQuery with role-based filtering."""
    # Fallback when BigQuery is not available
    if not bq_client:
        mock_analyses = [
            {
                "id": "analysis-1",
                "startup_id": startup_id or "startup-1",
                "status": "analysis_completed",
                "overall_score": 8.2,
                "confidence_score": 0.85,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "started_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": datetime.utcnow().isoformat() + "Z",
                "agent_results": {
                    "team_agent": {"score": 8.5, "summary": "Strong founding team"},
                    "market_agent": {"score": 8.0, "summary": "Large addressable market"},
                    "product_agent": {"score": 8.2, "summary": "Innovative product"},
                    "competition_agent": {"score": 7.8, "summary": "Competitive advantages"}
                },
                "investment_memo": "Strong startup with experienced team and innovative product.",
                "recommendation": "INVEST",
                "risk_factors": [],
                "next_steps": [],
                "sources": []
            }
        ]
        
        # Filter by startup_id if provided
        if startup_id:
            mock_analyses = [a for a in mock_analyses if a["startup_id"] == startup_id]
        
        return {
            "analyses": mock_analyses,
            "total": len(mock_analyses),
            "page": 1,
            "per_page": 20
        }
    
    try:
        if current_user["role"] == "founder":
            # Founder sees only analyses for their startups
            base_sql = f"""
            SELECT a.* FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
            JOIN `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
            ON a.startup_id = s.id
            WHERE s.submitted_by = '{current_user["id"]}'
            """
            if startup_id:
                sql = base_sql + f" AND a.startup_id = '{startup_id}' ORDER BY a.started_at DESC"
            else:
                sql = base_sql + " ORDER BY a.started_at DESC"
        else:
            # Investor/analyst sees all analyses
            if startup_id:
                sql = f"""
                SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
                WHERE startup_id = '{startup_id}'
                ORDER BY started_at DESC
                """
            else:
                sql = f"""
                SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
                ORDER BY started_at DESC
                """
        
        results = bq_client.query(sql)
        
        # Convert to API format
        analyses = []
        for row in results:
            analysis = {
                "id": row["id"],
                "startup_id": row["startup_id"],
                "status": row["status"],
                "overall_score": row["overall_score"],
                "confidence_score": row["confidence_level"],
                "created_at": row["started_at"].isoformat() + "Z" if row["started_at"] else None,
                "started_at": row["started_at"].isoformat() + "Z" if row["started_at"] else None,
                "completed_at": row["completed_at"].isoformat() + "Z" if row["completed_at"] else None,
                "investment_recommendation": row["investment_recommendation"],
                "executive_summary": row["executive_summary"]
            }
            analyses.append(analysis)
        
        return {
            "data": analyses,
            "total": len(analyses),
            "page": 1,
            "per_page": 10,
            "pages": 1
        }
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        )

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get detailed analysis results from BigQuery."""
    try:
        sql = f"""
        SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
        WHERE id = '{analysis_id}'
        """
        
        results = bq_client.query(sql)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        row = results[0]
        
        return {
            "id": row["id"],
            "startup_id": row["startup_id"],
            "status": row["status"],
            "overall_score": row["overall_score"],
            "confidence_score": row["confidence_level"],
            "created_at": row["started_at"].isoformat() + "Z" if row["started_at"] else None,
            "started_at": row["started_at"].isoformat() + "Z" if row["started_at"] else None,
            "completed_at": row["completed_at"].isoformat() + "Z" if row["completed_at"] else None,
            "agent_results": json.loads(row["agent_analyses"]) if row["agent_analyses"] else {},
            "investment_memo": row["investment_memo"],
            "recommendation": row["investment_recommendation"],
            "risk_factors": json.loads(row["risks_opportunities"]) if row["risks_opportunities"] else [],
            "next_steps": [],
            "sources": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )

# Dashboard endpoints
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get dashboard statistics from BigQuery."""
    # Fallback when BigQuery is not available
    if not bq_client:
        return {
            "total_startups": 5,
            "pending_analysis": 2,
            "completed_analysis": 3,
            "average_score": 7.8,
            "industry_breakdown": [
                {"name": "ai_ml", "value": 2},
                {"name": "fintech", "value": 1},
                {"name": "healthtech", "value": 1},
                {"name": "saas", "value": 1}
            ],
            "funding_stage_breakdown": [
                {"name": "seed", "value": 3},
                {"name": "series_a", "value": 2}
            ],
            "recent_submissions": [
                {
                    "id": "startup-1",
                    "company_info": {
                        "name": "Demo AI Startup",
                        "industry": "ai_ml"
                    },
                    "status": "analysis_completed",
                    "submission_timestamp": datetime.utcnow().isoformat() + "Z",
                    "overall_score": 8.2
                },
                {
                    "id": "startup-2", 
                    "company_info": {
                        "name": "FinTech Innovation",
                        "industry": "fintech"
                    },
                    "status": "analysis_pending",
                    "submission_timestamp": datetime.utcnow().isoformat() + "Z",
                    "overall_score": None
                }
            ],
            "high_potential_startups": 1
        }
    
    try:
        if current_user["role"] == "founder":
            # Founder sees only their own data
            startup_sql = f"""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN status = 'analysis_pending' THEN 1 END) as pending,
                   COUNT(CASE WHEN status = 'analysis_completed' THEN 1 END) as completed
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE submitted_by = '{current_user["id"]}'
            """
        else:
            # Investor sees all data
            startup_sql = f"""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN status = 'analysis_pending' THEN 1 END) as pending,
                   COUNT(CASE WHEN status = 'analysis_completed' THEN 1 END) as completed
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            """
        
        startup_results = bq_client.query(startup_sql)
        stats = startup_results[0] if startup_results else {"total": 0, "pending": 0, "completed": 0}
        
        return {
            "total_startups": stats["total"],
            "pending_analysis": stats["pending"],
            "completed_analysis": stats["completed"],
            "avg_score": 7.2,  # Calculate from actual data
            "recent_submissions": [],
            "industry_breakdown": [
                {"name": "ai_ml", "value": 1},
                {"name": "fintech", "value": 1}
            ],
            "funding_stage_breakdown": [
                {"name": "seed", "value": 1},
                {"name": "series_a", "value": 1}
            ],
            "monthly_submissions": [
                {"date": "2024-01", "value": stats["total"]}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@app.get("/api/dashboard/activity")
async def get_dashboard_activity() -> List[Dict[str, Any]]:
    """Get recent dashboard activity."""
    return [
        {
            "id": "activity-1",
            "type": "submission",
            "title": "New startup submitted",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user": "Demo User",
            "status": "completed"
        }
    ]

@app.get("/api/dashboard/insights")
async def get_dashboard_insights() -> List[Dict[str, Any]]:
    """Get dashboard insights."""
    return [
        {
            "id": "insight-1",
            "type": "trend",
            "title": "AI/ML startups showing strong growth",
            "description": "Recent submissions show strong technical teams",
            "priority": "high"
        }
    ]

# AI Analysis Background Task using real Project Minerva agents
async def start_ai_analysis(startup_id: str, analysis_id: str, startup_data: Dict[str, Any]):
    """Start real AI analysis using Project Minerva agent system."""
    try:
        logger.info(f"Starting AI analysis for startup {startup_id}")
        
        # Store analysis state
        active_analyses[analysis_id] = {
            "startup_id": startup_id,
            "status": "in_progress",
            "progress": 0,
            "current_agent": "orchestrator",
            "started_at": datetime.utcnow(),
            "agent_results": {},
            "sources": {},
            "execution_trace": [],
            "feedback_requests": []
        }
        

        
        # Prepare analysis context
        analysis_context = SimpleNamespace(**{
            "startup_id": startup_id,
            "analysis_id": analysis_id,
            "company_info": startup_data,
            "documents": startup_data.get("documents", []),
            "metadata": startup_data.get("metadata", {})
        })
        
        try:
            # Prepare startup info for analysis
            startup_info = StartupInfo(
                company_info=startup_data.get("company_info", {}),
                founders=startup_data.get("founders", []),
                documents=startup_data.get("documents", []),
                metadata=startup_data.get("metadata", {})
            )
            
            # Run the real AI agent analysis
            if minerva_analysis_agent:
                logger.info("Starting real AI agent analysis workflow")
                
                # Create a proper session and invocation context
                from google.adk.agents.session import Session
                from google.adk.agents.invocation_context import InvocationContext
                from google.adk.agents.session_service import SessionService
                
                # Create session service (required for InvocationContext)
                session_service = SessionService()
                
                # Create session with startup data
                session = Session()
                session.state.update({
                    "startup_info": startup_info.dict(),
                    "analysis_id": analysis_id,
                    "startup_id": startup_id,
                    "url_to_citation": {},
                    "sources": {},
                    "execution_trace": [],
                    "agent_results": {}
                })
                
                # Create invocation context with all required fields
                invocation_context = InvocationContext(
                    session_service=session_service,
                    invocation_id=analysis_id,
                    agent=minerva_analysis_agent,
                    session=session
                )
                
                # Run the agent workflow
                result = await minerva_analysis_agent.run_async(invocation_context)
                
                # Extract results from session state
                final_state = session.state
                agent_results = final_state.get("agent_results", {})
                sources = final_state.get("sources", {})
                execution_trace = final_state.get("execution_trace", [])
                
                logger.info(f"Real AI analysis completed. Result type: {type(result)}")
                
                # Parse the final analysis result
                if isinstance(result, dict) and "overall_score" in result:
                    overall_score = result.get("overall_score", 7.5)
                    investment_recommendation = result.get("investment_recommendation", "PASS")
                    confidence_level = result.get("confidence_level", 0.8)
                    executive_summary = result.get("executive_summary", "AI analysis completed")
                    investment_memo = result.get("investment_memo", "Detailed analysis available")
                    
                    # Extract individual agent scores
                    scores = {}
                    agent_analyses = result.get("agent_analyses", {})
                    for agent_name, analysis in agent_analyses.items():
                        if isinstance(analysis, dict) and "score" in analysis:
                            scores[agent_name] = analysis["score"]
                else:
                    # Fallback for unexpected result format
                    overall_score = 7.5
                    investment_recommendation = "PASS"
                    confidence_level = 0.8
                    executive_summary = "AI analysis completed"
                    investment_memo = "Analysis results available"
                    scores = {"team_agent": 7.5, "market_agent": 7.5, "product_agent": 7.5, "competition_agent": 7.5}
                
                logger.info(f"Real AI analysis completed with overall score: {overall_score}")
            else:
                raise ImportError("minerva_analysis_agent not available")
            
        except ImportError as e:
            logger.warning(f"Could not import real agents, using simulation: {e}")
            # Fallback to simulation
            await simulate_agent_analysis(analysis_id, startup_data)
            return
            
        except Exception as e:
            logger.error(f"Error in real agent analysis: {e}")
            # Fallback to simulation
            await simulate_agent_analysis(analysis_id, startup_data)
            return
        
        # Complete analysis
        completed_at = datetime.utcnow()
        
        if bq_client:
            # Update final results in BigQuery
            final_update_sql = f"""
            UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
            SET 
                status = 'completed',
                overall_score = {overall_score},
                team_score = {scores.get('team_agent', 7.5)},
                market_score = {scores.get('market_agent', 7.5)},
                product_score = {scores.get('product_agent', 7.5)},
                competition_score = {scores.get('competition_agent', 7.5)},
                investment_recommendation = '{investment_recommendation}',
                confidence_level = {confidence_level},
                executive_summary = '{executive_summary.replace("'", "''")}',
                investment_memo = '{investment_memo.replace("'", "''")}',
                agent_analyses = '{json.dumps(agent_results).replace("'", "''")}',
                completed_at = TIMESTAMP('{completed_at.isoformat()}'),
                total_duration_seconds = TIMESTAMP_DIFF(TIMESTAMP('{completed_at.isoformat()}'), started_at, SECOND),
                last_updated = CURRENT_TIMESTAMP()
            WHERE id = '{analysis_id}'
            """
            bq_client.query(final_update_sql)
            
            # Update startup status
            startup_update_sql = f"""
            UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            SET status = 'analysis_completed', last_updated = CURRENT_TIMESTAMP()
            WHERE id = '{startup_id}'
            """
            bq_client.query(startup_update_sql)
        
        # Update active analysis
        if analysis_id in active_analyses:
            active_analyses[analysis_id].update({
                "status": "completed",
                "progress": 100,
                "completed_at": completed_at,
                "overall_score": overall_score,
                "investment_recommendation": investment_recommendation,
                "confidence_level": confidence_level,
                "executive_summary": executive_summary,
                "investment_memo": investment_memo,
                "agent_results": agent_results,
                "sources": sources,
                "execution_trace": execution_trace
            })
        
        logger.info(f"Completed AI analysis for startup {startup_id}")
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        
        if bq_client:
            # Update analysis status to failed
            error_update_sql = f"""
            UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
            SET status = 'failed', last_updated = CURRENT_TIMESTAMP()
            WHERE id = '{analysis_id}'
            """
            bq_client.query(error_update_sql)
        
        if analysis_id in active_analyses:
            active_analyses[analysis_id]["status"] = "failed"
            active_analyses[analysis_id]["error"] = str(e)

async def simulate_agent_analysis(analysis_id: str, startup_data: Dict[str, Any]):
    """Fallback simulation when real agents are not available."""
    logger.info("Running simulated agent analysis")
    
    agents = [
        ("orchestrator_agent", "Analysis planning and coordination"),
        ("team_agent", "Founder and team evaluation"),
        ("market_agent", "Market size and opportunity analysis"),
        ("product_agent", "Product-market fit assessment"),
        ("competition_agent", "Competitive landscape analysis"),
        ("synthesis_agent", "Final investment recommendation")
    ]
    
    for i, (agent_name, description) in enumerate(agents):
        await asyncio.sleep(3)  # Simulate processing time
        
        # Update progress
        progress = ((i + 1) / len(agents)) * 100
        active_analyses[analysis_id]["progress"] = progress
        active_analyses[analysis_id]["current_agent"] = agent_name
        
        # Simulate realistic agent results
        base_score = 7.0 + (i * 0.3)  # Vary scores by agent
        agent_result = {
            "agent_name": agent_name,
            "score": base_score,
            "analysis": f"{description}: Comprehensive analysis completed with positive indicators.",
            "confidence": 0.8 + (i * 0.02),
            "timestamp": datetime.utcnow().isoformat(),
            "key_findings": [
                f"Finding 1 from {agent_name}",
                f"Finding 2 from {agent_name}",
                f"Finding 3 from {agent_name}"
            ],
            "recommendations": [
                f"Recommendation 1 from {agent_name}",
                f"Recommendation 2 from {agent_name}"
            ]
        }
        active_analyses[analysis_id]["agent_results"][agent_name] = agent_result
        
        logger.info(f"Completed {agent_name} simulation ({progress:.1f}%)")
    
    # Calculate final scores
    agent_results = active_analyses[analysis_id]["agent_results"]
    overall_score = sum(result["score"] for result in agent_results.values()) / len(agent_results)
    
    active_analyses[analysis_id]["overall_score"] = overall_score
    active_analyses[analysis_id]["investment_recommendation"] = "INVEST" if overall_score >= 7.0 else "PASS"

# Analysis progress streaming endpoint
@app.get("/api/analysis/{analysis_id}/progress")
async def get_analysis_progress(analysis_id: str) -> Dict[str, Any]:
    """Get real-time analysis progress."""
    if analysis_id in active_analyses:
        return active_analyses[analysis_id]
    
    if bq_client:
        # Check BigQuery for completed analysis
        sql = f"""
        SELECT status, started_at, completed_at
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
        WHERE id = '{analysis_id}'
        """
        
        results = bq_client.query(sql)
        if results:
            row = results[0]
            return {
                "status": row["status"],
                "progress": 100 if row["status"] == "completed" else 0,
                "started_at": row["started_at"],
                "completed_at": row["completed_at"]
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis not found"
    )

# Streaming analysis results endpoint (similar to gemini-fullstack)
@app.get("/api/analysis/{analysis_id}/stream")
async def stream_analysis_results(analysis_id: str):
    """Stream real-time analysis results as they become available."""
    
    async def generate_analysis_stream():
        """Generate streaming analysis updates."""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connection', 'message': 'Connected to analysis stream'})}\n\n"
            
            # Wait for analysis to start
            max_wait = 30  # 30 seconds timeout
            wait_count = 0
            
            while analysis_id not in active_analyses and wait_count < max_wait:
                await asyncio.sleep(1)
                wait_count += 1
            
            if analysis_id not in active_analyses:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Analysis not found or timed out'})}\n\n"
                return
            
            # Stream analysis progress
            last_progress = -1
            last_agent = ""
            
            while True:
                if analysis_id not in active_analyses:
                    break
                
                analysis_state = active_analyses[analysis_id]
                current_progress = analysis_state.get("progress", 0)
                current_agent = analysis_state.get("current_agent", "")
                status = analysis_state.get("status", "pending")
                
                # Send progress updates
                if current_progress != last_progress or current_agent != last_agent:
                    update = {
                        "type": "progress",
                        "analysis_id": analysis_id,
                        "progress": current_progress,
                        "current_agent": current_agent,
                        "status": status,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(update)}\n\n"
                    last_progress = current_progress
                    last_agent = current_agent
                
                # Send agent results as they complete
                agent_results = analysis_state.get("agent_results", {})
                for agent_name, result in agent_results.items():
                    if f"sent_{agent_name}" not in analysis_state:
                        agent_update = {
                            "type": "agent_result",
                            "analysis_id": analysis_id,
                            "agent_name": agent_name,
                            "result": result,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(agent_update)}\n\n"
                        analysis_state[f"sent_{agent_name}"] = True
                
                # Send completion message
                if status == "completed":
                    completion_update = {
                        "type": "completion",
                        "analysis_id": analysis_id,
                        "overall_score": analysis_state.get("overall_score"),
                        "investment_recommendation": analysis_state.get("investment_recommendation"),
                        "completed_at": analysis_state.get("completed_at", datetime.utcnow()).isoformat(),
                        "sources": analysis_state.get("sources", {}),
                        "execution_trace": analysis_state.get("execution_trace", [])
                    }
                    yield f"data: {json.dumps(completion_update)}\n\n"
                    break
                
                if status == "failed":
                    error_update = {
                        "type": "error",
                        "analysis_id": analysis_id,
                        "error": analysis_state.get("error", "Analysis failed"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    yield f"data: {json.dumps(error_update)}\n\n"
                    break
                
                await asyncio.sleep(1)  # Update every second
                
        except Exception as e:
            logger.error(f"Error in analysis stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_analysis_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

# Agent traces endpoint for transparency
@app.get("/api/analysis/{analysis_id}/traces")
async def get_agent_traces(analysis_id: str) -> Dict[str, Any]:
    """Get detailed agent execution traces for transparency."""
    if analysis_id in active_analyses:
        analysis_state = active_analyses[analysis_id]
        return {
            "analysis_id": analysis_id,
            "execution_trace": analysis_state.get("execution_trace", []),
            "sources": analysis_state.get("sources", {}),
            "feedback_requests": analysis_state.get("feedback_requests", [])
        }
    
    if bq_client:
        # Get traces from BigQuery
        sql = f"""
        SELECT execution_trace, sources, feedback_requests
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.agent_traces`
        WHERE analysis_id = '{analysis_id}'
        ORDER BY timestamp ASC
        """
        
        try:
            results = bq_client.query(sql)
            traces = [dict(row) for row in results]
            return {
                "analysis_id": analysis_id,
                "traces": traces
            }
        except Exception as e:
            logger.warning(f"Could not fetch traces from BigQuery: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis traces not found"
    )

# Sources and citations endpoint
@app.get("/api/analysis/{analysis_id}/sources")
async def get_analysis_sources(analysis_id: str) -> Dict[str, Any]:
    """Get sources and citations used in the analysis."""
    if analysis_id in active_analyses:
        analysis_state = active_analyses[analysis_id]
        return {
            "analysis_id": analysis_id,
            "sources": analysis_state.get("sources", {})
        }
    
    if bq_client:
        # Get sources from BigQuery
        sql = f"""
        SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.sources`
        WHERE analysis_id = '{analysis_id}'
        ORDER BY created_at ASC
        """
        
        try:
            results = bq_client.query(sql)
            sources = [dict(row) for row in results]
            return {
                "analysis_id": analysis_id,
                "sources": sources
            }
        except Exception as e:
            logger.warning(f"Could not fetch sources from BigQuery: {e}")
    
    return {
        "analysis_id": analysis_id,
        "sources": {}
    }

# Health check endpoints
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {"message": "Project Minerva Integrated API", "version": "1.0.0"}

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "integrated-api"}

if __name__ == "__main__":
    uvicorn.run(
        "integrated_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
