"""
Moonlight AI Core - Main Application
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 라이프사이클 관리"""
    settings = get_settings()
    print(f"🌙 {settings.app_name} v{settings.app_version} 시작...")
    print(f"   - Debug: {settings.debug}")
    print(f"   - LLM: {settings.default_model}")
    
    # TODO: 초기화 작업
    # - Database 연결
    # - Redis 연결
    # - Tool Registry 로드
    # - gRPC 클라이언트 (Voice Service)
    
    yield
    
    # 정리 작업
    print("🌙 Moonlight AI Core 종료...")


def create_app() -> FastAPI:
    """FastAPI 앱 생성"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="달빛 비서 시스템 - AI Core",
        lifespan=lifespan,
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite, React
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 라우터 등록
    app.include_router(api_router, prefix="/api")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


