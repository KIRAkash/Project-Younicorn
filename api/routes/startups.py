"""Startup routes for Project Younicorn API."""

import uuid
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks

from ..models import StartupSubmissionRequest
from ..utils import get_current_user_from_token, safe_json_loads
from ..services import bq_client, analysis_service, gcs_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/startups", tags=["startups"])

# Thread pool for running analysis without blocking other requests
# max_workers=5 allows 5 concurrent analyses
# Adjust based on expected concurrent users and available resources
analysis_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="analysis")

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
        
        # Upload files to GCS
        gcs_files_list = []
        if gcs_storage.is_available:
            # Upload documents from base64
            for doc in startup_data.documents:
                if doc.data:
                    # Validate file size (50MB limit)
                    if doc.size and doc.size > 50 * 1024 * 1024:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File {doc.filename} exceeds 50MB limit"
                        )
                    
                    destination_path = f"startups/{startup_id}/documents/{doc.filename}"
                    gcs_path = gcs_storage.upload_base64_file(
                        doc.data,
                        destination_path,
                        doc.content_type,
                        metadata={
                            "startup_id": startup_id,
                            "uploaded_by": current_user.get('uid') or current_user.get('id'),
                            "upload_timestamp": submission_timestamp.isoformat()
                        }
                    )
                    
                    if gcs_path:
                        gcs_files_list.append({
                            "filename": doc.filename,
                            "gcs_path": gcs_path,
                            "content_type": doc.content_type,
                            "size": doc.size or 0,
                            "file_type": "document"
                        })
                        logger.info(f"Uploaded document {doc.filename} to {gcs_path}")
            
            # Add any pre-uploaded GCS files
            for gcs_file in startup_data.gcs_files:
                gcs_files_list.append(gcs_file.dict())
        else:
            logger.warning("GCS storage not available, files will not be persisted")
        
        if bq_client and bq_client.is_available:
            # Store in BigQuery with comprehensive fields
            company_info = startup_dict["company_info"]
            startup_row = {
                # Basic Info
                "id": startup_id,
                "company_name": company_info.get("name", ""),
                "description": company_info.get("description", ""),
                "industry": company_info.get("industry", "other"),
                "funding_stage": company_info.get("funding_stage", "pre_seed"),
                "location": company_info.get("location", ""),
                "website_url": company_info.get("website_url"),
                "logo_url": company_info.get("logo_url"),
                "logo_gcs_path": company_info.get("logo_gcs_path"),
                "founded_date": serialize_for_bigquery(company_info.get("founded_date")),
                "employee_count": company_info.get("employee_count"),
                
                # Product & Technology (Point 1)
                "product_stage": company_info.get("product_stage", "idea"),
                "technology_stack": company_info.get("technology_stack"),
                "ip_patents": company_info.get("ip_patents"),
                "development_timeline": company_info.get("development_timeline"),
                "product_roadmap": company_info.get("product_roadmap"),
                
                # Market & Customer (Point 2)
                "target_customer_profile": company_info.get("target_customer_profile"),
                "customer_acquisition_cost": company_info.get("customer_acquisition_cost"),
                "lifetime_value": company_info.get("lifetime_value"),
                "current_customer_count": company_info.get("current_customer_count"),
                "customer_retention_rate": company_info.get("customer_retention_rate"),
                "geographic_markets": company_info.get("geographic_markets"),
                "go_to_market_strategy": company_info.get("go_to_market_strategy"),
                
                # Traction & Metrics (Point 3)
                "monthly_recurring_revenue": company_info.get("monthly_recurring_revenue"),
                "annual_recurring_revenue": company_info.get("annual_recurring_revenue"),
                "revenue_growth_rate": company_info.get("revenue_growth_rate"),
                "user_growth_rate": company_info.get("user_growth_rate"),
                "burn_rate": company_info.get("burn_rate"),
                "runway_months": company_info.get("runway_months"),
                "key_performance_indicators": company_info.get("key_performance_indicators"),
                
                # Financial Details (Point 6)
                "revenue_run_rate": company_info.get("revenue_run_rate"),
                "funding_raised": company_info.get("funding_raised"),
                "funding_seeking": company_info.get("funding_seeking"),
                "previous_funding_rounds": company_info.get("previous_funding_rounds"),
                "current_investors": company_info.get("current_investors"),
                "use_of_funds": company_info.get("use_of_funds"),
                "profitability_timeline": company_info.get("profitability_timeline"),
                "unit_economics": company_info.get("unit_economics"),
                
                # Legal & Compliance (Point 8)
                "company_structure": company_info.get("company_structure", "private_limited"),
                "incorporation_location": company_info.get("incorporation_location", "India"),
                "regulatory_requirements": company_info.get("regulatory_requirements"),
                "legal_issues": company_info.get("legal_issues"),
                
                # Vision & Strategy (Point 9)
                "mission_statement": company_info.get("mission_statement"),
                "five_year_vision": company_info.get("five_year_vision"),
                "exit_strategy": company_info.get("exit_strategy"),
                "social_impact": company_info.get("social_impact"),
                
                # JSON Fields
                "submission_type": startup_dict.get("submission_type", "form"),
                "founders": json.dumps(serialize_for_bigquery(startup_dict["founders"])),
                # Don't store document data (base64) - only metadata. Files are in GCS.
                "documents": json.dumps([{
                    "filename": doc.get("filename"),
                    "content_type": doc.get("content_type"),
                    "size": doc.get("size"),
                    "document_type": doc.get("document_type")
                } for doc in startup_dict.get("documents", [])]),
                "gcs_files": json.dumps(gcs_files_list),  # Store GCS file references
                "metadata": json.dumps(serialize_for_bigquery(startup_dict.get("metadata", {}))),
                "company_info": json.dumps(serialize_for_bigquery(company_info)),
                
                # System Fields
                "submitted_by": current_user.get('uid') or current_user.get('id'),
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
        
        # Pass GCS files to analysis (videos, audio, documents)
        # The gcs_files_list contains all uploaded files with their GCS URIs
        # Run analysis in thread pool to avoid blocking other API requests
        # This allows other endpoints to respond while analysis runs
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            analysis_executor,
            lambda: asyncio.run(analysis_service.start_ai_analysis(
                startup_id,
                analysis_id,
                startup_dict,
                gcs_files_list if gcs_files_list else None
            ))
        )
        logger.info(f"Started background analysis in thread pool for startup {startup_id} with analysis {analysis_id}")
        
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
            user_id = current_user.get('uid') or current_user.get('id')
            where_conditions.append(f"submitted_by = '{user_id}'")
        
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
            WHERE status = 'completed' AND is_latest = true
        ) a ON s.id = a.startup_id
        WHERE {where_clause}
        ORDER BY s.submission_timestamp DESC
        LIMIT {per_page} OFFSET {offset}
        """
        
        logger.info(f"Executing query: {sql}")
        results = list(bq_client.query(sql))  # Convert to list to avoid hanging
        logger.info(f"Query returned {len(results)} results")
        
        # Convert BigQuery results to API format
        startups = []
        for row in results:
            # Handle timestamp - could be datetime or string
            submission_ts = row["submission_timestamp"]
            if hasattr(submission_ts, 'isoformat'):
                submission_ts = submission_ts.isoformat()
            elif not isinstance(submission_ts, str):
                submission_ts = str(submission_ts)
            
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
                "submission_timestamp": submission_ts,
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
                WHERE status = 'completed' AND is_latest = true
            ) a ON s.id = a.startup_id
            WHERE s.id = '{startup_id}' AND s.submitted_by = '{current_user.get("uid") or current_user.get("id")}'
            """
        else:
            sql = f"""
            SELECT s.*, 
                   CASE WHEN a.startup_id IS NOT NULL THEN true ELSE false END as analysis_completed
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups` s
            LEFT JOIN (
                SELECT DISTINCT startup_id 
                FROM `{bq_client.project_id}.{bq_client.dataset_id}.analyses` 
                WHERE status = 'completed' AND is_latest = true
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
        
        # Handle timestamp - could be datetime or string
        submission_ts = row["submission_timestamp"]
        if hasattr(submission_ts, 'isoformat'):
            submission_ts = submission_ts.isoformat()
        elif not isinstance(submission_ts, str):
            submission_ts = str(submission_ts)
        
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
            "submission_timestamp": submission_ts,
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
            WHERE id = '{startup_id}' AND submitted_by = '{current_user.get("uid") or current_user.get("id")}'
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
