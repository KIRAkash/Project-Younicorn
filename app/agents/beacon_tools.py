# Copyright 2025 Google LLC
# ... (licenses) ...

"""ADK Tools for Beacon AI Agent.

This file implements the "Single Tool Router" pattern.
"""

import logging
import json
from typing import Literal, Dict, Any
from datetime import datetime
import asyncio

from pydantic import BaseModel, Field
from google.cloud import bigquery
from api.config.settings import settings
from api.services.firestore_client import fs_client  # Still needed for questions
from api.services.reanalysis_service import reanalysis_service

logger = logging.getLogger(__name__)

# Initialize BigQuery client
bq_client = bigquery.Client(project=settings.google_cloud_project)


# --- 1. Define ONE "Flattened" Schema for ALL Actions ---
class BeaconActionArgs(BaseModel):
    """Arguments for the primary Beacon tool. The LLM will choose one action_type
    and fill in only the arguments relevant to that action."""
    
    action_type: Literal[
        "add_question",
        "add_note",
        "update_status",
        "trigger_reanalysis"
    ] = Field(..., description="The specific action to perform.")
    
    # Arguments for "add_question"
    question_text: str | None = Field(None, description="The question to ask the founders.")
    category: str | None = Field(None, description="Category for the new question. Must be one of: 'team', 'market', 'product', 'traction', 'financials', 'technical', 'other'.")
    
    # Arguments for "add_note"
    note_text: str | None = Field(None, description="The private investor note content.")
    
    # Arguments for "update_status"
    status: str | None = Field(None, description="New status for the startup. Must be one of: 'New', 'On Watch', 'Shortlist', 'Pass', 'Invested'.")
    
    # Arguments for "trigger_reanalysis"
    focus_areas: str | None = Field(None, description="Specific areas to focus on in the re-analysis.")


# --- 2. Define the ONE Tool Implementation ---
async def perform_beacon_action(
    tool_context,        # No type hint
    args: Dict[str, Any] # <-- FIX: The Runner passes a dict, not a Pydantic model
) -> str:
    """
    Performs a specific action for the Beacon agent based on the 'action_type'.
    This single tool routes to all other business logic.
    """
    try:
        # --- FIX: Manually parse the dict into the Pydantic model ---
        try:
            # This validates the dict from the LLM
            parsed_args = BeaconActionArgs.model_validate(args)
        except Exception as pydantic_error:
            logger.error(f"Pydantic validation error for tool args: {pydantic_error}")
            return json.dumps({"status": "error", "message": f"Invalid arguments: {pydantic_error}"})
        # --- END FIX ---

        # Get context info
        startup_id = tool_context.state.get("startup_id")
        user_id = tool_context.state.get("user_id")
        
        if not startup_id:
            return json.dumps({"status": "error", "message": "No startup_id in session."})
        if not user_id:
            return json.dumps({"status": "error", "message": "No user_id in session."})

        # --- 3. Python Router Logic (now using 'parsed_args') ---
        
        if parsed_args.action_type == "add_question":
            if not parsed_args.question_text or not parsed_args.category:
                return json.dumps({"status": "error", "message": "Missing 'question_text' or 'category' for add_question."})
            
            question_data = {
                "startup_id": startup_id, "asked_by": user_id,
                "question_text": parsed_args.question_text, "category": parsed_args.category,
                "priority": "medium", "source": "Younicorn Agents"
            }
            created_doc = fs_client.create_question(question_data)
            response = {"status": "success", "question_id": created_doc.get("id")}
            return json.dumps(response)

        elif parsed_args.action_type == "add_note":
            if not parsed_args.note_text:
                return json.dumps({"status": "error", "message": "Missing 'note_text' for add_note."})

            # Direct BigQuery operation (same logic as API endpoint)
            try:
                # Get investor email from user_id (assuming user_id is email)
                investor_email = user_id
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
                            bigquery.ScalarQueryParameter("note", "STRING", parsed_args.note_text),
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
                            bigquery.ScalarQueryParameter("note", "STRING", parsed_args.note_text),
                            bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                        ]
                    )
                    
                    bq_client.query(insert_query, job_config=job_config).result()
                
                response = {"status": "success", "note": parsed_args.note_text, "updated_at": now}
                return json.dumps(response)
                
            except Exception as e:
                logger.error(f"Error adding note to BigQuery: {e}", exc_info=True)
                return json.dumps({"status": "error", "message": str(e)})

        elif parsed_args.action_type == "update_status":
            if not parsed_args.status:
                return json.dumps({"status": "error", "message": "Missing 'status' for update_status."})

            # Direct BigQuery operation (same logic as API endpoint)
            try:
                # Get investor email from user_id (assuming user_id is email)
                investor_email = user_id
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
                            bigquery.ScalarQueryParameter("status", "STRING", parsed_args.status),
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
                            bigquery.ScalarQueryParameter("status", "STRING", parsed_args.status),
                            bigquery.ScalarQueryParameter("now", "TIMESTAMP", now),
                        ]
                    )
                    
                    bq_client.query(insert_query, job_config=job_config).result()
                
                response = {"status": "success", "new_status": parsed_args.status, "updated_at": now}
                return json.dumps(response)
                
            except Exception as e:
                logger.error(f"Error updating status in BigQuery: {e}", exc_info=True)
                return json.dumps({"status": "error", "message": str(e)})

        elif parsed_args.action_type == "trigger_reanalysis":
            if not parsed_args.focus_areas:
                return json.dumps({"status": "error", "message": "Missing 'focus_areas' for trigger_reanalysis."})

            analysis_result = await reanalysis_service.trigger_reanalysis(
                startup_id=startup_id,
                investor_notes=parsed_args.focus_areas,
                investor_id=user_id
            )
            response = {
                "status": "success",
                "message": analysis_result.get("message", "Re-analysis triggered."),
                "analysis_id": analysis_result.get("analysis_id")
            }
            return json.dumps(response)
            
        else:
            return json.dumps({"status": "error", "message": f"Unknown action_type: {parsed_args.action_type}"})

    except Exception as e:
        logger.error(f"Error in perform_beacon_action tool: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": str(e)})


# --- 4. Export the *single raw function* in a list ---
beacon_tools = [
    perform_beacon_action
]