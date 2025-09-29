"""Startup routes for Project Minerva API."""

import uuid
import logging
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends

from ..models import StartupSubmissionRequest
from ..utils import get_current_user_from_token, safe_json_loads
from ..services import bq_client, analysis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/startups", tags=["startups"])

def serialize_for_bigquery(obj):
    """Recursively serialize objects for BigQuery, converting datetime to ISO strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_for_bigquery(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_bigquery(item) for item in obj]
    else:
        return obj

@router.post("")
async def create_startup(
    startup_data: StartupSubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Create a new startup submission."""
    try:
        startup_id = str(uuid.uuid4())
        submission_timestamp = datetime.utcnow()
        
        # Convert Pydantic objects to dictionaries for JSON serialization
        startup_dict = startup_data.dict()
        bigquery_success = False
        
        if bq_client and bq_client.is_available:
            # Store in BigQuery - serialize all datetime objects and convert arrays to JSON strings
            # Use the same schema as integrated_server.py
            startup_row = {
                "id": startup_id,
                "company_name": startup_dict["company_info"].get("name", ""),
                "description": startup_dict["company_info"].get("description", ""),
                "industry": startup_dict["company_info"].get("industry", "other"),
                "funding_stage": startup_dict["company_info"].get("funding_stage", "pre_seed"),
                "location": startup_dict["company_info"].get("location", ""),
                "website_url": startup_dict["company_info"].get("website_url"),
                "founded_date": serialize_for_bigquery(startup_dict["company_info"].get("founded_date")),
                "employee_count": startup_dict["company_info"].get("employee_count"),
                "revenue_run_rate": startup_dict["company_info"].get("revenue_run_rate"),
                "funding_raised": startup_dict["company_info"].get("funding_raised"),
                "funding_seeking": startup_dict["company_info"].get("funding_seeking"),
                "founders": json.dumps(serialize_for_bigquery(startup_dict["founders"])),
                "documents": json.dumps(serialize_for_bigquery(startup_dict["documents"])),
                "metadata": json.dumps(serialize_for_bigquery(startup_dict.get("metadata", {}))),
                "submitted_by": current_user["id"],
                "submission_timestamp": submission_timestamp.isoformat(),
                "last_updated": submission_timestamp.isoformat(),
                "status": "submitted"
            }
            
            
            try:
                bq_client.insert_rows("startups", [startup_row])
                logger.info(f"Startup {startup_id} stored in BigQuery")
                bigquery_success = True
            except RuntimeError as e:
                if "BigQuery access temporarily restricted" in str(e):
                    logger.warning(f"BigQuery access restricted, continuing without persistence: {e}")
                else:
                    raise
        
        # Start AI analysis in background (regardless of BigQuery status)
        analysis_id = str(uuid.uuid4())
        background_tasks.add_task(
            analysis_service.start_ai_analysis,
            startup_id,
            analysis_id,
            startup_dict
        )
        
        # Return appropriate response based on BigQuery status
        if bigquery_success:
            return {
                "id": startup_id,
                "message": "Startup submitted successfully",
                "analysis_id": analysis_id,
                "status": "submitted"
            }
        else:
            return {
                "id": startup_id,
                "message": "Startup submitted successfully (BigQuery unavailable)",
                "analysis_id": analysis_id,
                "status": "submitted"
            }
            
    except Exception as e:
        logger.error(f"Error creating startup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create startup: {str(e)}"
        )

@router.get("")
async def list_startups(
    page: int = 1,
    per_page: int = 20,
    search: str = None,
    industry: str = None,
    funding_stage: str = None,
    status: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """List startups from BigQuery with role-based filtering."""
    if not bq_client or not bq_client.is_available:
        return {
            "data": [],
            "total": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0
        }
    
    try:
        # Build WHERE clause based on role and filters
        where_conditions = []
        
        if current_user["role"] == "founder":
            # Founder sees only their own submissions
            where_conditions.append(f"submitted_by = '{current_user['id']}'")
        
        # Add search filter
        if search:
            search_escaped = search.replace("'", "''")
            where_conditions.append(f"(company_name LIKE '%{search_escaped}%' OR description LIKE '%{search_escaped}%')")
        
        # Add industry filter
        if industry:
            where_conditions.append(f"industry = '{industry}'")
        
        # Add funding stage filter
        if funding_stage:
            where_conditions.append(f"funding_stage = '{funding_stage}'")
        
        # Add status filter
        if status:
            where_conditions.append(f"status = '{status}'")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        sql = f"""
        SELECT s.*, 
               CASE WHEN a.startup_id IS NOT NULL THEN true ELSE false END as analysis_completed
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
        LEFT JOIN (
            SELECT DISTINCT startup_id 
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` 
            WHERE status = 'completed'
        ) a ON s.id = a.startup_id
        WHERE {where_clause}
        ORDER BY s.submission_timestamp DESC
        LIMIT {per_page} OFFSET {offset}
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
                    "location": row.get("location", ""),
                    "website_url": row.get("website_url"),
                    "founded_date": row.get("founded_date"),
                    "employee_count": row.get("employee_count"),
                    "revenue_run_rate": row.get("revenue_run_rate"),
                    "funding_raised": row.get("funding_raised"),
                    "funding_seeking": row.get("funding_seeking"),
                    **safe_json_loads(row.get("company_info"), {})
                },
                "founders": safe_json_loads(row.get("founders"), []),
                "documents": safe_json_loads(row.get("documents"), []),
                "metadata": safe_json_loads(row.get("metadata"), {}),
                "submission_timestamp": row["submission_timestamp"].isoformat(),
                "submitted_by": row["submitted_by"],
                "status": row["status"],
                "analysis_completed": bool(row.get("analysis_completed", False))
            }
            startups.append(startup)
        
        # Get total count for pagination
        count_sql = f"""
        SELECT COUNT(*) as total FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
        WHERE {where_clause}
        """
        count_results = bq_client.query(count_sql)
        total_count = list(count_results)[0]['total'] if count_results else 0
        
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
        
        return {
            "data": startups,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Error listing startups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list startups: {str(e)}"
        )

@router.get("/{startup_id}")
async def get_startup(startup_id: str, current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Get a specific startup from BigQuery."""
    if not bq_client or not bq_client.is_available:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found (BigQuery unavailable)"
        )
    
    try:
        # Role-based access control with analysis completion check
        if current_user["role"] == "founder":
            sql = f"""
            SELECT s.*, 
                   CASE WHEN a.startup_id IS NOT NULL THEN true ELSE false END as analysis_completed
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
            LEFT JOIN (
                SELECT DISTINCT startup_id 
                FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` 
                WHERE status = 'completed'
            ) a ON s.id = a.startup_id
            WHERE s.id = '{startup_id}' AND s.submitted_by = '{current_user["id"]}'
            """
        else:
            sql = f"""
            SELECT s.*, 
                   CASE WHEN a.startup_id IS NOT NULL THEN true ELSE false END as analysis_completed
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
            LEFT JOIN (
                SELECT DISTINCT startup_id 
                FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` 
                WHERE status = 'completed'
            ) a ON s.id = a.startup_id
            WHERE s.id = '{startup_id}'
            """
        
        results = list(bq_client.query(sql))
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Startup not found"
            )
        
        row = results[0]
        startup = {
            "id": row["id"],
            "company_info": {
                "name": row["company_name"],
                "description": row["description"],
                "industry": row["industry"],
                "funding_stage": row["funding_stage"],
                "location": row.get("location", ""),
                "website_url": row.get("website_url"),
                "founded_date": row.get("founded_date"),
                "employee_count": row.get("employee_count"),
                "revenue_run_rate": row.get("revenue_run_rate"),
                "funding_raised": row.get("funding_raised"),
                "funding_seeking": row.get("funding_seeking"),
                **safe_json_loads(row.get("company_info"), {})
            },
            "founders": safe_json_loads(row.get("founders"), []),
            "documents": safe_json_loads(row.get("documents"), []),
            "metadata": safe_json_loads(row.get("metadata"), {}),
            "submission_timestamp": row["submission_timestamp"].isoformat(),
            "submitted_by": row["submitted_by"],
            "status": row["status"],
            "analysis_completed": bool(row.get("analysis_completed", False))
        }
        
        return startup
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting startup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get startup: {str(e)}"
        )

@router.delete("/{startup_id}")
async def delete_startup(startup_id: str, current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """Delete a startup from BigQuery."""
    if not bq_client or not bq_client.is_available:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Startup not found (BigQuery unavailable)"
        )
    
    try:
        # Role-based access control - only founders can delete their own startups
        if current_user["role"] == "founder":
            sql = f"""
            DELETE FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE id = '{startup_id}' AND submitted_by = '{current_user["id"]}'
            """
        else:
            # Investors/analysts can delete any startup (admin function)
            sql = f"""
            DELETE FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE id = '{startup_id}'
            """
        
        query_job = bq_client.query(sql)
        
        # Check if any rows were affected
        if query_job.num_dml_affected_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Startup not found or access denied"
            )
        
        return {"message": "Startup deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting startup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete startup: {str(e)}"
        )
