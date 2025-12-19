"""
Chat API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ..agents.orchestrator import AgentOrchestrator

router = APIRouter()


class ChatRequest(BaseModel):
    """채팅 요청"""
    user_id: str = "dev_user"
    session_id: Optional[str] = None
    message: str
    enable_tools: bool = True


class ChatResponse(BaseModel):
    """채팅 응답"""
    message: str
    tool_used: Optional[str] = None
    success: bool = True


# 글로벌 Orchestrator (나중에 DI로 변경)
orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Orchestrator 싱글톤"""
    global orchestrator
    if orchestrator is None:
        orchestrator = AgentOrchestrator()
    return orchestrator


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    대화 처리 (REST)
    
    - Multi-agent 시스템으로 처리
    - Tool Calling 자동 처리
    """
    orch = get_orchestrator()
    
    result = await orch.process(
        user_id=request.user_id,
        message=request.message,
        session_id=request.session_id,
        enable_tools=request.enable_tools,
    )
    
    return ChatResponse(
        message=result.message,
        tool_used=result.tool_used,
        success=result.success,
    )


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    """
    대화 처리 (WebSocket)
    
    - 스트리밍 응답 지원
    - 실시간 통신
    """
    await websocket.accept()
    
    orch = get_orchestrator()
    
    try:
        while True:
            # 메시지 수신
            data = await websocket.receive_json()
            
            # 처리
            result = await orch.process(
                user_id=data.get("user_id", "dev_user"),
                message=data["message"],
                session_id=data.get("session_id"),
                enable_tools=data.get("enable_tools", True),
            )
            
            # 응답 전송
            await websocket.send_json({
                "message": result.message,
                "tool_used": result.tool_used,
                "success": result.success,
            })
            
    except WebSocketDisconnect:
        print("WebSocket 연결 종료")


