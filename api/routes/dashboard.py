"""Dashboard routes for Project Minerva API."""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends

from ..utils import get_current_user_from_token
from ..services import bq_client

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
            startup_filter = f"WHERE submitted_by = '{current_user['id']}'"
        
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
            analysis_filter = f"""
            WHERE a.startup_id IN (
                SELECT id FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
                WHERE submitted_by = '{current_user['id']}'
            )
            """
        
        analysis_sql = f"""
        SELECT 
            COUNT(*) as total_analyses,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_analyses,
            SUM(CASE WHEN status IN ('running', 'pending') THEN 1 ELSE 0 END) as pending_analyses,
            AVG(CASE WHEN overall_score IS NOT NULL THEN overall_score ELSE NULL END) as average_score
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` a
        {analysis_filter}
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
        {analysis_filter.replace('a.startup_id', 's.id') if analysis_filter else ''}
        ORDER BY a.started_at DESC
        LIMIT 10
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
        
        return {
            "total_startups": total_startups,
            "total_analyses": total_analyses,
            "pending_analyses": pending_analyses,
            "completed_analyses": completed_analyses,
            "average_score": round(average_score, 2),
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.get("/activity")
async def get_dashboard_activity() -> List[Dict[str, Any]]:
    """Get recent dashboard activity."""
    return [
        {
            "id": "1",
            "type": "analysis_completed",
            "message": "Analysis completed for TechStart Inc.",
            "timestamp": "2024-01-15T10:30:00Z",
            "score": 8.2
        }
    ]

@router.get("/insights")
async def get_dashboard_insights() -> List[Dict[str, Any]]:
    """Get dashboard insights."""
    return [
        {
            "id": "1",
            "title": "Market Trends",
            "description": "AI/ML startups showing 15% higher success rates",
            "type": "trend"
        }
    ]
