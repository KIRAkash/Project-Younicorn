"""Analysis routes for Project Younicorn API."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json

from ..utils import get_current_user_from_token, safe_json_loads
from ..utils.firebase_auth import require_investor
from ..services import bq_client, active_analyses

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.get("")
async def list_analyses(
    startup_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_investor)
) -> Dict[str, Any]:
    """
    List analyses from BigQuery.
    
    Requires: Authorization header with Firebase ID token (investor role only)
    """
    if not bq_client or not bq_client.is_available:
        return {
            "data": [],
            "total": 0,
            "page": 1,
            "per_page": 20
        }
    
    try:
        # Build base query - explicitly select the individual analysis columns
        base_sql = f"""
        SELECT a.id, a.startup_id, a.status, a.overall_score, a.team_score, a.market_score, 
               a.product_score, a.competition_score, a.investment_recommendation, a.confidence_level,
               a.executive_summary, a.investment_memo, a.started_at, a.completed_at, a.total_duration_seconds,
               a.team_analysis, a.market_analysis, a.product_analysis, a.competition_analysis, a.synthesis_analysis,
               a.agent_analyses, a.version,
               s.company_name, s.submitted_by
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        LEFT JOIN `{bq_client.project_id}.{bq_client.dataset_id}.startups` s ON a.startup_id = s.id
        """
        
        # Add filters
        conditions = ["a.is_latest = true"]  # Always filter for latest analyses
        if startup_id:
            conditions.append(f"a.startup_id = '{startup_id}'")
        
        # Investors can see all analyses (no additional filtering needed)
        
        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)
        
        base_sql += " ORDER BY a.started_at DESC"
        
        logger.info(f"Executing analysis query: {base_sql}")
        logger.info(f"Current user: {current_user}")
        logger.info(f"Startup ID filter: {startup_id}")
        
        results = bq_client.query(base_sql)
        analyses = []
        
        for row in results:
            
            analysis = {
                "id": row["id"],
                "startup_id": row["startup_id"],
                "company_name": row.get("company_name", "Unknown"),
                "status": row["status"],
                "overall_score": row.get("overall_score"),
                "team_score": row.get("team_score"),
                "market_score": row.get("market_score"),
                "product_score": row.get("product_score"),
                "competition_score": row.get("competition_score"),
                "investment_recommendation": row.get("investment_recommendation"),
                "confidence_level": row.get("confidence_level"),
                "executive_summary": row.get("executive_summary"),
                "investment_memo": row.get("investment_memo"),
                # Individual analysis columns (structured Pydantic schemas)
                "team_analysis": safe_json_loads(row.get("team_analysis"), None),
                "market_analysis": safe_json_loads(row.get("market_analysis"), None),
                "product_analysis": safe_json_loads(row.get("product_analysis"), None),
                "competition_analysis": safe_json_loads(row.get("competition_analysis"), None),
                "synthesis_analysis": safe_json_loads(row.get("synthesis_analysis"), None),
                "started_at": row.get("started_at").isoformat() if row.get("started_at") else None,
                "completed_at": row.get("completed_at").isoformat() if row.get("completed_at") else None,
                "total_duration_seconds": row.get("total_duration_seconds")
            }
            analyses.append(analysis)
        
        logger.info(f"Found {len(analyses)} analyses for startup {startup_id}")
        
        return {
            "data": analyses,
            "total": len(analyses),
            "page": 1,
            "per_page": 20
        }
        
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        )

@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(require_investor)
) -> Dict[str, Any]:
    """
    Get detailed analysis results from BigQuery.
    
    Requires: Authorization header with Firebase ID token (investor role only)
    """
    try:
        sql = f"""
        SELECT * FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
        WHERE id = '{analysis_id}'
        """
        
        results = list(bq_client.query(sql))
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        row = results[0]
        analysis = {
            "id": row["id"],
            "startup_id": row["startup_id"],
            "status": row["status"],
            "overall_score": row.get("overall_score"),
            "team_score": row.get("team_score"),
            "market_score": row.get("market_score"),
            "product_score": row.get("product_score"),
            "competition_score": row.get("competition_score"),
            "investment_recommendation": row.get("investment_recommendation"),
            "confidence_level": row.get("confidence_level"),
            "executive_summary": row.get("executive_summary"),
            "investment_memo": row.get("investment_memo"),
            # Individual analysis columns (structured Pydantic schemas)
            "team_analysis": safe_json_loads(row.get("team_analysis"), None),
            "market_analysis": safe_json_loads(row.get("market_analysis"), None),
            "product_analysis": safe_json_loads(row.get("product_analysis"), None),
            "competition_analysis": safe_json_loads(row.get("competition_analysis"), None),
            "synthesis_analysis": safe_json_loads(row.get("synthesis_analysis"), None),
            "started_at": row.get("started_at").isoformat() if row.get("started_at") else None,
            "completed_at": row.get("completed_at").isoformat() if row.get("completed_at") else None,
            "total_duration_seconds": row.get("total_duration_seconds"),
            "version": row.get("version", 1)
        }
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )

@router.get("/{analysis_id}/progress")
async def get_analysis_progress(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(require_investor)
) -> Dict[str, Any]:
    """
    Get real-time analysis progress.
    
    Requires: Authorization header with Firebase ID token (investor role only)
    """
    if analysis_id in active_analyses:
        return active_analyses[analysis_id]
    
    # Check BigQuery for completed analysis
    if bq_client and bq_client.is_available:
        try:
            sql = f"""
            SELECT status, overall_score, investment_recommendation, confidence_level
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
            WHERE id = '{analysis_id}'
            """
            
            results = list(bq_client.query(sql))
            if results:
                row = results[0]
                return {
                    "id": analysis_id,
                    "status": row["status"],
                    "progress": 100 if row["status"] == "completed" else 0,
                    "overall_score": row.get("overall_score"),
                    "investment_recommendation": row.get("investment_recommendation"),
                    "confidence_level": row.get("confidence_level")
                }
        except Exception as e:
            logger.warning(f"Could not fetch analysis from BigQuery: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis not found"
    )

