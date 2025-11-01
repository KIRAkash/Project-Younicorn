"""
Founder-specific routes for Project Younicorn API.

Provides endpoints for founders to view their submissions and track analysis status.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends
from google.cloud import bigquery
import logging
import json

from ..utils.firebase_auth import require_founder, get_current_user
from ..services.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/founder", tags=["founder"])


@router.get("/submissions")
async def get_founder_submissions(
    current_user: Dict[str, Any] = Depends(require_founder)
) -> Dict[str, Any]:
    """
    Get all submissions for the current founder.
    
    Requires: Authorization header with Firebase ID token (founder role)
    """
    try:
        founder_email = current_user['email']
        
        # Initialize BigQuery client
        bq_client = BigQueryClient()
        client = bq_client.client
        
        # Query to get founder's submissions
        query = """
        SELECT 
            s.id as startup_id,
            s.company_name,
            s.industry,
            s.submission_timestamp as submission_date,
            COALESCE(
                (SELECT status FROM `{project}.{dataset}.analyses` 
                 WHERE startup_id = s.id AND is_latest = true
                 ORDER BY started_at DESC LIMIT 1),
                'pending'
            ) as analysis_status,
            (SELECT overall_score FROM `{project}.{dataset}.analyses` 
             WHERE startup_id = s.id AND status = 'completed' AND is_latest = true
             ORDER BY started_at DESC LIMIT 1) as overall_score
        FROM `{project}.{dataset}.startups` s
        WHERE s.submitted_by = @founder_email
        ORDER BY s.submission_timestamp DESC
        """.format(
            project=client.project,
            dataset=bq_client.dataset_id
        )
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("founder_email", "STRING", founder_email)
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        submissions = []
        for row in results:
            submissions.append({
                'startup_id': row.startup_id,
                'company_name': row.company_name,
                'industry': row.industry,
                'submission_date': row.submission_date.isoformat() if row.submission_date else None,
                'analysis_status': row.analysis_status,
                'overall_score': float(row.overall_score) if row.overall_score else None
            })
        
        return {
            'success': True,
            'submissions': submissions,
            'count': len(submissions)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch founder submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/submission/{startup_id}")
async def get_founder_submission_details(
    startup_id: str,
    current_user: Dict[str, Any] = Depends(require_founder)
) -> Dict[str, Any]:
    """
    Get details of a specific submission for the current founder.
    
    Requires: Authorization header with Firebase ID token (founder role)
    """
    try:
        founder_email = current_user['email']
        
        # Initialize BigQuery client
        bq_client = BigQueryClient()
        client = bq_client.client
        
        # Query to get submission details
        query = """
        SELECT 
            id as startup_id,
            company_name,
            industry,
            website,
            description,
            stage,
            funding_raised,
            team_size,
            location,
            submission_timestamp as submission_date,
            submitted_by
        FROM `{project}.{dataset}.startups`
        WHERE id = @startup_id AND submitted_by = @founder_email
        """.format(
            project=client.project,
            dataset=bq_client.dataset_id
        )
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id),
                bigquery.ScalarQueryParameter("founder_email", "STRING", founder_email)
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Submission not found or access denied'
            )
        
        row = results[0]
        submission = {
            'startup_id': row.startup_id,
            'company_name': row.company_name,
            'industry': row.industry,
            'website': row.website,
            'description': row.description,
            'stage': row.stage,
            'funding_raised': row.funding_raised,
            'team_size': row.team_size,
            'location': row.location,
            'submission_date': row.submission_date.isoformat() if row.submission_date else None
        }
        
        return {
            'success': True,
            'submission': submission
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch submission details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/submission/{startup_id}/analysis")
async def get_founder_submission_analysis(
    startup_id: str,
    current_user: Dict[str, Any] = Depends(require_founder)
) -> Dict[str, Any]:
    """
    Get analysis results for a specific submission (founder can only see their own).
    
    Requires: Authorization header with Firebase ID token (founder role)
    """
    try:
        founder_email = current_user['email']
        
        # Initialize BigQuery client
        bq_client = BigQueryClient()
        client = bq_client.client
        
        # First verify the startup belongs to this founder
        verify_query = """
        SELECT submitted_by
        FROM `{project}.{dataset}.startups`
        WHERE id = @startup_id
        """.format(
            project=client.project,
            dataset=bq_client.dataset_id
        )
        
        verify_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id)
            ]
        )
        
        verify_job = client.query(verify_query, job_config=verify_job_config)
        verify_results = list(verify_job.result())
        
        if not verify_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Submission not found'
            )
        
        if verify_results[0].submitted_by != founder_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Access denied'
            )
        
        # Get analysis results
        analysis_query = """
        SELECT 
            a.id,
            a.startup_id,
            a.status,
            a.overall_score,
            a.team_score,
            a.market_score,
            a.product_score,
            a.competition_score,
            a.started_at as analysis_date,
            a.team_analysis,
            a.market_analysis,
            a.product_analysis,
            a.competition_analysis,
            a.synthesis_analysis,
            a.agent_analyses,
            s.company_name,
            s.industry
        FROM `{project}.{dataset}.analyses` a
        LEFT JOIN `{project}.{dataset}.startups` s ON a.startup_id = s.id
        WHERE a.startup_id = @startup_id AND a.status = 'completed' AND a.is_latest = true
        ORDER BY a.started_at DESC
        LIMIT 1
        """.format(
            project=client.project,
            dataset=bq_client.dataset_id
        )
        
        analysis_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("startup_id", "STRING", startup_id)
            ]
        )
        
        analysis_job = client.query(analysis_query, job_config=analysis_job_config)
        analysis_results = list(analysis_job.result())
        
        if not analysis_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Analysis not yet completed'
            )
        
        row = analysis_results[0]
        
        # Parse agent_analyses if it's a string
        agent_analyses = row.agent_analyses
        if isinstance(agent_analyses, str):
            try:
                agent_analyses = json.loads(agent_analyses)
            except:
                pass
        
        analysis = {
            'startup_id': row.startup_id,
            'company_name': row.company_name,
            'industry': row.industry,
            'status': row.status,
            'overall_score': float(row.overall_score) if row.overall_score else None,
            'team_score': float(row.team_score) if row.team_score else None,
            'market_score': float(row.market_score) if row.market_score else None,
            'product_score': float(row.product_score) if row.product_score else None,
            'competition_score': float(row.competition_score) if row.competition_score else None,
            'analysis_date': row.analysis_date.isoformat() if row.analysis_date else None,
            'team_analysis': row.team_analysis,
            'market_analysis': row.market_analysis,
            'product_analysis': row.product_analysis,
            'competition_analysis': row.competition_analysis,
            'synthesis_analysis': row.synthesis_analysis,
            'agent_analyses': agent_analyses
        }
        
        return {
            'success': True,
            'analysis': analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_founder_stats(
    current_user: Dict[str, Any] = Depends(require_founder)
) -> Dict[str, Any]:
    """
    Get statistics for the current founder's submissions.
    
    Requires: Authorization header with Firebase ID token (founder role)
    """
    try:
        founder_email = current_user['email']
        
        # Initialize BigQuery client
        bq_client = BigQueryClient()
        client = bq_client.client
        
        # Query to get founder stats
        query = """
        WITH startup_analyses AS (
            SELECT 
                s.id,
                (SELECT status FROM `{project}.{dataset}.analyses` 
                 WHERE startup_id = s.id AND is_latest = true
                 ORDER BY started_at DESC LIMIT 1) as analysis_status,
                (SELECT overall_score FROM `{project}.{dataset}.analyses` 
                 WHERE startup_id = s.id AND status = 'completed' AND is_latest = true
                 ORDER BY started_at DESC LIMIT 1) as overall_score
            FROM `{project}.{dataset}.startups` s
            WHERE s.submitted_by = @founder_email
        )
        SELECT 
            COUNT(*) as total_submissions,
            COUNTIF(analysis_status = 'completed') as completed_analyses,
            COUNTIF(analysis_status = 'in_progress') as in_progress,
            COUNTIF(analysis_status IS NULL OR analysis_status = 'pending') as pending,
            AVG(overall_score) as avg_score
        FROM startup_analyses
        """.format(
            project=client.project,
            dataset=bq_client.dataset_id
        )
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("founder_email", "STRING", founder_email)
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if results:
            row = results[0]
            stats = {
                'total_submissions': row.total_submissions,
                'completed_analyses': row.completed_analyses,
                'in_progress': row.in_progress,
                'pending': row.pending,
                'average_score': float(row.avg_score) if row.avg_score else None
            }
        else:
            stats = {
                'total_submissions': 0,
                'completed_analyses': 0,
                'in_progress': 0,
                'pending': 0,
                'average_score': None
            }
        
        return {
            'success': True,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch founder stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
