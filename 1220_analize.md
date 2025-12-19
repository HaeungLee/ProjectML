# 1220 Moonlight 구현 현황 분석 (as-is)

작성일: 2025-12-20  
기준 문서: `1214_최종설계.md`, `1214_firstcommit.md`, `1214_plan.md`  
대상 코드: `moonlight/`

---

## 1) 결론 요약

- **"E2E(웹→AI Core→LLM)"는 거의 연결 가능**: Web UI가 `/api/chat` REST 호출을 하고, AI Core가 `/api/chat` 엔드포인트를 제공함.
- **다만 "Tool Calling"은 아직 실제 실행이 아니라 Mock**: 오케스트레이터의 `_execute_tool`과 Tools API `/api/tools/execute`가 Mock 응답.
- **Memory/RAG/Constitution/Voice는 스켈레톤 단계**: 패키지/폴더만 있고 핵심 로직이 비어있음.
- **WebSocket 경로는 잠재적 불일치**: AI Core WS는 `/api/chat/ws`인데, Vite 프록시는 `/ws`만 ws 프록시로 설정되어 있음.

---

## 2) 레포 구조 구현도 (문서 대비)

문서(1214)에서 제안한 모노레포 구조와 비교:

- `moonlight/docker/` ✅ 존재
  - `docker-compose.yml` ✅ Postgres(pgvector) + Redis 구성 완료
  - `init.sql` ✅ 존재
- `moonlight/shared/proto/` ✅ 존재
  - `agent.proto`, `voice.proto` ✅ 존재
- `moonlight/packages/ai-core/` ✅ 존재
  - FastAPI 엔트리포인트/설정/에이전트 뼈대 ✅
  - Tools/Memory/Constitution 폴더는 존재하지만 내용은 거의 없음 ✅/⬜
- `moonlight/packages/web-ui/` ✅ 존재
  - Vite+React 기본 채팅 UI ✅
- `moonlight/packages/voice-service/` ✅ 존재
  - 스켈레톤(폴더/버전) 수준 ✅
- `moonlight/packages/gateway/` ❌ 없음 (문서 Phase 4에서 Rust Gateway 예정)

---

## 3) 서비스별 구현 현황

### 3.1 AI Core (Python/FastAPI) — "동작 뼈대는 있음"

**구현됨(✅)**
- FastAPI 앱/라이프사이클: `moonlight/packages/ai-core/src/main.py`
  - CORS 설정 포함
  - `/api` 라우터 등록
- 설정(Pydantic Settings): `moonlight/packages/ai-core/src/config.py`
  - Postgres/Redis URL 구성
  - OpenRouter 설정
- API 라우팅: `moonlight/packages/ai-core/src/api/__init__.py`
  - Health: `/api/health`, `/api/`
  - Chat: `/api/chat`(REST), `/api/chat/ws`(WS)
  - Tools: `/api/tools`, `/api/tools/execute`
- Multi-Agent 핵심 뼈대: `moonlight/packages/ai-core/src/agents/`
  - `orchestrator.py`: Stage1(Intent) + Stage2+3(Validate) 흐름 구현
  - `intent_parser.py`: 키워드 빠른 매칭 + LLM JSON 파싱
  - `validator.py`: Tool별 Pydantic 모델 일부 + 누락 파라미터 명확화 메시지 생성
- OpenRouter 호출 래퍼: `moonlight/packages/ai-core/src/llm/provider.py`
  - `/chat/completions` 호출
  - tool_calls가 오면 포맷팅 문자열로 반환(현재는 "실행 루프"까지는 미구현)

**미구현/리스크(⬜/⚠️)**
- Tool 실행이 Mock:
  - `AgentOrchestrator._execute_tool()`가 "완료되었습니다" 문자열만 반환
  - `api/tools.py`의 `/execute`도 Mock
- Tool Calling "루프" 미구현:
  - `LLMProvider.chat()`가 tool_calls를 문자열로 포맷팅만 함
  - 오케스트레이터가 tool_calls를 받아 실제 Tool 실행→결과를 다시 LLM에 넣는 "agentic loop"가 없음
- Tool Registry/Plugin Loader 없음 (1214 설계의 핵심 구조 미구현)
- DB/Redis 연결 및 Memory 저장 로직 없음 (lifespan에 TODO로만 존재)
- gRPC(Voice Service) 클라이언트 연결 없음 (lifespan TODO)
- 고위험 Tool 확인(Stage3 분리)은 "메시지 생성"만 있고, 실제 사용자 확인 플로우(승인/취소 state machine)가 없음

---

### 3.2 Web UI (React/Vite) — "REST 기반 채팅은 준비됨"

**구현됨(✅)**
- 간단한 채팅 UI: `moonlight/packages/web-ui/src/App.tsx`
  - 메시지 리스트/입력/로딩
  - `/api/chat`로 POST
  - `tool_used`가 있으면 배지 표시
- Vite 프록시: `moonlight/packages/web-ui/vite.config.ts`
  - `/api` → `http://localhost:8000`

**미구현/리스크(⬜/⚠️)**
- WebSocket 프록시 경로 불일치 가능:
  - Vite는 `/ws`만 WS 프록시
  - 서버 WS는 `/api/chat/ws`
  - 현재 App은 WS를 사용하지 않아서 즉시 문제는 아니지만, WS 전환 시 수정 필요

---

### 3.3 Voice Service (Python) — "폴더만 준비"

**구현됨(✅)**
- 패키지/폴더 구조: `moonlight/packages/voice-service/src/stt`, `tts`

**미구현(⬜)**
- gRPC 서버/프로토콜 구현
- STT/TTS 실제 엔진(API/모델) 연동

---

### 3.4 Infra (Docker: Postgres+pgvector, Redis) — "구성 완료"

**구현됨(✅)**
- `moonlight/docker/docker-compose.yml`에 Postgres(pgvector) + Redis 존재
- healthcheck 포함

**미구현(⬜)**
- AI Core에서 DB/Redis를 실제 사용(세션/메모리/벡터 저장)하는 코드

---

## 4) 문서 목표(Phase 1) 대비 현재 진척도

Phase 1 성공 기준:
- [ ] 웹 UI에서 텍스트 대화 가능
- [ ] Function Calling 작동 확인
- [ ] Latency < 5초 측정

현재 상태 판단:
- 텍스트 대화: **부분 달성(✅/⚠️)**
  - 서버 실행 + OpenRouter API 키 세팅만 되면 REST 대화는 동작할 확률 높음
  - 다만 tool_calls 반환 포맷이 단순 문자열이라 UX/로직이 불완전할 수 있음
- Function Calling: **미달(⬜)**
  - tool 정의 전달/실행/결과 반영의 루프가 없음
- Latency 측정: **미달(⬜)**
  - 측정/로그/메트릭 없음

---

## 5) 다음 구현(우선순위) — "가장 작은 E2E"부터

### P0: 바로 E2E 동작 확인 (최단 루트)

1) **AI Core 실행/환경변수 연결**
- `OPENROUTER_API_KEY` 설정 후 AI Core가 실제 응답을 내는지 확인
- 목표: Web UI → `/api/chat` → OpenRouter 응답까지

2) **Web UI ↔ AI Core REST 연결 확인**
- 이미 `/api` 프록시는 있음
- 목표: 브라우저에서 메시지 보내면 응답이 표시

3) **WebSocket 경로 정리(선택)**
- WS를 쓸 계획이면, Vite ws 프록시를 `/api/chat/ws`에 맞추거나 App이 `/ws`를 사용하도록 정합성 맞추기

---

### P1: Tool Calling "작동 확인" (Mock를 벗어나기)

문서 목표인 "Function Calling 작동 확인"을 위해 필요한 최소 구현:

1) **Tool Registry 최소 버전**
- 하드코딩 1~2개 Tool부터 시작(예: `google_search`는 결과를 "모의"로 하더라도 구조만)
- Tool 스키마(JSON Schema) + 실행 함수 매핑

2) **Agentic Loop(필수)**
- LLM에 `tools`를 제공
- tool_calls 발생 시:
  - Tool 실행
  - Tool 결과를 `role=tool` 메시지로 다시 LLM에 넣고 최종 답변 생성

3) **고위험 Tool 승인 플로우 최소화**
- MVP는 "승인 요구" 메시지까지만 하고, 실제 실행은 "승인 응답"을 한 번 더 받아야 실행되도록 상태를 들고 가는 방식이 필요
  - (지금은 TODO 주석대로 바로 실행되는 상태)

---

### P2: Memory/RAG 착수(Phase 3 전초)

- Redis에 세션 대화 저장(TTL)부터 시작
- Postgres(pgvector)에 대화 임베딩 저장/유사도 검색
- 오케스트레이터에 "최근 대화/유사 대화"를 컨텍스트로 주입

---

## 6) 체크리스트 (다음 세션에 바로 할 일)

- [ ] Docker up: Postgres/Redis 기동
- [ ] AI Core `.env` 설정(OPENROUTER_API_KEY)
- [ ] AI Core 실행 후 `/api/health` 확인
- [ ] Web UI 실행 후 채팅 REST 왕복 확인
- [ ] Tool Calling을 위한 최소 Tool Registry + agentic loop 구현
- [ ] WebSocket 경로 정합성 조정(WS를 쓸 경우)

---

## 7) 참고: 현 상태에서 보이는 작은 설계-구현 갭

- Tool System(Plugin/Registry) 설계는 문서에 있지만, 코드에는 아직 없음
- Memory/Constitution/Voice는 문서 계획 대비 폴더만 존재
- WebSocket은 서버 경로(`/api/chat/ws`)와 프록시(`/ws`)가 어긋나 있어, WS 전환 시 정리 필요
