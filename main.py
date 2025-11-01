#!/usr/bin/env python3
"""Main FastAPI application for Project Younicorn."""

import logging
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.services import fs_client
from api.routes import (
    auth_router, 
    startups_router, 
    analysis_router, 
    dashboard_router,
    firebase_auth_router,
    founder_router,
    images_router,
    beacon_router
)
from api.routes.startup_status import router as startup_status_router
from api.routes.questions import router as questions_router
from api.routes.notifications import router as notifications_router
from api.routes.activity import router as activity_router
from api.routes.reanalysis import router as reanalysis_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(firebase_auth_router)
app.include_router(founder_router)
app.include_router(startups_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)
app.include_router(images_router)
app.include_router(startup_status_router)
app.include_router(questions_router)
app.include_router(notifications_router)
app.include_router(activity_router)
app.include_router(reanalysis_router)
app.include_router(beacon_router)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        fs_client.initialize()
        logger.info("✅ Firestore client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firestore client: {e}")
        # Don't fail startup, just log the error

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down services...")

# Health check endpoints
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "Project Younicorn Integrated API",
        "version": settings.api_version,
        "status": "healthy"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "integrated-api",
        "version": settings.api_version
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
