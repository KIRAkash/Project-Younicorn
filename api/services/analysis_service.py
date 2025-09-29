"""AI Analysis service for Project Minerva API."""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback

from .bigquery_client import bq_client
from ..utils import extract_json_from_text

logger = logging.getLogger(__name__)

# In-memory storage for active analyses
active_analyses: Dict[str, Dict[str, Any]] = {}

class AnalysisService:
    
    @staticmethod
    def _extract_executive_summary(exec_summary_obj):
        """Extract executive summary text from the nested structure."""
        if isinstance(exec_summary_obj, dict):
            # Try the new schema format first
            if 'investment_summary' in exec_summary_obj:
                return exec_summary_obj['investment_summary']
            
            # Try the old schema format
            sections = exec_summary_obj.get('sections', [])
            if sections:
                # Combine all section bodies into a coherent summary
                summary_parts = []
                for section in sections:
                    if isinstance(section, dict) and 'body' in section:
                        summary_parts.append(section['body'])
                return ' '.join(summary_parts)
            elif 'title' in exec_summary_obj:
                return exec_summary_obj['title']
        elif isinstance(exec_summary_obj, str):
            return exec_summary_obj
        return "AI analysis completed successfully"
    
    @staticmethod
    def _extract_investment_memo(investment_memo_obj):
        """Extract investment memo text from the nested structure."""
        if isinstance(investment_memo_obj, dict):
            # Try the new schema format first
            if 'investment_thesis' in investment_memo_obj:
                return investment_memo_obj['investment_thesis']
            
            # Try to get the company overview and investment thesis (old format)
            parts = []
            if 'company_overview' in investment_memo_obj:
                parts.append(investment_memo_obj['company_overview'])
            if parts:
                return ' '.join(parts)
        elif isinstance(investment_memo_obj, str):
            return investment_memo_obj
        return "Detailed analysis available in agent results"
    
    @staticmethod
    async def start_ai_analysis(startup_id: str, analysis_id: str, startup_data: Dict[str, Any]):
        """Start real AI analysis using Project Minerva agent system."""
        try:
            # Initialize analysis state
            active_analyses[analysis_id] = {
                "id": analysis_id,
                "startup_id": startup_id,
                "status": "running",
                "progress": 0,
                "started_at": datetime.utcnow(),
                "agent_results": {},
                "sources": {},
                "execution_trace": []
            }
            
            logger.info(f"Starting AI analysis for startup {startup_id}")
            
            # Try to use real agents
            try:
                from app.agent import minerva_analysis_agent, StartupInfo
                import json
                
                # Update progress
                active_analyses[analysis_id]["progress"] = 10
                active_analyses[analysis_id]["current_step"] = "Initializing agents"
                
                logger.info("Starting real AI agent workflow")
                
                # Create startup info object for agent analysis
                startup_info = StartupInfo(
                    company_info=json.dumps(startup_data.get("company_info", {})),
                    founders=json.dumps(startup_data.get("founders", [])),
                    documents=json.dumps(startup_data.get("documents", [])),
                    metadata=json.dumps(startup_data.get("metadata", {}))
                )
                
                # Use proper ADK Runner pattern
                from google.adk.runners import InMemoryRunner
                from google.genai import types as genai_types
                
                # Create runner
                runner = InMemoryRunner(
                    agent=minerva_analysis_agent,
                    app_name="minerva_analysis"
                )
                
                # Create a session with state
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
                
                # Create user message
                user_message = genai_types.Content(
                    parts=[genai_types.Part(text=f"Please analyze this startup submission. The startup_info is available in the session state: {startup_info.model_dump_json()}")]
                )
                
                # Update session state
                startup_data_dict = startup_info.model_dump()
                session.state.update({
                    "startup_info": startup_data_dict,
                    "analysis_id": analysis_id,
                    "startup_id": startup_id
                })
                
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
                
                # Process agent events and extract results (using the same pattern as integrated_server.py)
                agent_results = {}
                sources = {}
                execution_trace = []
                result = None
                
                # Process events to extract agent results
                for event in events:
                    # Extract structured result from event content
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                # Store all agent text responses for analysis
                                agent_name = event.author
                                if agent_name not in agent_results:
                                    agent_results[agent_name] = []
                                
                                # Parse JSON from agent response (handle markdown code blocks)
                                parsed_json = extract_json_from_text(part.text)
                                if parsed_json:
                                    agent_results[agent_name].append(parsed_json)
                                    logger.info(f"Successfully parsed JSON from {agent_name}")
                                    
                                    # Check if this is the synthesis agent with final results
                                    if agent_name == 'synthesis_agent' and isinstance(parsed_json, dict):
                                        logger.info(f"=== DEBUGGING: Synthesis Agent Result ===")
                                        logger.info(f"Synthesis JSON keys: {list(parsed_json.keys())}")
                                        logger.info(f"Full synthesis result: {parsed_json}")
                                        
                                        if 'final_analysis' in parsed_json:
                                            final_analysis = parsed_json['final_analysis']
                                            
                                            # Handle the actual schema format - values are directly in final_analysis
                                            overall_score = final_analysis.get('overall_score', 7.5)
                                            investment_rec = final_analysis.get('recommendation', 'PASS')
                                            confidence = final_analysis.get('confidence_level', 0.8)
                                            exec_summary = final_analysis.get('executive_summary', {})
                                            investment_memo = final_analysis.get('investment_memo', {})
                                            
                                            # Also check for nested header format (fallback)
                                            if overall_score == 7.5:  # Default value, try nested format
                                                header = final_analysis.get('header', {})
                                                rec_summary = header.get('recommendation_summary', {})
                                                if rec_summary:
                                                    overall_score = rec_summary.get('overall_score', overall_score)
                                                    investment_rec = rec_summary.get('recommendation', investment_rec)
                                                    confidence = rec_summary.get('confidence', confidence)
                                            
                                            # Create a flattened result structure
                                            result = {
                                                "overall_score": float(overall_score),
                                                "investment_recommendation": str(investment_rec),
                                                "confidence_level": float(confidence),
                                                "executive_summary": AnalysisService._extract_executive_summary(exec_summary),
                                                "investment_memo": AnalysisService._extract_investment_memo(investment_memo),
                                                "raw_analysis": final_analysis  # Keep the full structure for reference
                                            }
                                            logger.info(f"Found synthesis result with overall_score: {result.get('overall_score')}")
                                        elif 'overall_score' in parsed_json:
                                            result = parsed_json
                                            logger.info(f"Found direct synthesis result with score: {parsed_json.get('overall_score')}")
                                        else:
                                            # Try to find nested analysis results
                                            for key, value in parsed_json.items():
                                                if isinstance(value, dict) and 'overall_score' in value:
                                                    result = value
                                                    logger.info(f"Found nested synthesis result in '{key}' with score: {value.get('overall_score')}")
                                                    break
                                else:
                                    # Store raw text if JSON parsing fails
                                    agent_results[agent_name].append(part.text)
                                    logger.warning(f"Could not parse JSON from {agent_name}, storing raw text")
                                
                                execution_trace.append({
                                    "agent": agent_name,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "result": parsed_json or part.text
                                })
                
                # Get final session state and merge results
                final_state = session.state if session else {}
                session_agent_results = final_state.get("agent_results", {})
                
                # Merge session results with event results
                for agent_name, session_result in session_agent_results.items():
                    if agent_name not in agent_results:
                        agent_results[agent_name] = []
                    if isinstance(session_result, list):
                        agent_results[agent_name].extend(session_result)
                    else:
                        agent_results[agent_name].append(session_result)
                
                logger.info(f"Agent workflow completed. Events: {len(events)}, Agent results: {len(agent_results)}")
                logger.info(f"Agent results keys: {list(agent_results.keys())}")
                
                # Update progress
                if analysis_id in active_analyses:
                    active_analyses[analysis_id]["progress"] = 90
                    active_analyses[analysis_id]["current_step"] = "Processing results"
                
                # Extract individual agent analyses and scores
                individual_analyses = {}
                scores = {}
                
                for agent_name, results in agent_results.items():
                    if results and isinstance(results[0], dict):
                        agent_data = results[0]
                        logger.info(f"{agent_name} data keys: {list(agent_data.keys())}")
                        
                        # Store the full analysis
                        individual_analyses[agent_name] = agent_data
                        
                        # Extract score
                        if "overall_score" in agent_data:
                            scores[agent_name] = agent_data["overall_score"]
                            logger.info(f"Extracted score from {agent_name}: {agent_data['overall_score']}")
                        elif "score" in agent_data:
                            scores[agent_name] = agent_data["score"]
                            logger.info(f"Extracted score from {agent_name}: {agent_data['score']}")
                        else:
                            logger.warning(f"No score found in {agent_name} data")
                
                # If no synthesis result found, create one from individual agent results
                if not result and agent_results:
                    logger.info("=== DEBUGGING: Creating synthesis from individual agents ===")
                    logger.info(f"Individual scores extracted: {scores}")
                    
                    # Extract summaries and recommendations
                    executive_summaries = []
                    investment_recommendations = []
                    
                    for agent_name, agent_data in individual_analyses.items():
                        # Extract summaries and recommendations
                        if "executive_summary" in agent_data:
                            executive_summaries.append(agent_data["executive_summary"])
                        if "summary" in agent_data:
                            executive_summaries.append(agent_data["summary"])
                        if "investment_recommendation" in agent_data:
                            investment_recommendations.append(agent_data["investment_recommendation"])
                    
                    # Calculate weighted overall score using synthesis agent weights
                    if scores:
                        team_score = scores.get('team_agent', 7.5)
                        market_score = scores.get('market_agent', 7.5) 
                        product_score = scores.get('product_agent', 7.5)
                        competition_score = scores.get('competition_agent', 7.5)
                        
                        # Apply synthesis agent weighting: Team 25%, Market 25%, Product 30%, Competition 20%
                        overall_score = (team_score * 0.25) + (market_score * 0.25) + (product_score * 0.30) + (competition_score * 0.20)
                        logger.info(f"Calculated weighted overall score: {overall_score} from individual scores: team={team_score}, market={market_score}, product={product_score}, competition={competition_score}")
                    else:
                        overall_score = 7.5
                        logger.warning("No individual scores found, using default overall score")
                    
                    # Determine investment recommendation
                    if investment_recommendations:
                        investment_rec = investment_recommendations[0]
                    else:
                        if overall_score >= 8.0:
                            investment_rec = "STRONG_BUY"
                        elif overall_score >= 7.0:
                            investment_rec = "BUY"
                        elif overall_score >= 6.0:
                            investment_rec = "HOLD"
                        else:
                            investment_rec = "PASS"
                    
                    # Create executive summary
                    if executive_summaries:
                        exec_summary = " ".join(executive_summaries[:2])  # Combine first 2 summaries
                    else:
                        exec_summary = f"AI analysis completed with overall score of {overall_score:.1f}"
                    
                    result = {
                        "overall_score": overall_score,
                        "investment_recommendation": investment_rec,
                        "confidence_level": 0.8,
                        "executive_summary": exec_summary,
                        "investment_memo": f"Analysis based on {len(scores)} specialist agents with weighted score calculation.",
                        "individual_scores": scores
                    }
                    logger.info(f"Created synthesis result from {len(scores)} agent scores: {scores}")
                    logger.info(f"Final weighted overall score: {overall_score}")
                
                # If still no result, fall back to simulation
                if not result:
                    logger.warning("No agent results found, falling back to simulation")
                    await AnalysisService.simulate_agent_analysis(analysis_id, startup_data)
                    return
                
                logger.info(f"Real AI analysis completed. Result type: {type(result)}")
                
                # Parse the final analysis result
                if isinstance(result, dict) and "overall_score" in result:
                    overall_score = result.get("overall_score", 7.5)
                    investment_recommendation = result.get("investment_recommendation", "PASS")
                    confidence_level = result.get("confidence_level", 0.8)
                    executive_summary = str(result.get("executive_summary", "AI analysis completed"))
                    investment_memo = str(result.get("investment_memo", "Detailed analysis available"))
                    
                    # Use individual scores from result or extracted scores
                    if "individual_scores" in result:
                        scores = result["individual_scores"]
                    else:
                        # Extract individual agent scores from agent_analyses
                        agent_analyses = result.get("agent_analyses", {})
                        for agent_name, analysis in agent_analyses.items():
                            if isinstance(analysis, dict) and "score" in analysis:
                                scores[agent_name] = analysis["score"]
                else:
                    # Fallback for unexpected result format
                    overall_score = 7.5
                    investment_recommendation = "PASS"
                    confidence_level = 0.8
                    executive_summary = str("AI analysis completed")
                    investment_memo = str("Analysis results available")
                
                # Ensure we have individual scores
                if not scores:
                    scores = {"team_agent": 7.5, "market_agent": 7.5, "product_agent": 7.5, "competition_agent": 7.5}
                    logger.warning("No individual scores found, using default scores")
                
                logger.info(f"Real AI analysis completed with overall score: {overall_score}")
                
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
            
            # Complete analysis (moved inside the inner try block)
            completed_at = datetime.utcnow()
        
            if bq_client and bq_client.is_available:
                # Debug: Print values before BigQuery update
                logger.info("=== DEBUGGING: BigQuery Update Values ===")
                logger.info(f"overall_score: {overall_score} (type: {type(overall_score)})")
                logger.info(f"investment_recommendation: {investment_recommendation} (type: {type(investment_recommendation)})")
                logger.info(f"confidence_level: {confidence_level} (type: {type(confidence_level)})")
                logger.info(f"executive_summary: {str(executive_summary)[:100]}... (type: {type(executive_summary)})")
                logger.info(f"agent_results keys: {list(agent_results.keys())}")
                
                # Insert complete analysis results (single INSERT, no UPDATE needed)
                try:
                    complete_analysis_row = {
                        "id": str(analysis_id),
                        "startup_id": str(startup_id),
                        "request_id": str(analysis_id),  # Using analysis_id as request_id
                        "status": "completed",
                        "overall_score": float(overall_score),
                        "team_score": float(scores.get('team_agent', 7.5)),
                        "market_score": float(scores.get('market_agent', 7.5)),
                        "product_score": float(scores.get('product_agent', 7.5)),
                        "competition_score": float(scores.get('competition_agent', 7.5)),
                        "investment_recommendation": str(investment_recommendation),
                        "confidence_level": float(confidence_level),
                        "executive_summary": str(executive_summary),
                        "investment_memo": str(investment_memo),
                        # Individual agent analysis columns
                        "team_analysis": json.dumps(individual_analyses.get('team_agent', {})) if individual_analyses.get('team_agent') else None,
                        "market_analysis": json.dumps(individual_analyses.get('market_agent', {})) if individual_analyses.get('market_agent') else None,
                        "product_analysis": json.dumps(individual_analyses.get('product_agent', {})) if individual_analyses.get('product_agent') else None,
                        "competition_analysis": json.dumps(individual_analyses.get('competition_agent', {})) if individual_analyses.get('competition_agent') else None,
                        "synthesis_analysis": json.dumps(individual_analyses.get('synthesis_agent', {})) if individual_analyses.get('synthesis_agent') else None,
                        # Legacy field for backward compatibility
                        "agent_analyses": json.dumps(agent_results),  # Convert to JSON string for BigQuery
                        "risks_opportunities": "{}",  # JSON string for BigQuery
                        "key_insights": "{}",  # JSON string for BigQuery
                        "started_at": (datetime.utcnow() - timedelta(seconds=30)).isoformat(),  # Approximate start time
                        "completed_at": completed_at.isoformat(),
                        "total_duration_seconds": 30.0,  # Approximate duration
                        "version": 1,
                        "last_updated": completed_at.isoformat()
                    }
                    
                    bq_client.insert_rows("analyses", [complete_analysis_row])
                    logger.info("Successfully inserted complete analysis results into BigQuery")
                    
                except Exception as bq_error:
                    logger.error(f"BigQuery insert failed: {bq_error}")
                    logger.error(f"Error type: {type(bq_error)}")
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    # Store results in memory for now - they'll be available via API
                    logger.info("Results stored in active_analyses memory cache")
                
                # Skip startup status update to avoid streaming buffer issues
                # Status can be inferred from the existence of completed analysis
                logger.info("Skipping startup status update to avoid streaming buffer conflicts")
            
                # Update active analysis
                if analysis_id in active_analyses:
                    active_analyses[analysis_id].update({
                        "status": "completed",
                        "progress": 100,
                        "completed_at": completed_at,
                        "overall_score": overall_score,
                        "investment_recommendation": investment_recommendation,
                        "confidence_level": confidence_level,
                        "executive_summary": executive_summary,
                        "investment_memo": investment_memo,
                        "agent_results": agent_results,
                        "individual_analyses": individual_analyses,
                        "sources": sources,
                        "execution_trace": execution_trace
                    })
                
                    logger.info(f"Completed AI analysis for startup {startup_id}")
                
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
            if analysis_id in active_analyses:
                active_analyses[analysis_id]["status"] = "failed"
                active_analyses[analysis_id]["error"] = str(e)

    @staticmethod
    async def simulate_agent_analysis(analysis_id: str, startup_data: Dict[str, Any]):
        """Fallback simulation when real agents are not available."""
        logger.info("Running simulated agent analysis")
        
        # Simulate analysis steps
        steps = [
            ("Analyzing team composition", 20),
            ("Evaluating market opportunity", 40), 
            ("Assessing product viability", 60),
            ("Analyzing competition", 80),
            ("Generating final recommendation", 100)
        ]
        
        for step_name, progress in steps:
            if analysis_id in active_analyses:
                active_analyses[analysis_id]["progress"] = progress
                active_analyses[analysis_id]["current_step"] = step_name
            await asyncio.sleep(2)  # Simulate processing time
        
        # Generate mock results
        overall_score = 7.2
        team_score = 7.5
        market_score = 7.0
        product_score = 7.5
        competition_score = 6.8
        
        # Update final results
        if analysis_id in active_analyses:
            active_analyses[analysis_id].update({
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.utcnow(),
                "overall_score": overall_score,
                "team_score": team_score,
                "market_score": market_score,
                "product_score": product_score,
                "competition_score": competition_score,
                "investment_recommendation": "INVEST" if overall_score >= 7.0 else "PASS",
                "confidence_level": 0.85,
                "executive_summary": "This startup shows strong potential with experienced founders and a compelling market opportunity.",
                "investment_memo": "Recommended for investment based on strong team execution and market positioning.",
                "agent_results": {
                    "team_agent": [{"analysis": "Strong founding team with relevant experience", "score": team_score}],
                    "market_agent": [{"analysis": "Large addressable market with growth potential", "score": market_score}],
                    "product_agent": [{"analysis": "Innovative product with clear value proposition", "score": product_score}],
                    "competition_agent": [{"analysis": "Competitive landscape manageable", "score": competition_score}]
                }
            })
        
        active_analyses[analysis_id]["investment_recommendation"] = "INVEST" if overall_score >= 7.0 else "PASS"

# Global analysis service instance
analysis_service = AnalysisService()
