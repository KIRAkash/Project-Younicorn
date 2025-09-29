"""Analysis routes for Project Minerva API."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json

from ..utils import get_current_user_from_token, safe_json_loads
from ..services import bq_client, active_analyses

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.get("")
async def list_analyses(startup_id: Optional[str] = None, current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """List analyses from BigQuery with role-based filtering."""
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
               a.agent_analyses, a.risks_opportunities, a.key_insights, a.version,
               s.company_name, s.submitted_by
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        LEFT JOIN `{bq_client.project_id}.{bq_client.dataset_id}.startups` s ON a.startup_id = s.id
        """
        
        # Add filters
        conditions = []
        if startup_id:
            conditions.append(f"a.startup_id = '{startup_id}'")
        
        if current_user["role"] == "founder":
            conditions.append(f"s.submitted_by = '{current_user['id']}'")
        
        if conditions:
            base_sql += " WHERE " + " AND ".join(conditions)
        
        base_sql += " ORDER BY a.started_at DESC"
        
        logger.info(f"Executing analysis query: {base_sql}")
        logger.info(f"Current user: {current_user}")
        logger.info(f"Startup ID filter: {startup_id}")
        
        results = bq_client.query(base_sql)
        analyses = []
        
        # Debug: Check what BigQuery is actually returning
        results_list = list(results)
        if results_list:
            sample_row = results_list[0]
            logger.info(f"BigQuery row keys: {list(sample_row.keys())}")
            logger.info(f"Raw team_analysis type: {type(sample_row.get('team_analysis'))}")
            logger.info(f"Raw team_analysis value (first 200 chars): {str(sample_row.get('team_analysis'))[:200]}")
            logger.info(f"Raw market_analysis type: {type(sample_row.get('market_analysis'))}")
            logger.info(f"Raw agent_analyses type: {type(sample_row.get('agent_analyses'))}")
        
        results = results_list
        
        for row in results:
            # Debug individual column parsing
            team_raw = row.get("team_analysis")
            team_parsed = safe_json_loads(team_raw, None)
            logger.info(f"team_analysis - raw type: {type(team_raw)}, parsed type: {type(team_parsed)}, is_null: {team_raw is None}")
            
            if team_raw and team_parsed is None:
                logger.error(f"Failed to parse team_analysis: {str(team_raw)[:100]}...")
            
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
                # Individual analysis columns from new BigQuery schema
                "team_analysis": safe_json_loads(row.get("team_analysis"), None),
                "market_analysis": safe_json_loads(row.get("market_analysis"), None),
                "product_analysis": safe_json_loads(row.get("product_analysis"), None),
                "competition_analysis": safe_json_loads(row.get("competition_analysis"), None),
                "synthesis_analysis": safe_json_loads(row.get("synthesis_analysis"), None),
                # Legacy field for backward compatibility
                "agent_analyses": safe_json_loads(row.get("agent_analyses"), {}),
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
async def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get detailed analysis results from BigQuery."""
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
            # Individual analysis columns from new BigQuery schema
            "team_analysis": safe_json_loads(row.get("team_analysis"), None),
            "market_analysis": safe_json_loads(row.get("market_analysis"), None),
            "product_analysis": safe_json_loads(row.get("product_analysis"), None),
            "competition_analysis": safe_json_loads(row.get("competition_analysis"), None),
            "synthesis_analysis": safe_json_loads(row.get("synthesis_analysis"), None),
            # Legacy fields for backward compatibility
            "agent_analyses": safe_json_loads(row.get("agent_analyses"), {}),
            "risks_opportunities": safe_json_loads(row.get("risks_opportunities"), {}),
            "key_insights": safe_json_loads(row.get("key_insights"), {}),
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
async def get_analysis_progress(analysis_id: str) -> Dict[str, Any]:
    """Get real-time analysis progress."""
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

@router.get("/{analysis_id}/stream")
async def stream_analysis_results(analysis_id: str):
    """Stream real-time analysis results as they become available."""
    
    async def generate_analysis_stream():
        """Generate SSE stream of analysis progress."""
        last_progress = -1
        max_iterations = 300  # 5 minutes max (300 * 1 second)
        iteration = 0
        
        while iteration < max_iterations:
            try:
                if analysis_id in active_analyses:
                    analysis_state = active_analyses[analysis_id]
                    current_progress = analysis_state.get("progress", 0)
                    
                    # Send update if progress changed
                    if current_progress != last_progress:
                        data = {
                            "progress": current_progress,
                            "status": analysis_state.get("status", "running"),
                            "current_step": analysis_state.get("current_step", "Processing"),
                            "overall_score": analysis_state.get("overall_score"),
                            "investment_recommendation": analysis_state.get("investment_recommendation")
                        }
                        
                        yield f"data: {json.dumps(data)}\n\n"
                        last_progress = current_progress
                    
                    # Check if analysis is complete
                    if analysis_state.get("status") in ["completed", "failed"]:
                        # Send final update
                        final_data = {
                            "progress": 100,
                            "status": analysis_state["status"],
                            "completed": True,
                            "overall_score": analysis_state.get("overall_score"),
                            "investment_recommendation": analysis_state.get("investment_recommendation"),
                            "confidence_level": analysis_state.get("confidence_level")
                        }
                        yield f"data: {json.dumps(final_data)}\n\n"
                        break
                else:
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
                                final_data = {
                                    "progress": 100,
                                    "status": row["status"],
                                    "completed": True,
                                    "overall_score": row.get("overall_score"),
                                    "investment_recommendation": row.get("investment_recommendation"),
                                    "confidence_level": row.get("confidence_level")
                                }
                                yield f"data: {json.dumps(final_data)}\n\n"
                                break
                        except Exception as e:
                            logger.warning(f"Could not fetch analysis from BigQuery: {e}")
                
                await asyncio.sleep(1)  # Wait 1 second before next check
                iteration += 1
                
            except Exception as e:
                logger.error(f"Error in analysis stream: {e}")
                error_data = {
                    "progress": 0,
                    "status": "error",
                    "error": str(e),
                    "completed": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                break
        
        # Send timeout if we reach max iterations
        if iteration >= max_iterations:
            timeout_data = {
                "progress": 0,
                "status": "timeout",
                "error": "Analysis timed out",
                "completed": True
            }
            yield f"data: {json.dumps(timeout_data)}\n\n"
    
    return StreamingResponse(
        generate_analysis_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/{analysis_id}/traces")
async def get_agent_traces(analysis_id: str) -> Dict[str, Any]:
    """Get detailed agent execution traces for transparency."""
    if analysis_id in active_analyses:
        analysis_state = active_analyses[analysis_id]
        return {
            "analysis_id": analysis_id,
            "traces": analysis_state.get("execution_trace", [])
        }
    
    if bq_client and bq_client.is_available:
        try:
            sql = f"""
            SELECT agent_analyses FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
            WHERE id = '{analysis_id}'
            """
            
            results = list(bq_client.query(sql))
            if results:
                row = results[0]
                agent_analyses = safe_json_loads(row.get("agent_analyses"), {})
                return {
                    "analysis_id": analysis_id,
                    "traces": agent_analyses
                }
        except Exception as e:
            logger.warning(f"Could not fetch traces from BigQuery: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis traces not found"
    )

@router.get("/{analysis_id}/sources")
async def get_analysis_sources(analysis_id: str) -> Dict[str, Any]:
    """Get sources and citations used in the analysis."""
    if analysis_id in active_analyses:
        analysis_state = active_analyses[analysis_id]
        return {
            "analysis_id": analysis_id,
            "sources": analysis_state.get("sources", {})
        }
    
    if bq_client and bq_client.is_available:
        # Get sources from BigQuery
        try:
            sql = f"""
            SELECT agent_analyses FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
            WHERE id = '{analysis_id}'
            """
            
            results = list(bq_client.query(sql))
            if results:
                row = results[0]
                agent_analyses = safe_json_loads(row.get("agent_analyses"), {})
                
                # Extract sources from agent analyses
                sources = {}
                for agent_name, agent_data in agent_analyses.items():
                    if isinstance(agent_data, list) and agent_data:
                        agent_result = agent_data[0]
                        if isinstance(agent_result, dict) and "sources" in agent_result:
                            sources[agent_name] = agent_result["sources"]
                
                return {
                    "analysis_id": analysis_id,
                    "sources": sources
                }
        except Exception as e:
            logger.warning(f"Could not fetch sources from BigQuery: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis sources not found"
    )
