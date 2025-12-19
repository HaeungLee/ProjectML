"""
Health Check Endpoints
"""

from fastapi import APIRouter

from ..config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """서버 상태 확인"""
    settings = get_settings()
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🌙 Moonlight AI Core",
        "description": "압도적이지 않지만 달빛처럼",
    }


