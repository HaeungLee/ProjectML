"""
API Routes
"""

from fastapi import APIRouter

from .chat import router as chat_router
from .tools import router as tools_router
from .health import router as health_router

router = APIRouter()

router.include_router(health_router, tags=["Health"])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(tools_router, prefix="/tools", tags=["Tools"])


