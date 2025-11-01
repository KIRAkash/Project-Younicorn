"""Dashboard routes for Project Younicorn API."""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends

from ..utils import get_current_user_from_token
from ..services import bq_client
from ..services.file_content_cache_service import file_content_cache_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get dashboard statistics from BigQuery."""
    if not bq_client or not bq_client.is_available:
        return {
            "total_startups": 0,
            "total_analyses": 0,
            "pending_analyses": 0,
            "completed_analyses": 0,
            "average_score": 0.0,
            "recent_activity": []
        }
    
    try:
        # Role-based filtering
        startup_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            startup_filter = f"WHERE submitted_by = '{user_id}'"
        
        # Get startup statistics
        startup_sql = f"""
        SELECT COUNT(*) as total_startups
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        """
        
        startup_results = list(bq_client.query(startup_sql))
        total_startups = startup_results[0]["total_startups"] if startup_results else 0
        
        # Get analysis statistics
        analysis_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            analysis_filter = f"""
            WHERE a.startup_id IN (
                SELECT id FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
                WHERE submitted_by = '{user_id}'
            )
            """
        
        analysis_sql = f"""
        SELECT 
            COUNT(*) as total_analyses,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_analyses,
            SUM(CASE WHEN status IN ('running', 'pending') THEN 1 ELSE 0 END) as pending_analyses,
            AVG(CASE WHEN overall_score IS NOT NULL THEN overall_score ELSE NULL END) as average_score
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        WHERE is_latest = true {' AND ' + analysis_filter.replace('WHERE ', '') if analysis_filter else ''}
        """
        
        analysis_results = list(bq_client.query(analysis_sql))
        if analysis_results:
            result = analysis_results[0]
            total_analyses = result["total_analyses"] or 0
            completed_analyses = result["completed_analyses"] or 0
            pending_analyses = result["pending_analyses"] or 0
            average_score = float(result["average_score"]) if result["average_score"] else 0.0
        else:
            total_analyses = completed_analyses = pending_analyses = 0
            average_score = 0.0
        
        # Get recent activity
        recent_activity_sql = f"""
        SELECT 
            s.company_name,
            a.status,
            a.overall_score,
            a.investment_recommendation,
            a.started_at,
            a.completed_at
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        JOIN `{bq_client.project_id}.{bq_client.dataset_id}.startups` s ON a.startup_id = s.id
        WHERE a.is_latest = true {' AND ' + analysis_filter.replace('WHERE ', '').replace('a.startup_id', 's.id') if analysis_filter else ''}
        ORDER BY a.started_at DESC
        LIMIT 5
        """
        
        recent_results = bq_client.query(recent_activity_sql)
        recent_activity = []
        
        for row in recent_results:
            activity = {
                "company_name": row["company_name"],
                "status": row["status"],
                "overall_score": row.get("overall_score"),
                "investment_recommendation": row.get("investment_recommendation"),
                "started_at": row.get("started_at").isoformat() if row.get("started_at") else None,
                "completed_at": row.get("completed_at").isoformat() if row.get("completed_at") else None
            }
            recent_activity.append(activity)
        
        # Get recent submissions
        recent_submissions_sql = f"""
        SELECT 
            s.id,
            s.company_name,
            s.industry,
            s.funding_stage,
            s.status,
            s.submission_timestamp,
            s.logo_url,
            s.description,
            a.status as analysis_status,
            a.overall_score
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
        LEFT JOIN `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a ON s.id = a.startup_id AND a.is_latest = true
        {startup_filter}
        ORDER BY s.submission_timestamp DESC
        LIMIT 10
        """
        
        recent_submissions_results = bq_client.query(recent_submissions_sql)
        recent_submissions = []
        
        for row in recent_submissions_results:
            submission = {
                "id": row["id"],
                "company_info": {
                    "name": row.get("company_name", "Unknown"),
                    "industry": row.get("industry", "unknown"),
                    "funding_stage": row.get("funding_stage", "unknown"),
                    "logo_url": row.get("logo_url"),
                    "description": row.get("description", "")
                },
                "status": row["status"],
                "analysis_status": row.get("analysis_status"),
                "overall_score": row.get("overall_score"),
                "submission_timestamp": row.get("submission_timestamp").isoformat() if row.get("submission_timestamp") else None
            }
            recent_submissions.append(submission)
        
        # Get industry breakdown
        industry_sql = f"""
        SELECT 
            industry,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY industry
        ORDER BY count DESC
        LIMIT 10
        """
        
        industry_results = bq_client.query(industry_sql)
        industry_breakdown = []
        
        for row in industry_results:
            industry_breakdown.append({
                "name": row["industry"] or "unknown",
                "value": row["count"]
            })
        
        # Get funding stage breakdown
        funding_stage_sql = f"""
        SELECT 
            funding_stage,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY funding_stage
        ORDER BY count DESC
        LIMIT 10
        """
        
        funding_stage_results = bq_client.query(funding_stage_sql)
        funding_stage_breakdown = []
        
        for row in funding_stage_results:
            funding_stage_breakdown.append({
                "name": row["funding_stage"] or "unknown",
                "value": row["count"]
            })
        
        # Get product stage breakdown
        product_stage_sql = f"""
        SELECT 
            product_stage,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY product_stage
        ORDER BY count DESC
        LIMIT 10
        """
        
        product_stage_results = bq_client.query(product_stage_sql)
        product_stage_breakdown = []
        
        for row in product_stage_results:
            product_stage_breakdown.append({
                "name": row["product_stage"] or "unknown",
                "value": row["count"]
            })
        
        # Get company structure breakdown
        company_structure_sql = f"""
        SELECT 
            company_structure,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY company_structure
        ORDER BY count DESC
        LIMIT 10
        """
        
        company_structure_results = bq_client.query(company_structure_sql)
        company_structure_breakdown = []
        
        for row in company_structure_results:
            company_structure_breakdown.append({
                "name": row["company_structure"] or "unknown",
                "value": row["count"]
            })
        
        return {
            "total_startups": total_startups,
            "total_analyses": total_analyses,
            "pending_analysis": pending_analyses,
            "completed_analysis": completed_analyses,
            "avg_score": round(average_score, 2),
            "recent_submissions": recent_submissions,
            "industry_breakdown": industry_breakdown,
            "funding_stage_breakdown": funding_stage_breakdown,
            "product_stage_breakdown": product_stage_breakdown,
            "company_structure_breakdown": company_structure_breakdown,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.get("/core-stats")
async def get_core_stats(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get core dashboard statistics (fast - just counts)."""
    if not bq_client or not bq_client.is_available:
        return {
            "total_startups": 0,
            "completed_analysis": 0,
            "pending_analysis": 0
        }
    
    try:
        # Role-based filtering
        startup_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            startup_filter = f"WHERE submitted_by = '{user_id}'"
        
        # Get startup count
        startup_sql = f"""
        SELECT COUNT(*) as total_startups
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        """
        
        startup_results = list(bq_client.query(startup_sql))
        total_startups = startup_results[0]["total_startups"] if startup_results else 0
        
        # Get analysis counts
        analysis_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            analysis_filter = f"""
            AND a.startup_id IN (
                SELECT id FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
                WHERE submitted_by = '{user_id}'
            )
            """
        
        analysis_sql = f"""
        SELECT 
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_analyses,
            SUM(CASE WHEN status IN ('running', 'pending') THEN 1 ELSE 0 END) as pending_analyses
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        WHERE is_latest = true {analysis_filter}
        """
        
        analysis_results = list(bq_client.query(analysis_sql))
        if analysis_results:
            result = analysis_results[0]
            completed_analyses = result["completed_analyses"] or 0
            pending_analyses = result["pending_analyses"] or 0
        else:
            completed_analyses = pending_analyses = 0
        
        return {
            "total_startups": total_startups,
            "completed_analysis": completed_analyses,
            "pending_analysis": pending_analyses
        }
        
    except Exception as e:
        logger.error(f"Error getting core stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get core stats: {str(e)}"
        )

@router.get("/recent-startups")
async def get_recent_startups(
    limit: int = 5,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> List[Dict[str, Any]]:
    """Get recent startup submissions (medium speed - limited data)."""
    if not bq_client or not bq_client.is_available:
        return []
    
    try:
        # Role-based filtering
        startup_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            startup_filter = f"WHERE s.submitted_by = '{user_id}'"
        
        recent_submissions_sql = f"""
        SELECT 
            s.id,
            s.company_name,
            s.industry,
            s.funding_stage,
            s.status,
            s.submission_timestamp,
            s.logo_url,
            s.description,
            a.status as analysis_status,
            a.overall_score
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
        LEFT JOIN `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a ON s.id = a.startup_id AND a.is_latest = true
        {startup_filter}
        ORDER BY s.submission_timestamp DESC
        LIMIT {limit}
        """
        
        recent_submissions_results = bq_client.query(recent_submissions_sql)
        recent_submissions = []
        
        for row in recent_submissions_results:
            submission = {
                "id": row["id"],
                "company_info": {
                    "name": row.get("company_name", "Unknown"),
                    "industry": row.get("industry", "unknown"),
                    "funding_stage": row.get("funding_stage", "unknown"),
                    "logo_url": row.get("logo_url"),
                    "description": row.get("description", "")
                },
                "status": row["status"],
                "analysis_status": row.get("analysis_status"),
                "overall_score": row.get("overall_score"),
                "submission_timestamp": row.get("submission_timestamp").isoformat() if row.get("submission_timestamp") else None
            }
            recent_submissions.append(submission)
        
        return recent_submissions
        
    except Exception as e:
        logger.error(f"Error getting recent startups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent startups: {str(e)}"
        )

@router.get("/breakdowns")
async def get_breakdowns(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get breakdown statistics (slow - aggregations)."""
    if not bq_client or not bq_client.is_available:
        return {
            "industry_breakdown": [],
            "funding_stage_breakdown": [],
            "product_stage_breakdown": [],
            "company_structure_breakdown": []
        }
    
    try:
        # Role-based filtering
        startup_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            startup_filter = f"WHERE submitted_by = '{user_id}'"
        
        # Get industry breakdown
        industry_sql = f"""
        SELECT 
            industry,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY industry
        ORDER BY count DESC
        LIMIT 10
        """
        
        industry_results = bq_client.query(industry_sql)
        industry_breakdown = [{"name": row["industry"] or "unknown", "value": row["count"]} for row in industry_results]
        
        # Get funding stage breakdown
        funding_stage_sql = f"""
        SELECT 
            funding_stage,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY funding_stage
        ORDER BY count DESC
        LIMIT 10
        """
        
        funding_stage_results = bq_client.query(funding_stage_sql)
        funding_stage_breakdown = [{"name": row["funding_stage"] or "unknown", "value": row["count"]} for row in funding_stage_results]
        
        # Get product stage breakdown
        product_stage_sql = f"""
        SELECT 
            product_stage,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY product_stage
        ORDER BY count DESC
        LIMIT 10
        """
        
        product_stage_results = bq_client.query(product_stage_sql)
        product_stage_breakdown = [{"name": row["product_stage"] or "unknown", "value": row["count"]} for row in product_stage_results]
        
        # Get company structure breakdown
        company_structure_sql = f"""
        SELECT 
            company_structure,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        {startup_filter}
        GROUP BY company_structure
        ORDER BY count DESC
        LIMIT 10
        """
        
        company_structure_results = bq_client.query(company_structure_sql)
        company_structure_breakdown = [{"name": row["company_structure"] or "unknown", "value": row["count"]} for row in company_structure_results]
        
        return {
            "industry_breakdown": industry_breakdown,
            "funding_stage_breakdown": funding_stage_breakdown,
            "product_stage_breakdown": product_stage_breakdown,
            "company_structure_breakdown": company_structure_breakdown
        }
        
    except Exception as e:
        logger.error(f"Error getting breakdowns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get breakdowns: {str(e)}"
        )

@router.get("/activity")
async def get_dashboard_activity(
    limit: int = 8,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> List[Dict[str, Any]]:
    """Get recent dashboard activity."""
    if not bq_client or not bq_client.is_available:
        return []
    
    try:
        # Role-based filtering
        analysis_filter = ""
        if current_user["role"] == "founder":
            user_id = current_user.get('uid') or current_user.get('id')
            analysis_filter = f"""
            WHERE s.submitted_by = '{user_id}'
            """
        
        recent_activity_sql = f"""
        SELECT 
            s.company_name,
            a.status,
            a.overall_score,
            a.investment_recommendation,
            a.started_at,
            a.completed_at
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        JOIN `{bq_client.project_id}.{bq_client.dataset_id}.startups` s ON a.startup_id = s.id
        {analysis_filter}
        ORDER BY a.started_at DESC
        LIMIT {limit}
        """
        
        recent_results = bq_client.query(recent_activity_sql)
        recent_activity = []
        
        for row in recent_results:
            activity = {
                "company_name": row["company_name"],
                "status": row["status"],
                "overall_score": row.get("overall_score"),
                "investment_recommendation": row.get("investment_recommendation"),
                "started_at": row.get("started_at").isoformat() if row.get("started_at") else None,
                "completed_at": row.get("completed_at").isoformat() if row.get("completed_at") else None
            }
            recent_activity.append(activity)
        
        return recent_activity
        
    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity: {str(e)}"
        )

@router.get("/cache-stats")
async def get_cache_stats(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get file content cache statistics."""
    try:
        stats = file_content_cache_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "cache_stats": {}
        }
