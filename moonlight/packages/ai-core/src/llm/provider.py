"""
LLM Provider

OpenRouter API를 통한 다양한 LLM 모델 호출
Tool Calling 지원
"""

from typing import Optional
import httpx

from ..config import get_settings


class LLMProvider:
    """
    LLM Provider
    
    OpenRouter API를 통해 다양한 모델 호출:
    - Google Gemini (무료)
    - Claude
    - GPT-4
    - Llama
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.default_model = settings.default_model
        
        # HTTP 클라이언트
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://moonlight.local",  # OpenRouter 요구
                "X-Title": "Moonlight AI",
            },
            timeout=30.0,
        )
    
    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[list[dict]] = None,
    ) -> str:
        """
        채팅 완성
        
        Args:
            messages: 대화 메시지 리스트
            model: 사용할 모델 (기본: default_model)
            temperature: 창의성 (0.0-1.0)
            max_tokens: 최대 토큰 수
            tools: Tool 정의 리스트
        
        Returns:
            str: 생성된 응답
        """
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Tool Calling
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            choice = data["choices"][0]
            
            # Tool Call 처리
            if choice.get("message", {}).get("tool_calls"):
                return self._format_tool_calls(choice["message"]["tool_calls"])
            
            # 일반 응답
            return choice["message"]["content"]
            
        except httpx.HTTPStatusError as e:
            print(f"LLM API 오류: {e.response.status_code}")
            return "죄송합니다, 일시적인 오류가 발생했습니다."
        except Exception as e:
            print(f"LLM 호출 오류: {e}")
            return "죄송합니다, 응답을 생성하는 데 실패했습니다."
    
    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        model: Optional[str] = None,
    ) -> dict:
        """
        Tool Calling을 포함한 채팅
        
        Returns:
            dict: {
                "content": str,
                "tool_calls": list[dict] | None
            }
        """
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.3,  # Tool 호출은 낮은 temperature
        }
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            message = data["choices"][0]["message"]
            
            return {
                "content": message.get("content"),
                "tool_calls": message.get("tool_calls"),
            }
            
        except Exception as e:
            print(f"Tool Calling 오류: {e}")
            return {"content": None, "tool_calls": None}
    
    def _format_tool_calls(self, tool_calls: list[dict]) -> str:
        """Tool Call 응답 포맷팅"""
        if not tool_calls:
            return ""
        
        call = tool_calls[0]
        func = call.get("function", {})
        return f"[Tool: {func.get('name')}] {func.get('arguments')}"
    
    async def close(self):
        """클라이언트 정리"""
        await self.client.aclose()


