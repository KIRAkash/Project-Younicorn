"""API routes for Project Minerva."""

from .auth import router as auth_router
from .startups import router as startups_router
from .analysis import router as analysis_router
from .dashboard import router as dashboard_router

__all__ = ["auth_router", "startups_router", "analysis_router", "dashboard_router"]
