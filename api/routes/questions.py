"""
Questions API routes for Q&A feature.
Handles questions from investors and answers from founders.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
import logging
import asyncio

from api.models.requests import QuestionRequest, AnswerRequest, QuestionUpdateRequest, BulkAnswerRequest
from api.models.responses import QuestionResponse, BulkAnswerResponse, BulkAnswerResult
from api.services import fs_client, bq_client
from api.services.reanalysis_service import reanalysis_service
from api.utils.firebase_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new question for a startup.
    Only investors can create questions.
    """
    try:
        # Check if user is an investor
        if current_user.get('role') != 'investor':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only investors can ask questions"
            )
        
        # Get startup info to find the founder
        startup_query = f"""
            SELECT id, submitted_by, company_name
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE id = '{question_data.startup_id}'
            LIMIT 1
        """
        startup_results = list(bq_client.query(startup_query))
        
        if not startup_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Startup {question_data.startup_id} not found"
            )
        
        startup = startup_results[0]
        
        # Create question in Firestore
        question = fs_client.create_question({
            "startup_id": question_data.startup_id,
            "asked_by": current_user['uid'],
            "asked_by_name": current_user.get('name', current_user.get('email')),
            "asked_by_role": current_user['role'],
            "question_text": question_data.question_text,
            "category": question_data.category.value,
            "priority": question_data.priority.value,
            "status": "pending",
            "is_ai_generated": False,
            "tags": question_data.tags
        })
        
        # Send notification to founder
        fs_client.create_notification(
            user_id=startup['submitted_by'],
            type="new_question",
            title="New Question from Investor",
            message=f"{current_user.get('name', 'An investor')} asked about {question_data.category.value}",
            related_id=question['id'],
            related_type="question"
        )
        
        # Create activity feed entry
        fs_client.create_activity(
            startup_id=question_data.startup_id,
            user_id=current_user['uid'],
            user_name=current_user.get('name', current_user.get('email')),
            activity_type="question_asked",
            description=f"Asked a question about {question_data.category.value}",
            metadata={"question_id": question['id'], "category": question_data.category.value}
        )
        
        logger.info(f"Question created: {question['id']} for startup {question_data.startup_id}")
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create question: {str(e)}"
        )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a single question by ID."""
    try:
        question = fs_client.get_question(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found"
            )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get question: {str(e)}"
        )


@router.put("/{question_id}/answer", response_model=QuestionResponse)
async def answer_question(
    question_id: str,
    answer_data: AnswerRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Answer a question.
    Only founders can answer questions about their startups.
    """
    try:
        # Get the question
        question = fs_client.get_question(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found"
            )
        
        # Check if user is a founder
        if current_user.get('role') != 'founder':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only founders can answer questions"
            )
        
        # Verify the founder owns this startup
        startup_query = f"""
            SELECT id, submitted_by, company_name
            FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
            WHERE id = '{question['startup_id']}'
            AND submitted_by = '{current_user['uid']}'
            LIMIT 1
        """
        startup_results = list(bq_client.query(startup_query))
        
        if not startup_results:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only answer questions about your own startup"
            )
        
        # Update question with embedded answer
        updated_question = fs_client.update_question(question_id, {
            "status": "answered",
            "answer": {
                "answered_by": current_user['uid'],
                "answered_by_name": current_user.get('name', current_user.get('email')),
                "answer_text": answer_data.answer_text,
                "attachments": [att.dict() for att in answer_data.attachments]
            }
        })
        
        # Notify the investor who asked the question
        fs_client.create_notification(
            user_id=question['asked_by'],
            type="question_answered",
            title="Question Answered",
            message=f"{current_user.get('name', 'Founder')} answered your question",
            related_id=question_id,
            related_type="question"
        )
        
        # Create activity feed entry
        fs_client.create_activity(
            startup_id=question['startup_id'],
            user_id=current_user['uid'],
            user_name=current_user.get('name', current_user.get('email')),
            activity_type="answer_provided",
            description=f"Answered a question about {question['category']}",
            metadata={"question_id": question_id, "category": question['category']}
        )
        
        # Check if auto-reanalysis should trigger
        should_trigger = await reanalysis_service.check_auto_trigger_conditions(
            startup_id=question['startup_id']
        )
        
        if should_trigger:
            logger.info(f"All questions answered for startup {question['startup_id']}, triggering auto-reanalysis")
            
            # Trigger reanalysis in background
            asyncio.create_task(
                reanalysis_service.trigger_reanalysis(
                    startup_id=question['startup_id'],
                    investor_notes="Auto-triggered: All investor questions have been answered by the founder.",
                    investor_id="system"
                )
            )
            
            # Notify founder that reanalysis was triggered
            try:
                fs_client.create_notification(
                    user_id=current_user['uid'],
                    type="reanalysis_triggered",
                    title="Reanalysis Started",
                    message="Your answers triggered a new analysis. You'll be notified when it's complete.",
                    related_id=question['startup_id'],
                    related_type="startup"
                )
            except Exception as notif_error:
                logger.error(f"Failed to send reanalysis notification: {notif_error}")
        
        logger.info(f"Question answered: {question_id}")
        return updated_question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.post("/bulk-answer", response_model=BulkAnswerResponse)
async def bulk_answer_questions(
    bulk_data: BulkAnswerRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Answer multiple questions at once.
    Only founders can answer questions about their startups.
    """
    try:
        # Check if user is a founder
        if current_user.get('role') != 'founder':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only founders can answer questions"
            )
        
        results = []
        successful_count = 0
        failed_count = 0
        startup_id = None
        
        # Process each answer
        for answer_item in bulk_data.answers:
            try:
                # Get the question
                question = fs_client.get_question(answer_item.question_id)
                
                if not question:
                    results.append(BulkAnswerResult(
                        question_id=answer_item.question_id,
                        success=False,
                        error=f"Question {answer_item.question_id} not found"
                    ))
                    failed_count += 1
                    continue
                
                # Store startup_id for later reanalysis check
                if startup_id is None:
                    startup_id = question['startup_id']
                
                # Verify the founder owns this startup
                startup_query = f"""
                    SELECT id, submitted_by, company_name
                    FROM `{bq_client.project_id}.{bq_client.dataset_id}.startups`
                    WHERE id = '{question['startup_id']}'
                    AND submitted_by = '{current_user['uid']}'
                    LIMIT 1
                """
                startup_results = list(bq_client.query(startup_query))
                
                if not startup_results:
                    results.append(BulkAnswerResult(
                        question_id=answer_item.question_id,
                        success=False,
                        error="You can only answer questions about your own startup"
                    ))
                    failed_count += 1
                    continue
                
                # Update question with embedded answer
                updated_question = fs_client.update_question(answer_item.question_id, {
                    "status": "answered",
                    "answer": {
                        "answered_by": current_user['uid'],
                        "answered_by_name": current_user.get('name', current_user.get('email')),
                        "answer_text": answer_item.answer_text,
                        "attachments": [att.dict() for att in answer_item.attachments]
                    }
                })
                
                # Notify the investor who asked the question
                try:
                    fs_client.create_notification(
                        user_id=question['asked_by'],
                        type="question_answered",
                        title="Question Answered",
                        message=f"{current_user.get('name', 'Founder')} answered your question",
                        related_id=answer_item.question_id,
                        related_type="question"
                    )
                except Exception as notif_error:
                    logger.warning(f"Failed to send notification for question {answer_item.question_id}: {notif_error}")
                
                # Create activity feed entry
                try:
                    fs_client.create_activity(
                        startup_id=question['startup_id'],
                        user_id=current_user['uid'],
                        user_name=current_user.get('name', current_user.get('email')),
                        activity_type="answer_provided",
                        description=f"Answered a question about {question['category']}",
                        metadata={"question_id": answer_item.question_id, "category": question['category']}
                    )
                except Exception as activity_error:
                    logger.warning(f"Failed to create activity for question {answer_item.question_id}: {activity_error}")
                
                results.append(BulkAnswerResult(
                    question_id=answer_item.question_id,
                    success=True,
                    question=updated_question
                ))
                successful_count += 1
                
            except Exception as e:
                logger.error(f"Error answering question {answer_item.question_id}: {e}")
                results.append(BulkAnswerResult(
                    question_id=answer_item.question_id,
                    success=False,
                    error=str(e)
                ))
                failed_count += 1
        
        # Trigger reanalysis after successful bulk submission
        # Since the UI only allows submission when all questions are answered,
        # we always trigger reanalysis after successful submission
        reanalysis_triggered = False
        if startup_id and successful_count > 0:
            logger.info(f"Bulk answers submitted for startup {startup_id}, triggering reanalysis")
            
            # Trigger reanalysis in background
            asyncio.create_task(
                reanalysis_service.trigger_reanalysis(
                    startup_id=startup_id,
                    investor_notes="Auto-triggered: Founder submitted answers to all investor questions.",
                    investor_id="system"
                )
            )
            
            reanalysis_triggered = True
            
            # Notify founder that reanalysis was triggered
            try:
                fs_client.create_notification(
                    user_id=current_user['uid'],
                    type="reanalysis_triggered",
                    title="Reanalysis Started",
                    message="Your answers triggered a new analysis. You'll be notified when it's complete.",
                    related_id=startup_id,
                    related_type="startup"
                )
            except Exception as notif_error:
                logger.error(f"Failed to send reanalysis notification: {notif_error}")
        
        # Build response message
        if successful_count == len(bulk_data.answers):
            message = f"All {successful_count} answers submitted successfully"
        elif successful_count > 0:
            message = f"{successful_count} answers submitted successfully, {failed_count} failed"
        else:
            message = f"All {failed_count} answers failed"
        
        if reanalysis_triggered:
            message += ". Reanalysis has been triggered automatically."
        
        logger.info(f"Bulk answer completed: {successful_count} successful, {failed_count} failed")
        
        return BulkAnswerResponse(
            total=len(bulk_data.answers),
            successful=successful_count,
            failed=failed_count,
            results=results,
            reanalysis_triggered=reanalysis_triggered,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bulk answers: {str(e)}"
        )


@router.get("/startup/{startup_id}", response_model=List[QuestionResponse])
async def get_startup_questions(
    startup_id: str,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all questions for a startup.
    Can filter by status: pending, answered, clarification_needed
    """
    try:
        questions = fs_client.get_questions_by_startup(
            startup_id=startup_id,
            status=status
        )
        
        logger.info(f"Retrieved {len(questions)} questions for startup {startup_id}")
        return questions
        
    except Exception as e:
        logger.error(f"Error getting startup questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get questions: {str(e)}"
        )


@router.get("/my-questions", response_model=List[QuestionResponse])
async def get_my_questions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all questions asked by the current user (investor)."""
    try:
        if current_user.get('role') != 'investor':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only investors can view their questions"
            )
        
        questions = fs_client.get_questions_by_user(current_user['uid'])
        
        logger.info(f"Retrieved {len(questions)} questions for user {current_user['uid']}")
        return questions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get questions: {str(e)}"
        )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    update_data: QuestionUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a question (text, category, priority, tags).
    Only the question asker can update it.
    """
    try:
        # Get the question
        question = fs_client.get_question(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found"
            )
        
        # Check if user is the asker
        if question['asked_by'] != current_user['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own questions"
            )
        
        # Build update dict
        update_dict = {}
        if update_data.question_text is not None:
            update_dict['question_text'] = update_data.question_text
        if update_data.category is not None:
            update_dict['category'] = update_data.category.value
        if update_data.priority is not None:
            update_dict['priority'] = update_data.priority.value
        if update_data.tags is not None:
            update_dict['tags'] = update_data.tags
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update question
        updated_question = fs_client.update_question(question_id, update_dict)
        
        logger.info(f"Question updated: {question_id}")
        return updated_question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}"
        )


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a question.
    Only the question asker or admin can delete it.
    """
    try:
        # Get the question
        question = fs_client.get_question(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found"
            )
        
        # Check if user is the asker or admin
        if question['asked_by'] != current_user['uid'] and current_user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own questions"
            )
        
        # Delete question
        fs_client.delete_question(question_id)
        
        logger.info(f"Question deleted: {question_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete question: {str(e)}"
        )
