"""Reanalysis service for Project Younicorn API."""

import asyncio
import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime

from .bigquery_client import bq_client
from .firestore_client import fs_client
from .analysis_service import analysis_service
from ..utils import safe_json_loads

logger = logging.getLogger(__name__)


class ReanalysisService:
    """Service for handling startup reanalysis with enhanced context."""
    
    @staticmethod
    async def trigger_reanalysis(
        startup_id: str,
        investor_notes: str,
        investor_id: str
    ) -> Dict[str, Any]:
        """
        Trigger reanalysis with enhanced context.
        
        Args:
            startup_id: Unique identifier for the startup
            investor_notes: Specific notes/instructions from investor
            investor_id: ID of the investor triggering reanalysis
        
        Returns:
            Dictionary with analysis_id, message, and status
        """
        try:
            logger.info(f"Triggering reanalysis for startup {startup_id}")
            
            # 1. Fetch startup data from BigQuery
            startup_data = await ReanalysisService._fetch_startup_data(startup_id)
            
            # 2. Fetch answered questions from Firestore
            answered_questions = await ReanalysisService._fetch_answered_questions(startup_id)
            
            # 3. Fetch GCS files from startup record
            gcs_files = safe_json_loads(startup_data.get('gcs_files_raw', '[]'), [])
            
            # 4. Extract attachments from answered questions and add to gcs_files
            import mimetypes
            answer_attachments_count = 0
            for question in answered_questions:
                answer_attachments = question.get('answer_attachments', [])
                for attachment in answer_attachments:
                    gcs_path = attachment.get('gcs_path')
                    if gcs_path:
                        filename = attachment.get('filename', 'unknown')
                        
                        # Detect content_type from filename if not provided
                        content_type = attachment.get('content_type')
                        if not content_type:
                            content_type, _ = mimetypes.guess_type(filename)
                            content_type = content_type or 'application/octet-stream'
                        
                        # Add to gcs_files list for processing
                        gcs_files.append({
                            'gcs_path': gcs_path,
                            'filename': filename,
                            'content_type': content_type,
                            'size': attachment.get('size', 0),
                            'source': 'answer_attachment'  # Mark source for tracking
                        })
                        answer_attachments_count += 1
                        logger.debug(f"  Added answer attachment: {filename} ({content_type})")
            
            if answer_attachments_count > 0:
                logger.info(f"Extracted {answer_attachments_count} attachments from answered questions")
            
            # 5. Build enhanced context
            enhanced_startup_data = {
                **startup_data,
                "is_reanalysis": True,
                "investor_notes": investor_notes,
                "answered_questions": answered_questions
            }
            
            # 6. Generate new analysis_id
            analysis_id = str(uuid.uuid4())
            
            logger.info(f"Starting reanalysis {analysis_id} for startup {startup_id}")
            logger.info(f"  - Investor notes: {investor_notes[:100]}...")
            logger.info(f"  - Answered questions: {len(answered_questions)}")
            logger.info(f"  - Original GCS files: {len(gcs_files) - answer_attachments_count}")
            logger.info(f"  - Answer attachments: {answer_attachments_count}")
            logger.info(f"  - Total files to process: {len(gcs_files)}")
            
            # 6. Trigger analysis (same function, enhanced context)
            asyncio.create_task(
                analysis_service.start_ai_analysis(
                    startup_id=startup_id,
                    analysis_id=analysis_id,
                    startup_data=enhanced_startup_data,
                    gcs_files=gcs_files,
                    is_reanalysis=True
                )
            )
            
            return {
                "analysis_id": analysis_id,
                "message": "Reanalysis started successfully",
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Error triggering reanalysis: {e}")
            raise
    
    @staticmethod
    async def _fetch_startup_data(startup_id: str) -> Dict[str, Any]:
        """
        Fetch complete startup data from BigQuery.
        
        Args:
            startup_id: Unique identifier for the startup
        
        Returns:
            Dictionary containing all startup data
        
        Raises:
            Exception if startup not found
        """
        if not bq_client or not bq_client.is_available:
            raise Exception("BigQuery client not available")
        
        try:
            sql = f"""
            SELECT *
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE id = '{startup_id}'
            LIMIT 1
            """
            results = list(bq_client.query(sql))
            
            if not results:
                raise Exception(f"Startup {startup_id} not found")
            
            row = results[0]
            
            # Build startup data dictionary
            startup_data = {
                "startup_id": startup_id,
                "company_info": safe_json_loads(row.get("company_info"), {}),
                "founders": safe_json_loads(row.get("founders"), []),
                "documents": safe_json_loads(row.get("documents"), []),
                "gcs_files_raw": row.get("gcs_files", "[]"),  # Keep raw for later parsing
                "metadata": safe_json_loads(row.get("metadata"), {}),
                "submission_type": row.get("submission_type", "form"),
                "submitted_by": row.get("submitted_by")
            }
            
            logger.info(f"Fetched startup data for {startup_id}")
            return startup_data
            
        except Exception as e:
            logger.error(f"Error fetching startup data: {e}")
            raise
    
    @staticmethod
    async def _fetch_answered_questions(startup_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all answered questions from Firestore.
        
        Args:
            startup_id: Unique identifier for the startup
        
        Returns:
            List of formatted question-answer pairs
        """
        try:
            questions = fs_client.get_questions_by_startup(
                startup_id=startup_id,
                status='answered'
            )
            
            # Format for agent consumption
            formatted_questions = []
            total_attachments = 0
            for q in questions:
                answer_data = q.get('answer', {})
                answer_attachments = answer_data.get('attachments', [])
                total_attachments += len(answer_attachments)
                
                formatted_questions.append({
                    "question_text": q.get('question_text'),
                    "answer_text": answer_data.get('answer_text'),
                    "category": q.get('category'),
                    "priority": q.get('priority'),
                    "asked_by": q.get('asked_by_name'),
                    "answered_by": answer_data.get('answered_by_name'),
                    "answer_attachments": answer_attachments  # Include attachments
                })
            
            logger.info(f"Fetched {len(formatted_questions)} answered questions with {total_attachments} attachments for startup {startup_id}")
            return formatted_questions
            
        except Exception as e:
            logger.error(f"Error fetching answered questions: {e}")
            # Return empty list if Firestore fails
            return []
    
    @staticmethod
    async def check_auto_trigger_conditions(startup_id: str) -> bool:
        """
        Check if auto-reanalysis should trigger.
        Condition: No unanswered questions remain.
        
        Args:
            startup_id: Unique identifier for the startup
        
        Returns:
            True if auto-reanalysis should trigger, False otherwise
        """
        try:
            # Get all questions for this startup
            all_questions = fs_client.get_questions_by_startup(startup_id=startup_id)
            
            if not all_questions or len(all_questions) == 0:
                logger.info(f"No questions found for startup {startup_id}, skipping auto-trigger")
                return False
            
            # Check if any are pending/unanswered
            unanswered = [q for q in all_questions if q.get('status') != 'answered']
            
            # Trigger if no unanswered questions
            should_trigger = len(unanswered) == 0
            
            logger.info(f"Auto-trigger check for startup {startup_id}: "
                       f"{len(all_questions)} total questions, {len(unanswered)} unanswered, "
                       f"should_trigger={should_trigger}")
            
            return should_trigger
            
        except Exception as e:
            logger.error(f"Error checking auto-trigger conditions: {e}")
            return False


# Global reanalysis service instance
reanalysis_service = ReanalysisService()
