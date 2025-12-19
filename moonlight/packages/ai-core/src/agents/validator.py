"""
Parameter Validator Agent

Stage 2+3: 파라미터 검증 및 실행 확인 (병합)
"""

import json
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, EmailStr, ValidationError

from ..llm.provider import LLMProvider


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool = False
    tool_name: Optional[str] = None
    parameters: dict = None
    clarification_message: Optional[str] = None


# Tool별 Pydantic 모델 정의
class SendEmailParams(BaseModel):
    """이메일 전송 파라미터"""
    to: EmailStr
    subject: str
    body: str


class GoogleSearchParams(BaseModel):
    """검색 파라미터"""
    query: str


class CalendarEventParams(BaseModel):
    """캘린더 이벤트 파라미터"""
    title: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None


class GitHubIssueParams(BaseModel):
    """GitHub 이슈 파라미터"""
    repo: str
    title: str
    body: Optional[str] = None


# Tool → Pydantic 모델 매핑
PARAM_MODELS = {
    "send_email": SendEmailParams,
    "google_search": GoogleSearchParams,
    "create_event": CalendarEventParams,
    "github_issues": GitHubIssueParams,
}


class ParameterValidatorAgent:
    """
    파라미터 검증 에이전트
    
    Stage 2+3 병합:
    - Pydantic으로 타입/형식 검증
    - 누락된 파라미터 보완 (LLM)
    - 최종 실행 가능 여부 확인
    """
    
    def __init__(self, llm: LLMProvider):
        self.llm = llm
    
    async def validate(
        self,
        tool_name: str,
        parameters: dict,
        context: dict,
    ) -> ValidationResult:
        """
        파라미터 검증 및 보완
        
        Args:
            tool_name: Tool 이름
            parameters: 추출된 파라미터
            context: 대화 컨텍스트
        
        Returns:
            ValidationResult: 검증 결과
        """
        # 1. Pydantic 검증 시도
        model = PARAM_MODELS.get(tool_name)
        
        if model:
            try:
                validated = model(**parameters)
                return ValidationResult(
                    is_valid=True,
                    tool_name=tool_name,
                    parameters=validated.model_dump(),
                )
            except ValidationError as e:
                # 2. 누락된 파라미터 확인
                missing = self._extract_missing_fields(e)
                
                if missing:
                    # 3. LLM으로 명확화 메시지 생성
                    clarification = await self._generate_clarification(
                        tool_name, missing, context
                    )
                    return ValidationResult(
                        is_valid=False,
                        clarification_message=clarification,
                    )
                
                # 형식 오류
                return ValidationResult(
                    is_valid=False,
                    clarification_message="주인님, 입력 형식이 올바르지 않은 것 같아요.",
                )
        
        # 모델 없는 Tool → 기본 통과
        return ValidationResult(
            is_valid=True,
            tool_name=tool_name,
            parameters=parameters,
        )
    
    def _extract_missing_fields(self, error: ValidationError) -> list[str]:
        """Pydantic 오류에서 누락된 필드 추출"""
        missing = []
        for err in error.errors():
            if err["type"] == "missing":
                missing.append(err["loc"][0])
        return missing
    
    async def _generate_clarification(
        self,
        tool_name: str,
        missing_fields: list[str],
        context: dict,
    ) -> str:
        """명확화 요청 메시지 생성"""
        field_names = {
            "to": "받는 사람 이메일",
            "subject": "제목",
            "body": "내용",
            "query": "검색어",
            "title": "제목",
            "start_time": "시작 시간",
            "end_time": "종료 시간",
            "repo": "저장소 이름",
        }
        
        missing_korean = [
            field_names.get(f, f) for f in missing_fields
        ]
        
        if len(missing_korean) == 1:
            return f"주인님, {missing_korean[0]}을(를) 알려주시겠어요?"
        else:
            fields_str = ", ".join(missing_korean)
            return f"주인님, {fields_str}을(를) 알려주시겠어요?"


