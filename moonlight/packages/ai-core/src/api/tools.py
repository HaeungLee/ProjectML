"""
Tools API Endpoints
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ToolInfo(BaseModel):
    """Tool 정보"""
    name: str
    description: str
    category: str
    enabled: bool


class ToolExecuteRequest(BaseModel):
    """Tool 실행 요청"""
    tool_name: str
    parameters: dict
    user_id: str = "dev_user"


class ToolExecuteResponse(BaseModel):
    """Tool 실행 응답"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: int = 0


@router.get("")
async def list_tools() -> list[ToolInfo]:
    """
    사용 가능한 Tool 목록
    """
    # TODO: Tool Registry에서 동적 로드
    return [
        ToolInfo(
            name="google_search",
            description="Google 검색을 수행합니다",
            category="search",
            enabled=True,
        ),
        ToolInfo(
            name="send_email",
            description="이메일을 전송합니다",
            category="communication",
            enabled=True,
        ),
        ToolInfo(
            name="get_calendar",
            description="캘린더 일정을 조회합니다",
            category="productivity",
            enabled=True,
        ),
        ToolInfo(
            name="github_issues",
            description="GitHub 이슈를 관리합니다",
            category="development",
            enabled=True,
        ),
    ]


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(request: ToolExecuteRequest) -> ToolExecuteResponse:
    """
    Tool 직접 실행
    """
    import time
    
    start = time.time()
    
    # TODO: 실제 Tool 실행 로직
    # 지금은 Mock 응답
    
    execution_time = int((time.time() - start) * 1000)
    
    return ToolExecuteResponse(
        success=True,
        result=f"Tool '{request.tool_name}' 실행 완료 (Mock)",
        execution_time_ms=execution_time,
    )


@router.get("/{tool_name}")
async def get_tool_info(tool_name: str) -> ToolInfo:
    """
    특정 Tool 정보 조회
    """
    # TODO: Tool Registry에서 조회
    return ToolInfo(
        name=tool_name,
        description=f"{tool_name} Tool입니다",
        category="general",
        enabled=True,
    )


