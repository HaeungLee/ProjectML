"""
Intent Parser Agent

Stage 1: 사용자 의도 파악 및 Tool 선택
"""

import json
from dataclasses import dataclass, field
from typing import Optional

from ..llm.provider import LLMProvider


@dataclass
class IntentResult:
    """의도 파악 결과"""
    tool_needed: bool = False
    tool_name: Optional[str] = None
    parameters: dict = field(default_factory=dict)
    confidence: float = 0.0


class IntentParserAgent:
    """
    의도 파악 에이전트
    
    사용자 메시지를 분석하여:
    1. Tool이 필요한지 판단
    2. 어떤 Tool을 사용할지 선택
    3. 파라미터 추출
    """
    
    AVAILABLE_TOOLS = {
        "google_search": {
            "description": "웹 검색",
            "keywords": ["검색", "찾아", "알려", "뭐야", "어디"],
        },
        "send_email": {
            "description": "이메일 전송",
            "keywords": ["이메일", "메일", "보내", "전송"],
        },
        "get_calendar": {
            "description": "캘린더 조회",
            "keywords": ["일정", "캘린더", "스케줄", "약속"],
        },
        "create_event": {
            "description": "일정 생성",
            "keywords": ["일정 추가", "일정 만들", "약속 잡"],
        },
        "github_issues": {
            "description": "GitHub 이슈 관리",
            "keywords": ["깃허브", "github", "이슈", "issue"],
        },
        "notion_page": {
            "description": "Notion 페이지 관리",
            "keywords": ["노션", "notion", "문서"],
        },
    }
    
    def __init__(self, llm: LLMProvider):
        self.llm = llm
    
    async def parse(self, message: str, context: dict) -> IntentResult:
        """
        사용자 메시지 의도 파악
        
        Args:
            message: 사용자 메시지
            context: 대화 컨텍스트
        
        Returns:
            IntentResult: 의도 파악 결과
        """
        # 1. 빠른 키워드 매칭 (속도 최적화)
        quick_match = self._quick_keyword_match(message)
        if quick_match:
            return quick_match
        
        # 2. LLM을 통한 정밀 분석
        return await self._llm_parse(message, context)
    
    def _quick_keyword_match(self, message: str) -> Optional[IntentResult]:
        """
        빠른 키워드 매칭
        
        간단한 요청은 LLM 없이 처리 (지연시간 최소화)
        """
        message_lower = message.lower()
        
        for tool_name, info in self.AVAILABLE_TOOLS.items():
            for keyword in info["keywords"]:
                if keyword in message_lower:
                    return IntentResult(
                        tool_needed=True,
                        tool_name=tool_name,
                        parameters={"query": message},  # 기본 파라미터
                        confidence=0.7,
                    )
        
        return None
    
    async def _llm_parse(self, message: str, context: dict) -> IntentResult:
        """
        LLM을 통한 정밀 의도 파악
        """
        tools_desc = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.AVAILABLE_TOOLS.items()
        ])
        
        prompt = f"""사용자 메시지를 분석하여 어떤 Tool을 사용해야 하는지 판단하세요.

사용 가능한 Tools:
{tools_desc}

사용자 메시지: {message}

다음 JSON 형식으로만 답하세요:
{{
    "tool_needed": true/false,
    "tool_name": "tool_name 또는 null",
    "parameters": {{}},
    "confidence": 0.0-1.0
}}
"""
        
        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 일관성 높게
            )
            
            # JSON 파싱
            result = json.loads(response)
            
            return IntentResult(
                tool_needed=result.get("tool_needed", False),
                tool_name=result.get("tool_name"),
                parameters=result.get("parameters", {}),
                confidence=result.get("confidence", 0.5),
            )
            
        except (json.JSONDecodeError, KeyError):
            # 파싱 실패 → Tool 불필요로 처리
            return IntentResult(tool_needed=False)


