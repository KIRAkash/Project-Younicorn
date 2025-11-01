"""AI Analysis service for Project Younicorn API - Refactored for new Pydantic schemas."""

import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback

from .bigquery_client import bq_client
from .file_handling_service import file_handling_service
from .firestore_client import fs_client
from ..utils import extract_json_from_text

logger = logging.getLogger(__name__)

# In-memory storage for active analyses (thread-safe with lock)
active_analyses: Dict[str, Dict[str, Any]] = {}
active_analyses_lock = threading.Lock()

class AnalysisService:
    
    @staticmethod
    def _update_progress(analysis_id: str, progress: int, step: str):
        """Thread-safe progress update."""
        with active_analyses_lock:
            if analysis_id in active_analyses:
                active_analyses[analysis_id]["progress"] = progress
                active_analyses[analysis_id]["current_step"] = step
    
    @staticmethod
    def _update_status(analysis_id: str, status: str, **kwargs):
        """Thread-safe status update."""
        with active_analyses_lock:
            if analysis_id in active_analyses:
                active_analyses[analysis_id]["status"] = status
                active_analyses[analysis_id].update(kwargs)
    
    @staticmethod
    def _extract_executive_summary(synthesis_analysis):
        """Extract executive summary from synthesis analysis."""
        if isinstance(synthesis_analysis, dict):
            # New schema: get executive_summary from synthesis result
            if 'executive_summary' in synthesis_analysis:
                return synthesis_analysis['executive_summary']
        elif isinstance(synthesis_analysis, str):
            return synthesis_analysis
        return "AI analysis completed successfully"
    
    @staticmethod
    def _extract_investment_memo(synthesis_analysis):
        """Extract investment memo from synthesis analysis."""
        if isinstance(synthesis_analysis, dict):
            # New schema: get investment_memo from synthesis result
            if 'investment_memo' in synthesis_analysis:
                return synthesis_analysis['investment_memo']
            elif 'investment_thesis' in synthesis_analysis:
                return synthesis_analysis['investment_thesis']
        elif isinstance(synthesis_analysis, str):
            return synthesis_analysis
        return "Detailed analysis available in agent results"
    
    @staticmethod
    async def start_ai_analysis(startup_id: str, analysis_id: str, startup_data: Dict[str, Any], gcs_files: list = None, is_reanalysis: bool = False):
        """Start real AI analysis using Project Younicorn agent system with new structured schemas.
        
        Args:
            startup_id: Unique identifier for the startup
            analysis_id: Unique identifier for the analysis
            startup_data: Dictionary containing startup information
            gcs_files: List of GCS file objects with 'gcs_path' and 'content_type' fields
            is_reanalysis: Whether this is a reanalysis (default: False)
        """
        try:
            # Initialize analysis state (thread-safe)
            with active_analyses_lock:
                active_analyses[analysis_id] = {
                    "id": analysis_id,
                    "startup_id": startup_id,
                    "status": "running",
                    "progress": 0,
                    "current_step": "Initializing",
                    "started_at": datetime.utcnow().isoformat()
                }
            
            # Extract reanalysis context if present
            is_reanalysis = startup_data.get("is_reanalysis", False)
            investor_notes = startup_data.get("investor_notes", "")
            answered_questions = startup_data.get("answered_questions", [])
            
            logger.info(f"Starting {'RE-ANALYSIS' if is_reanalysis else 'ANALYSIS'} for startup {startup_id}")
            if is_reanalysis:
                logger.info(f"  - Investor notes: {investor_notes[:100] if investor_notes else 'None'}...")
                logger.info(f"  - Answered questions: {len(answered_questions)}")
            
            # Process files and extract text if provided
            attachments = []
            if gcs_files:
                logger.info(f"GCS files provided: {len(gcs_files)} file(s)")
                for gcs_file in gcs_files:
                    logger.info(f"  - {gcs_file.get('filename', 'unknown')} ({gcs_file.get('content_type', 'unknown')}) at {gcs_file.get('gcs_path', 'unknown')}")
                
                # Update progress
                AnalysisService._update_progress(analysis_id, 5, "Checking file content cache and extracting text")
                
                # Extract text from all files (with caching)
                logger.info("Processing files (checking cache first)...")
                attachments = await file_handling_service.process_files(gcs_files)
                logger.info(f"Processed {len(attachments)} file(s)")
                
                # Log cache statistics
                cached_count = sum(1 for a in attachments if a.get('cached', False))
                new_count = len(attachments) - cached_count
                if cached_count > 0:
                    logger.info(f"  ✓ Cache hits: {cached_count} file(s) (saved processing time!)")
                if new_count > 0:
                    logger.info(f"  ⚡ New files processed: {new_count} file(s)")
                
                for attachment in attachments:
                    cache_status = " [CACHED]" if attachment.get('cached', False) else " [NEW]"
                    logger.info(f"  - {attachment['filename']}: {attachment['text_length']} characters{cache_status}")
            
            # Enrich answered questions with extracted text from their attachments
            if is_reanalysis and answered_questions:
                logger.info("Enriching answered questions with attachment content...")
                
                # Create a lookup map: gcs_path -> extracted_text
                attachment_text_map = {}
                for att in attachments:
                    # Match by filename and source (answer attachments have source='answer_attachment')
                    gcs_path = None
                    for gcs_file in gcs_files:
                        if (gcs_file.get('filename') == att.get('filename') and 
                            gcs_file.get('source') == 'answer_attachment'):
                            gcs_path = gcs_file.get('gcs_path')
                            break
                    
                    if gcs_path:
                        attachment_text_map[gcs_path] = {
                            'filename': att.get('filename'),
                            'extracted_text': att.get('extracted_text'),
                            'text_length': att.get('text_length')
                        }
                
                # Enrich each answered question with its attachment content
                # Only keep filename and extracted_text (remove gcs_path, size, content_type, etc.)
                enriched_count = 0
                for question in answered_questions:
                    answer_attachments = question.get('answer_attachments', [])
                    if answer_attachments:
                        cleaned_attachments = []
                        for attachment in answer_attachments:
                            gcs_path = attachment.get('gcs_path')
                            if gcs_path and gcs_path in attachment_text_map:
                                # Only include filename and extracted_text for AI agents
                                cleaned_attachments.append({
                                    'filename': attachment.get('filename'),
                                    'extracted_text': attachment_text_map[gcs_path]['extracted_text']
                                })
                                enriched_count += 1
                        
                        # Replace with cleaned attachments (only filename + extracted_text)
                        question['answer_attachments'] = cleaned_attachments
                
                logger.info(f"  ✓ Enriched {enriched_count} answer attachments with extracted text")
            
            # Try to use real agents
            try:
                from app.agent import minerva_analysis_agent, StartupInfo
                import json
                
                # Update progress
                AnalysisService._update_progress(analysis_id, 10, "Initializing agents")
                
                logger.info("Starting real AI agent workflow")
                
                # Create startup info object for agent analysis
                startup_info = StartupInfo(
                    company_info=json.dumps(startup_data.get("company_info", {})),
                    founders=json.dumps(startup_data.get("founders", [])),
                    attachments=json.dumps(attachments),
                    metadata=json.dumps(startup_data.get("metadata", {})),
                    # Reanalysis fields
                    is_reanalysis=is_reanalysis,
                    investor_notes=investor_notes,
                    answered_questions=json.dumps(answered_questions)
                )
                
                # Log startup info for debugging
                logger.info(f"Startup info prepared:")
                logger.info(f"  - Company: {startup_data.get('company_info', {}).get('name', 'unknown')}")
                logger.info(f"  - Founders: {len(startup_data.get('founders', []))} founder(s)")
                logger.info(f"  - Attachments: {len(attachments)} file(s) with extracted text")
                logger.info(f"  - Total attachment text length: {sum(a['text_length'] for a in attachments)} characters")
                
                # Use proper ADK Runner pattern
                from google.adk.runners import InMemoryRunner
                from google.genai import types as genai_types
                
                # Create runner and session
                runner = InMemoryRunner(
                    agent=minerva_analysis_agent,
                    app_name="minerva_analysis"
                )
                
                session = await runner.session_service.create_session(
                    app_name="minerva_analysis",
                    user_id=f"user-{startup_id}",
                    session_id=analysis_id,
                    state={
                        "startup_info": startup_info.model_dump(),
                        "analysis_id": analysis_id,
                        "startup_id": startup_id
                    }
                )
                
                # Create user message (no heavy file data, just text)
                if attachments:
                    files_list = ", ".join([a['filename'] for a in attachments])
                    message_text = f"Please analyze this startup submission. The startup_info (including extracted text from {len(attachments)} files: {files_list}) is available in the session state."
                else:
                    message_text = "Please analyze this startup submission. The startup_info is available in the session state."
                
                user_message = genai_types.Content(
                    parts=[genai_types.Part(text=message_text)]
                )
                
                # Update session state
                # startup_data_dict = startup_info.model_dump()
                # session.state.update({
                #     "startup_info": startup_data_dict,
                #     "analysis_id": analysis_id,
                #     "startup_id": startup_id
                # })
                
                # Run the agent analysis and collect events
                logger.info("Starting agent workflow execution...")
                events = []
                async for event in runner.run_async(
                    user_id=session.user_id,
                    session_id=session.id,
                    new_message=user_message
                ):
                    events.append(event)
                    event_id = getattr(event, 'event_id', getattr(event, 'id', 'unknown'))
                    logger.info(f"Received event from {event.author}: {event_id}")
                
                logger.info("=" * 80)
                logger.info(f"✓ AGENT WORKFLOW COMPLETED - Collected {len(events)} events")
                logger.info("=" * 80)
                logger.info("STARTING EVENT PROCESSING...")
                logger.info("=" * 80)
                
                # Process agent events and extract structured results
                agent_analyses = {}
                synthesis_result = None
                files_analysis_result = None
                
                # Process events to extract structured agent results
                logger.info(f"Processing {len(events)} events to extract structured results...")
                for idx, event in enumerate(events):
                    logger.info(f"[Event {idx+1}/{len(events)}] Processing event from: {event.author}")
                    if event.content and event.content.parts:
                        logger.info(f"  - Event has {len(event.content.parts)} part(s)")
                        for part_idx, part in enumerate(event.content.parts):
                            if part.text:
                                agent_name = event.author
                                text_preview = part.text[:100].replace('\n', ' ')
                                logger.info(f"  - Part {part_idx+1}: {len(part.text)} chars - '{text_preview}...'")
                                
                                # Parse JSON from agent response
                                parsed_json = extract_json_from_text(part.text)
                                if parsed_json:
                                    logger.info(f"  ✓ Successfully parsed JSON from {agent_name} (keys: {list(parsed_json.keys())})")
                                else:
                                    logger.warning(f"  ✗ Failed to parse JSON from {agent_name}, storing raw text")
                                    # Store raw text as fallback
                                    if 'team' in agent_name:
                                        agent_analyses['team_analysis'] = {"raw_response": part.text}
                                        logger.info(f"  → Stored raw text for team_analysis")
                                    elif 'market' in agent_name:
                                        agent_analyses['market_analysis'] = {"raw_response": part.text}
                                        logger.info(f"  → Stored raw text for market_analysis")
                                    elif 'product' in agent_name:
                                        agent_analyses['product_analysis'] = {"raw_response": part.text}
                                        logger.info(f"  → Stored raw text for product_analysis")
                                    elif 'competition' in agent_name:
                                        agent_analyses['competition_analysis'] = {"raw_response": part.text}
                                        logger.info(f"  → Stored raw text for competition_analysis")
                                    elif 'synthesis' in agent_name:
                                        agent_analyses['synthesis_analysis'] = {"raw_response": part.text}
                                        logger.info(f"  → Stored raw text for synthesis_analysis")
                            else:
                                logger.warning(f"[Event {idx+1}/{len(events)}] Event has no content or parts")
                    else:
                        logger.warning(f"[Event {idx+1}/{len(events)}] Event has no content or parts")
                    
                    # Store agent analysis based on agent type
                    if agent_name == 'files_analysis_agent':
                        files_analysis_result = parsed_json
                        agent_analyses['files_analysis'] = parsed_json
                    elif agent_name == 'team_agent':
                        agent_analyses['team_analysis'] = parsed_json
                    elif agent_name == 'market_agent':
                        agent_analyses['market_analysis'] = parsed_json
                    elif agent_name == 'product_agent':
                        agent_analyses['product_analysis'] = parsed_json
                    elif agent_name == 'competition_agent':
                        agent_analyses['competition_analysis'] = parsed_json
                    elif agent_name == 'synthesis_agent':
                        synthesis_result = parsed_json
                        agent_analyses['synthesis_analysis'] = parsed_json
                
                # Get final session state for any additional results
                final_state = session.state if session else {}
                session_agent_results = final_state.get("agent_results", {})
                
                # Merge session results with event results
                for agent_name, session_result in session_agent_results.items():
                    if agent_name == 'files_analysis_agent' and 'files_analysis' not in agent_analyses:
                        files_analysis_result = session_result
                        agent_analyses['files_analysis'] = session_result
                    elif agent_name == 'team_agent' and 'team_analysis' not in agent_analyses:
                        agent_analyses['team_analysis'] = session_result
                    elif agent_name == 'market_agent' and 'market_analysis' not in agent_analyses:
                        agent_analyses['market_analysis'] = session_result
                    elif agent_name == 'product_agent' and 'product_analysis' not in agent_analyses:
                        agent_analyses['product_analysis'] = session_result
                    elif agent_name == 'competition_agent' and 'competition_analysis' not in agent_analyses:
                        agent_analyses['competition_analysis'] = session_result
                    elif agent_name == 'synthesis_agent' and 'synthesis_analysis' not in agent_analyses:
                        synthesis_result = session_result
                        agent_analyses['synthesis_analysis'] = session_result
                
                logger.info(f"Agent workflow completed. Events: {len(events)}, Agent analyses: {list(agent_analyses.keys())}")
                logger.info(f"Files analysis result available: {files_analysis_result is not None}")
                logger.info(f"Synthesis result available: {synthesis_result is not None}")
                
                # Update progress
                AnalysisService._update_progress(analysis_id, 90, "Processing results")
                
                # Extract scores from individual analyses
                scores = {}
                for analysis_type, analysis_data in agent_analyses.items():
                    if isinstance(analysis_data, dict) and 'overall_score' in analysis_data:
                        scores[analysis_type] = analysis_data['overall_score']
                        logger.info(f"Extracted score from {analysis_type}: {analysis_data['overall_score']}")
                
                # Extract final results from synthesis or calculate from individual analyses
                if synthesis_result:
                    # Use synthesis result directly (new structured schema)
                    overall_score = synthesis_result.get('overall_investability_score', 7.5)
                    investment_rec_obj = synthesis_result.get('investment_recommendation', {})
                    if isinstance(investment_rec_obj, dict):
                        investment_rec = investment_rec_obj.get('recommendation', 'PASS')
                        confidence = investment_rec_obj.get('confidence_level', 0.8)
                    else:
                        investment_rec = str(investment_rec_obj) if investment_rec_obj else 'PASS'
                        confidence = synthesis_result.get('confidence_level', 0.8)
                    
                    exec_summary = synthesis_result.get('executive_summary', 'AI analysis completed successfully')
                    investment_memo = synthesis_result.get('investment_memo', 'Detailed analysis available in structured results')
                    
                    # Extract individual scores from synthesis result
                    team_score = synthesis_result.get('team_score', scores.get('team_analysis', 7.0))
                    market_score = synthesis_result.get('market_score', scores.get('market_analysis', 7.0))
                    product_score = synthesis_result.get('product_score', scores.get('product_analysis', 7.0))
                    competition_score = synthesis_result.get('competition_score', scores.get('competition_analysis', 7.0))
                    
                    logger.info(f"Using synthesis result with overall_score: {overall_score}")
                else:
                    # Fallback: calculate from individual analyses
                    logger.info("No synthesis result, calculating from individual analyses")
                    team_score = scores.get('team_analysis', 7.0)
                    market_score = scores.get('market_analysis', 7.0)
                    product_score = scores.get('product_analysis', 7.0)
                    competition_score = scores.get('competition_analysis', 7.0)
                    
                    # Calculate weighted overall score
                    overall_score = (team_score * 0.25) + (market_score * 0.25) + (product_score * 0.30) + (competition_score * 0.20)
                    
                    # Determine investment recommendation
                    if overall_score >= 8.0:
                        investment_rec = "Strong Buy"
                    elif overall_score >= 7.0:
                        investment_rec = "Buy"
                    elif overall_score >= 6.0:
                        investment_rec = "Hold"
                    else:
                        investment_rec = "Pass"
                    
                    confidence = 0.8
                    exec_summary = f"AI analysis completed with overall score of {overall_score:.1f}"
                    investment_memo = "Detailed analysis available in structured results"
                
                logger.info("=" * 80)
                logger.info(f"✓ ANALYSIS COMPLETE - Overall Score: {overall_score:.2f}")
                logger.info(f"  - Investment Recommendation: {investment_rec}")
                logger.info(f"  - Confidence Level: {confidence:.2f}")
                logger.info(f"  - Team Score: {team_score:.2f}")
                logger.info(f"  - Market Score: {market_score:.2f}")
                logger.info(f"  - Product Score: {product_score:.2f}")
                logger.info(f"  - Competition Score: {competition_score:.2f}")
                logger.info("=" * 80)
                logger.info("STARTING BIGQUERY STORAGE...")
                logger.info("=" * 80)
                
                # Store results in BigQuery with new structured schema
                if bq_client and bq_client.is_available:
                    logger.info("BigQuery client is available, proceeding with storage...")
                    try:
                        # Update is_latest flags before inserting new analysis
                        try:
                            update_sql = f"""
                            UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
                            SET is_latest = false
                            WHERE startup_id = '{startup_id}'
                            """
                            bq_client.query(update_sql)
                            logger.info(f"Updated previous analyses to is_latest=false for startup {startup_id}")
                        except Exception as e:
                            logger.warning(f"Failed to update is_latest flags: {e}")
                        
                        completed_at = datetime.utcnow()
                        analysis_row = {
                            "id": analysis_id,
                            "startup_id": startup_id,
                            "request_id": analysis_id,
                            "status": "completed",
                            "is_latest": True,
                            "overall_score": float(overall_score),
                            "team_score": float(team_score),
                            "market_score": float(market_score),
                            "product_score": float(product_score),
                            "competition_score": float(competition_score),
                            "investment_recommendation": str(investment_rec),
                            "confidence_level": float(confidence),
                            "executive_summary": exec_summary,
                            "investment_memo": investment_memo,
                            # Individual structured analyses (new schema)
                            "files_analysis": agent_analyses.get('files_analysis'),
                            "team_analysis": agent_analyses.get('team_analysis'),
                            "market_analysis": agent_analyses.get('market_analysis'),
                            "product_analysis": agent_analyses.get('product_analysis'),
                            "competition_analysis": agent_analyses.get('competition_analysis'),
                            "synthesis_analysis": agent_analyses.get('synthesis_analysis'),
                            "started_at": active_analyses[analysis_id]["started_at"],
                            "completed_at": completed_at.isoformat(),
                            "total_duration_seconds": (completed_at - datetime.fromisoformat(active_analyses[analysis_id]["started_at"])).total_seconds(),
                            "version": 2  # Updated version for new schema
                        }
                        logger.info(f"Preparing to insert analysis row into BigQuery...")
                        logger.info(f"  - Analysis ID: {analysis_id}")
                        logger.info(f"  - Startup ID: {startup_id}")
                        logger.info(f"  - Overall Score: {analysis_row['overall_score']}")
                        logger.info(f"  - Agent analyses included: {[k for k, v in analysis_row.items() if k.endswith('_analysis') and v is not None]}")
                        
                        bq_client.insert_rows("analyses", [analysis_row])
                        
                        logger.info("=" * 80)
                        logger.info(f"✓ BIGQUERY STORAGE SUCCESSFUL")
                        logger.info(f"  - Analysis ID: {analysis_id}")
                        logger.info(f"  - Duration: {analysis_row['total_duration_seconds']:.2f} seconds")
                        logger.info("=" * 80)
                        
                        # Create AI-generated questions in Firestore from synthesis result
                        if synthesis_result and 'questions' in synthesis_result and not is_reanalysis:
                            try:
                                questions_list = synthesis_result.get('questions', [])
                                logger.info(f"Found {len(questions_list)} AI-generated questions in synthesis result")
                                
                                questions_created = 0
                                high_priority_count = 0
                                
                                for question_data in questions_list:
                                    # Each question should have: question_text, category, priority
                                    if isinstance(question_data, dict):
                                        question_text = question_data.get('question_text', '')
                                        category = question_data.get('category', 'business_model')
                                        priority = question_data.get('priority', 'medium')
                                        
                                        if question_text:
                                            # Create question in Firestore
                                            created_question = fs_client.create_question({
                                                "startup_id": startup_id,
                                                "asked_by": "Younicorn Analysis",
                                                "asked_by_name": "Younicorn Analysis",
                                                "asked_by_role": "system",
                                                "question_text": question_text,
                                                "category": category,
                                                "priority": priority,
                                                "status": "pending",
                                                "is_ai_generated": True,
                                                "tags": ["ai_generated", "analysis", category],
                                                "analysis_id": analysis_id
                                            })
                                            logger.info(f"Created AI-generated question for startup {startup_id}: {question_text[:50]}...")
                                            questions_created += 1
                                            if priority == 'high':
                                                high_priority_count += 1
                                            
                                            # Create activity feed entry for the AI-generated question
                                            try:
                                                fs_client.create_activity(
                                                    startup_id=startup_id,
                                                    user_id="ai_system",
                                                    user_name="Younicorn Analysis",
                                                    activity_type="ai_question_generated",
                                                    description=f"Younicorn Analysis generated a {priority} priority question about {category}",
                                                    metadata={
                                                        "question_id": created_question.get('id'),
                                                        "category": category,
                                                        "priority": priority,
                                                        "analysis_id": analysis_id
                                                    }
                                                )
                                            except Exception as activity_error:
                                                logger.error(f"Failed to create activity for AI question: {activity_error}")
                                
                                logger.info(f"Successfully created {questions_created} AI-generated questions for startup {startup_id}")
                                
                                # Send a single notification to the founder about all AI-generated questions
                                if questions_created > 0:
                                    try:
                                        # Get the founder's user_id from startup_data
                                        founder_id = startup_data.get('submitted_by')
                                        if founder_id:
                                            notification_message = f"Younicorn Analysis added {questions_created} question{'s' if questions_created > 1 else ''} for your startup"
                                            if high_priority_count > 0:
                                                notification_message += f" ({high_priority_count} high priority)"
                                            
                                            fs_client.create_notification(
                                                user_id=founder_id,
                                                type="ai_questions_generated",
                                                title="Younicorn Analysis Questions Ready",
                                                message=notification_message,
                                                related_id=analysis_id,
                                                related_type="analysis"
                                            )
                                            logger.info(f"Sent notification to founder {founder_id} about {questions_created} AI-generated questions")
                                    except Exception as notif_error:
                                        logger.error(f"Failed to send notification about AI questions: {notif_error}")
                                
                            except Exception as e:
                                logger.error(f"Failed to create AI-generated questions in Firestore: {e}")
                                # Continue execution even if question creation fails
                        
                        # Update active analysis
                        AnalysisService._update_status(
                            analysis_id,
                            "completed",
                            progress=100,
                            completed_at=completed_at.isoformat(),
                            overall_score=overall_score,
                            investment_recommendation=investment_rec,
                            confidence_level=confidence,
                            executive_summary=exec_summary,
                            investment_memo=investment_memo
                        )
                        
                        logger.info(f"Completed AI analysis for startup {startup_id}")
                        
                    except Exception as e:
                        logger.error(f"Failed to store analysis in BigQuery: {e}")
                        # Continue execution even if BigQuery fails
                        
            except ImportError as e:
                logger.warning(f"Could not import real agents, using simulation: {e}")
                # Fallback to simulation
                await AnalysisService.simulate_agent_analysis(analysis_id, startup_data)
                return
                
            except Exception as e:
                logger.error(f"Error in real agent analysis: {e}")
                logger.error(f"Error type: {type(e)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Fallback to simulation
                await AnalysisService.simulate_agent_analysis(analysis_id, startup_data)
                return
        
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            if bq_client and bq_client.is_available:
                try:
                    error_update_sql = f"""
                        UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
                        SET status = 'error',
                            last_updated = CURRENT_TIMESTAMP()
                        WHERE id = @analysis_id
                    """
                    bq_client.query(error_update_sql, {
                        "analysis_id": analysis_id
                    })
                except Exception as update_error:
                    logger.error(f"Failed to update analysis status to error: {update_error}")
            
            # Update active analysis with error
            AnalysisService._update_status(analysis_id, "failed", error=str(e))

    @staticmethod
    async def simulate_agent_analysis(analysis_id: str, startup_data: Dict[str, Any]):
        """Fallback simulation when real agents are not available."""
        logger.info("Running simulated agent analysis with new structured schema")
        
        # Simulate analysis steps
        steps = [
            ("Analyzing team composition", 20),
            ("Evaluating market opportunity", 40), 
            ("Assessing product viability", 60),
            ("Analyzing competition", 80),
            ("Generating final recommendation", 100)
        ]
        
        for step_name, progress in steps:
            AnalysisService._update_progress(analysis_id, progress, step_name)
            await asyncio.sleep(1)  # Simulate processing time
        
        # Create simulated structured results
        simulated_team_analysis = {
            "overall_score": 7.0,
            "founder_market_fit_score": 7.5,
            "team_completeness_score": 6.5,
            "experience_score": 7.0,
            "leadership_score": 7.0,
            "executive_summary": "Strong founding team with relevant experience",
            "founder_analysis": "Experienced founder with domain expertise",
            "team_composition": "Small but focused team",
            "experience_assessment": "Relevant industry experience",
            "leadership_evaluation": "Strong leadership capabilities",
            "strengths": ["Domain expertise", "Technical skills"],
            "weaknesses": ["Small team size"],
            "red_flags": [],
            "recommendations": ["Expand technical team"],
            "supporting_evidence": ["Previous startup experience"],
            "confidence_level": 0.8
        }
        
        simulated_market_analysis = {
            "overall_score": 8.0,
            "market_size_score": 8.5,
            "market_growth_score": 8.0,
            "market_timing_score": 7.5,
            "market_accessibility_score": 7.5,
            "market_sizing": {
                "tam_usd": 50000000000,
                "sam_usd": 5000000000,
                "som_usd": 500000000,
                "tam_methodology": "Top-down analysis",
                "sam_methodology": "Bottom-up analysis", 
                "som_methodology": "Market penetration model",
                "market_growth_rate": 15.0,
                "market_maturity": "Growth"
            },
            "executive_summary": "Large and growing market opportunity",
            "market_definition": "Well-defined target market",
            "market_trends": "Positive market trends",
            "market_timing": "Good market timing",
            "regulatory_environment": "Favorable regulatory environment",
            "opportunities": ["Market expansion", "New segments"],
            "challenges": ["Competition", "Market saturation"],
            "trends_supporting": ["Digital transformation"],
            "trends_opposing": ["Economic uncertainty"],
            "supporting_evidence": ["Market research", "Industry reports"],
            "confidence_level": 0.85
        }
        
        simulated_synthesis = {
            "overall_investability_score": 7.5,
            "team_score": 7.0,
            "market_score": 8.0,
            "product_score": 7.5,
            "competition_score": 7.0,
            "executive_summary": "Promising investment opportunity with strong market potential",
            "investment_thesis": "Strong market opportunity with experienced team",
            "investment_memo": "Recommended for investment based on market size and team capabilities",
            "investment_recommendation": {
                "recommendation": "Buy",
                "confidence_level": 0.8,
                "rationale": "Strong fundamentals with good growth potential"
            },
            "confidence_level": 0.8
        }
        
        # Store simulated results in BigQuery
        if bq_client and bq_client.is_available:
            try:
                # Update is_latest flags before inserting
                try:
                    startup_id_val = startup_data.get("startup_id", "unknown")
                    update_sql = f"""
                    UPDATE `{bq_client.project_id}.{bq_client.dataset_id}.analyses`
                    SET is_latest = false
                    WHERE startup_id = '{startup_id_val}'
                    """
                    bq_client.query(update_sql)
                except Exception as e:
                    logger.warning(f"Failed to update is_latest flags in simulation: {e}")
                
                completed_at = datetime.utcnow()
                analysis_row = {
                    "id": analysis_id,
                    "startup_id": startup_data.get("startup_id", "unknown"),
                    "request_id": analysis_id,
                    "status": "completed",
                    "is_latest": True,
                    "overall_score": 7.5,
                    "team_score": 7.0,
                    "market_score": 8.0,
                    "product_score": 7.5,
                    "competition_score": 7.0,
                    "investment_recommendation": "Buy",
                    "confidence_level": 0.8,
                    "executive_summary": "Simulated analysis completed successfully",
                    "investment_memo": "Simulated investment memo with positive recommendation",
                    # Individual structured analyses (simulated)
                    "team_analysis": simulated_team_analysis,
                    "market_analysis": simulated_market_analysis,
                    "product_analysis": None,  # Could add simulated product analysis
                    "competition_analysis": None,  # Could add simulated competition analysis
                    "synthesis_analysis": simulated_synthesis,
                    "started_at": active_analyses[analysis_id]["started_at"],
                    "completed_at": completed_at.isoformat(),
                    "total_duration_seconds": (completed_at - datetime.fromisoformat(active_analyses[analysis_id]["started_at"])).total_seconds(),
                    "version": 2
                }
                bq_client.insert_rows("analyses", [analysis_row])
                logger.info(f"Successfully stored simulated analysis results in BigQuery for {analysis_id}")
                
            except Exception as e:
                logger.error(f"Failed to store simulated analysis in BigQuery: {e}")
        
        # Update active analysis
        AnalysisService._update_status(
            analysis_id,
            "completed",
            progress=100,
            completed_at=datetime.utcnow(),
            overall_score=7.5,
            investment_recommendation="Buy",
            confidence_level=0.8,
            executive_summary="Simulated analysis completed successfully",
            investment_memo="Simulated investment memo"
        )
        
        logger.info(f"Completed simulated analysis for {analysis_id}")

    @staticmethod
    def get_analysis_progress(analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get the current progress of an analysis."""
        with active_analyses_lock:
            return active_analyses.get(analysis_id).copy() if analysis_id in active_analyses else None

    @staticmethod
    def cancel_analysis(analysis_id: str) -> bool:
        """Cancel a running analysis."""
        with active_analyses_lock:
            if analysis_id in active_analyses:
                active_analyses[analysis_id]["status"] = "cancelled"
                return True
            return False

# Global analysis service instance
analysis_service = AnalysisService()
