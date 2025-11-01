"""API routes for Project Younicorn."""

from .auth import router as auth_router
from .startups import router as startups_router
from .analysis import router as analysis_router
from .dashboard import router as dashboard_router
from .firebase_auth import router as firebase_auth_router
from .founder import router as founder_router
from .images import router as images_router
from .beacon import router as beacon_router

__all__ = [
    "auth_router", 
    "startups_router", 
    "analysis_router", 
    "dashboard_router",
    "firebase_auth_router",
    "founder_router",
    "images_router",
    "beacon_router"
]
