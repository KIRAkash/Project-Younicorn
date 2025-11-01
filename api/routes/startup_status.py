"""API routes for startup status management."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from google.cloud import bigquery

from api.config.settings import settings
from api.utils.auth import get_current_user_from_token

router = APIRouter()

# Initialize BigQuery client
bq_client = bigquery.Client(project=settings.google_cloud_project)


class StatusUpdateRequest(BaseModel):
    """Request model for updating startup status."""
    status: str  # 'On Watch', 'Shortlist', 'Pass'


class NoteUpdateRequest(BaseModel):
    """Request model for updating investor note."""
    note: str


class StartupStatusResponse(BaseModel):
    """Response model for startup status."""
    startup_id: str
    investor_email: str
    status: str
    investor_note: Optional[str] = None
    status_updated_at: str
    note_updated_at: Optional[str] = None


@router.get("/api/startups/{startup_id}/status")
async def get_startup_status(
    startup_id: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get status for a specific startup and investor."""
    try:
        investor_email = current_user.get("email")
        
        query = f"""
            SELECT 
                startup_id,
                investor_email,
                status,
                investor_note,
                CAST(status_updated_at AS STRING) as status_updated_at,
                CAST(note_updated_at AS STRING) as note_updated_at
            FROM `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
            WHERE startup_id = @startup_id AND investor_email = @investor_email
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
            ]
        )
        
        query_job = bq_client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if not results:
            # Return default "New" status if no record exists
            return {
                "startup_id": startup_id,
                "investor_email": investor_email,
                "status": "New",
                "investor_note": None,
                "status_updated_at": None,
                "note_updated_at": None
            }
        
        row = results[0]
        return {
            "startup_id": row.startup_id,
            "investor_email": row.investor_email,
            "status": row.status,
            "investor_note": row.investor_note,
            "status_updated_at": row.status_updated_at,
            "note_updated_at": row.note_updated_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get startup status: {str(e)}")


@router.put("/api/startups/{startup_id}/status")
async def update_startup_status(
    startup_id: str,
    request: StatusUpdateRequest,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update status for a startup."""
    try:
        investor_email = current_user.get("email")
        now = datetime.utcnow().isoformat()
        
        # Check if record exists
        check_query = f"""
            SELECT COUNT(*) as count
            FROM `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
            WHERE startup_id = @startup_id AND investor_email = @investor_email
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
            ]
        )
        
        check_job = bq_client.query(check_query, job_config=job_config)
        count = list(check_job.result())[0].count
        
        if count > 0:
            # Update existing record
            update_query = f"""
                UPDATE `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
                SET 
                    status = @status,
                    status_updated_at = @now,
                    last_updated = @now
                WHERE startup_id = @startup_id AND investor_email = @investor_email
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                    bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
                    bigquery.ScalarQueryParameter("status", "STRING", request.status),
                    bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                ]
            )
            
            bq_client.query(update_query, job_config=job_config).result()
        else:
            # Insert new record
            insert_query = f"""
                INSERT INTO `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
                (startup_id, investor_email, status, status_updated_at, created_at, last_updated)
                VALUES (@startup_id, @investor_email, @status, @now, @now, @now)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                    bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
                    bigquery.ScalarQueryParameter("status", "STRING", request.status),
                    bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                ]
            )
            
            bq_client.query(insert_query, job_config=job_config).result()
        
        return {
            "success": True,
            "startup_id": startup_id,
            "status": request.status,
            "updated_at": now
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update startup status: {str(e)}")


@router.put("/api/startups/{startup_id}/note")
async def update_startup_note(
    startup_id: str,
    request: NoteUpdateRequest,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update investor note for a startup."""
    try:
        investor_email = current_user.get("email")
        now = datetime.utcnow().isoformat()
        
        # Check if record exists
        check_query = f"""
            SELECT COUNT(*) as count
            FROM `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
            WHERE startup_id = @startup_id AND investor_email = @investor_email
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
            ]
        )
        
        check_job = bq_client.query(check_query, job_config=job_config)
        count = list(check_job.result())[0].count
        
        if count > 0:
            # Update existing record
            update_query = f"""
                UPDATE `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
                SET 
                    investor_note = @note,
                    note_updated_at = @now,
                    last_updated = @now
                WHERE startup_id = @startup_id AND investor_email = @investor_email
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                    bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
                    bigquery.ScalarQueryParameter("note", "STRING", request.note),
                    bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                ]
            )
            
            bq_client.query(update_query, job_config=job_config).result()
        else:
            # Insert new record with default "New" status
            insert_query = f"""
                INSERT INTO `{settings.google_cloud_project}.{settings.bigquery_dataset_id}.startup_status`
                (startup_id, investor_email, status, investor_note, note_updated_at, status_updated_at, created_at, last_updated)
                VALUES (@startup_id, @investor_email, 'New', @note, @now, @now, @now, @now)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                    bigquery.ScalarQueryParameter("investor_email", "STRING", investor_email),
                    bigquery.ScalarQueryParameter("note", "STRING", request.note),
                    bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                ]
            )
            
            bq_client.query(insert_query, job_config=job_config).result()
        
        return {
            "success": True,
            "startup_id": startup_id,
            "note": request.note,
            "updated_at": now
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update startup note: {str(e)}")
