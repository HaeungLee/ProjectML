# 🎯 음성 비서 시스템 v2 - 실현 가능성 분석 및 초기 기획
**작성일**: 2025-11-18
**목적**: 기존 Arion 프로젝트 분석 및 차세대 아키텍처 설계

---

## 📊 Executive Summary

### 현재 상황
- ✅ **기존 Arion**: Product 레벨 근처까지 구현 완료
- ✅ **핵심 강점**: MCP 서버 완벽 구현, Agent2Agent 시스템, 99-100% 정확도
- ❌ **주요 문제**: 과도한 복잡도 (Backend 4개), React Native 실패, API 비용
- 🎯 **목표**: 더 나은 구조, 확장 가능, 낮은 latency, 모바일 성공

### 핵심 결정 사항
- **Rust**: Gateway만 사용 (전체 Rust는 다음 프로젝트)
- **AI 프레임워크**: Python 생태계 유지 (LangChain/RAG)
- **STT**: Whisper → Hugging Face 최신 모델
- **TTS**: ElevenLabs (로컬 TTS는 RAM 80GB 활용 시 고려)
- **Frontend**: React Native + PWA 하이브리드
- **Focus**: "도전적이지만 가능" 영역에 집중, MVP 확실히 성공

---

## 1. 기존 Arion 프로젝트 분석

### 1.1 아키텍처 현황

```
현재 구조 (4개 Backend):
┌─────────────────────────────────────┐
│  React (Web) + React Native (Mobile) │
└────────────────┬────────────────────┘
                 │
     ┌───────────┼───────────┬─────────────┐
     ▼           ▼           ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐
│ Spring  │ │ Node.js │ │ Voice   │ │  Python  │
│  Boot   │ │ Agent   │ │ Proxy   │ │ STT/TTS  │
│  :8080  │ │ :3000   │ │ :8083   │ │  :8082   │
│         │ │ :8081   │ │         │ │          │
│ (Auth)  │ │(Agentica)│ │ (CORS)  │ │(Whisper) │
└─────────┘ └─────────┘ └─────────┘ └──────────┘
```

### 1.2 주요 강점

#### ✅ MCP 서버 완벽 구현
- Gmail, Google Calendar, Notion, GitHub, KakaoMap 통합
- 각 서비스별 독립적 connector 구조
- LLM Function Calling으로 자연어 명령 처리

#### ✅ Agent2Agent 시스템 (5개 Agent)
- 기능별 Agent 분리
- 모델 교체 유연성 (언제든 더 나은 모델로 변경)
- Agent 간 협업 구조

#### ✅ 검증 시스템 (3단계)
- 1차 검증: 75% 정확도
- 2차 검증: 99% 정확도
- 3차 검증: 100% 정확도
- **핵심**: Validation Feedback으로 오류 자동 수정

#### ✅ 추가 기능
- 쇼핑몰 연동
- Web Search
- 검색 기능

### 1.3 주요 문제점

#### ❌ 과도한 복잡도
- Backend 4개 → 개발/배포/유지보수 복잡
- 마이크로서비스 오버엔지니어링
- React Native 통합 실패 (복잡도가 원인)

#### ❌ 병목 지점
- **직렬 처리**: STT → Agent → TTS
- **Node.js 한계**: 단일 스레드 이벤트 루프
- **세션 관리**: Redis 단일 인스턴스 의존
- **메모리 비효율**: 전체 음성 버퍼링

#### ❌ Agentica 프레임워크 제약
- RAG/LangChain 통합 시 구조 60% 수정 필요
- 프레임워크 lock-in
- 커스터마이징 한계

#### ❌ API 비용
- 현재 가장 큰 문제
- OpenAI API 사용량 최적화 필요
- TTS (ElevenLabs) 비용

---

## 2. 새 아키텍처 설계

### 2.1 실현 가능성 평가

#### 🟢 실현 가능 (High Confidence - 85-95%)

| 목표 | 가능성 | 이유 |
|------|--------|------|
| **Rust Gateway** | 95% | Actix-web/Tokio 성숙, WebSocket 완벽 지원 |
| **스트리밍 STT** | 90% | Hugging Face 모델, Deepgram 선택지 |
| **병렬 처리** | 95% | Tokio async runtime 자연스러운 구현 |
| **PWA 구현** | 90% | Service Worker, Web Speech API 표준 |
| **React Native** | 85% | 단순화된 구조로 Expo 통합 용이 |

#### 🟡 도전적이지만 가능 (Medium Challenge - 70-80%) ← **우리 목표**

| 목표 | 가능성 | 전략 |
|------|--------|------|
| **Rust AI Orchestration** | 70% | Rust에서 Python 모듈 호출 (PyO3) 또는 HTTP API 분리 |
| **메모리 최적화** | 75% | 단계적 최적화, 초기엔 안전한 방식 → 점진적 Zero-copy |
| **VAD (Voice Activity Detection)** | 80% | Silero-VAD (ONNX) 또는 Python 서비스 분리 |
| **로컬 Wake Word** | 70% | MVP 제외, Phase 2에서 추가 |

#### 🔴 다음 프로젝트로 이관

| 목표 | 가능성 | 이유 |
|------|--------|------|
| **전체 Rust 구현** | 40% | LLM 프레임워크 직접 개발 필요, Python 생태계 압도적 우위 |
| **실시간 TTS 스트리밍** | 60% | ElevenLabs 스트리밍 지원하나 지연 존재 |

### 2.2 추천 하이브리드 아키텍처

```
┌─────────────────────────────────────────────────────┐
│         Frontend Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │  React Native   │  │   React PWA     │          │
│  │  (Expo)         │  │  + Service      │          │
│  │  iOS/Android    │  │    Worker       │          │
│  └─────────────────┘  └─────────────────┘          │
└───────────────────┬─────────────────────────────────┘
                    │ WebSocket (Binary Protocol)
                    ▼
┌─────────────────────────────────────────────────────┐
│      🦀 Rust Gateway (Actix-Web + Tokio)            │
│  ┌─────────────────────────────────────────────┐   │
│  │  - WebSocket 라우팅 & 연결 관리              │   │
│  │  - 음성 청킹 & 스트리밍 파이프라인           │   │
│  │  - Circuit Breaker & Rate Limiting          │   │
│  │  - JWT 인증 & 세션 관리                      │   │
│  │  - Zero-copy 메모리 관리                     │   │
│  │  - 로드 밸런싱 & 헬스 체크                   │   │
│  └─────────────────────────────────────────────┘   │
└──────┬──────────┬──────────┬──────────┬────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
  ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────────┐
  │  STT   │ │  TTS   │ │  Auth   │ │   AI Core    │
  │Service │ │Service │ │ Service │ │   Service    │
  │(Python)│ │(Python)│ │ (Rust)  │ │  (Python)    │
  └────┬───┘ └───┬────┘ └────┬────┘ └──────┬───────┘
       │         │           │              │
       ▼         ▼           ▼              ▼
  ┌─────────────────────────────────────────────────┐
  │  Hugging   ElevenLabs   Redis      LangChain    │
  │   Face       API        Cache      + RAG        │
  │   Model                           Vector DB     │
  └─────────────────────────────────────────────────┘
```

### 2.3 서비스 축소 전략

**기존 4개 → 새로 3개 (25% 감소)**

| Before | After | 이유 |
|--------|-------|------|
| Spring Boot (Auth) | Rust Gateway 통합 | JWT는 Rust로 충분, 복잡도 감소 |
| Node.js Agent | Python AI Service | Python 생태계 활용, Agentica 제거 |
| Voice Proxy | Rust Gateway 통합 | CORS/Timeout 처리 Gateway에서 |
| Python STT/TTS | Voice Service 유지 | 변경 없음 |

**결과**:
- ✅ 배포 단순화
- ✅ 운영 비용 절감
- ✅ 디버깅 용이
- ✅ React Native 통합 성공 가능성 ↑

---

## 3. 기술 스택 결정

### 3.1 Core Stack

#### 🦀 Rust Layer (Gateway Only)
```toml
[dependencies]
actix-web = "4.4"
actix-ws = "0.2"
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
jsonwebtoken = "9.2"
redis = { version = "0.24", features = ["tokio-comp"] }
```

**역할**:
- WebSocket 서버
- 음성 스트리밍 파이프라인
- JWT 인증
- 로드 밸런싱
- Circuit Breaker

#### 🐍 Python Layer (AI + Voice)

**AI Service** (LangChain/RAG):
```python
fastapi==0.108.0
langchain==0.1.0
openai==1.6.0
qdrant-client==1.7.0
chromadb==0.4.22
```

**Voice Service**:
```python
# STT - Hugging Face (Whisper 대체)
transformers==4.36.0
torch==2.1.0
# TTS
elevenlabs==0.2.26
```

#### ⚛️ Frontend Layer

**React Native** (Expo):
```json
{
  "expo": "~50.0.0",
  "react-native": "0.73.0",
  "react-native-webrtc": "118.0.0"
}
```

**React PWA**:
```json
{
  "vite": "^5.0.0",
  "react": "^18.2.0",
  "workbox-precaching": "^7.0.0"
}
```

### 3.2 Database & Infrastructure

```yaml
# Vector DB
qdrant:
  version: "1.7.0"
  storage: "local"  # 비용 절감

# Cache
redis:
  version: "7.2"
  persistence: true

# Monitoring
prometheus: "2.48"
grafana: "10.2"
```

---

## 4. MVP 로드맵 (4-6주)

### Phase 1: Foundation (Week 1-2)

#### Week 1: Rust Gateway
```rust
Day 1-2: Actix-web WebSocket 서버
  ├─ WebSocket echo 서버
  ├─ JWT 미들웨어
  └─ 기본 라우팅

Day 3-4: 음성 스트리밍 파이프라인
  ├─ Binary 청킹
  ├─ 버퍼 관리
  └─ Python 서비스 연동 (HTTP)

Day 5-7: 인증 & 세션
  ├─ JWT 발급/검증
  ├─ Redis 세션 저장
  └─ Rate limiting
```

#### Week 2: Python Services
```python
Day 8-10: Voice Service
  ├─ Hugging Face STT 통합
  ├─ ElevenLabs TTS 통합
  ├─ FastAPI 서버
  └─ 로컬 TTS (RAM 80GB 활용)

Day 11-14: AI Service
  ├─ OpenAI API 통합
  ├─ 기존 MCP 서버 마이그레이션
  │  ├─ Gmail
  │  ├─ Calendar
  │  ├─ Notion
  │  ├─ GitHub
  │  └─ KakaoMap
  ├─ Agent2Agent 시스템 재구축
  └─ 검증 3단계 시스템
```

### Phase 2: Integration (Week 3-4)

#### Week 3: Frontend
```typescript
Day 15-17: React Native (Expo)
  ├─ WebSocket 연결
  ├─ 음성 녹음 UI
  ├─ 채팅 인터페이스
  └─ 기본 설정 화면

Day 18-21: React PWA
  ├─ Service Worker
  ├─ 오프라인 지원
  ├─ Push 알림
  └─ 반응형 UI
```

#### Week 4: E2E Testing
```
Day 22-24: 통합 테스트
  ├─ 음성 → 텍스트 → LLM → TTS
  ├─ MCP 서버 기능 검증
  ├─ Agent2Agent 동작 확인
  └─ 모바일 앱 테스트

Day 25-28: 성능 측정
  ├─ Latency 프로파일링
  ├─ 메모리 사용량
  ├─ API 호출 비용 추적
  └─ 병목 지점 식별
```

### Phase 3: Optimization (Week 5-6)

#### Week 5: Performance
```
Day 29-31: Latency 최적화
  ├─ 스트리밍 STT
  ├─ 병렬 처리
  │  ├─ STT + Context Load 동시
  │  ├─ TTS 사전 준비
  │  └─ 캐싱 전략
  └─ Zero-copy 메모리 (점진적)

Day 32-35: RAG 시스템
  ├─ Vector DB (Qdrant) 셋업
  ├─ LangChain 통합
  ├─ 의미적 검색
  └─ 대화 컨텍스트 관리
```

#### Week 6: Production Ready
```
Day 36-38: 모니터링
  ├─ Prometheus 메트릭
  ├─ Grafana 대시보드
  ├─ 로그 집계 (Loki)
  └─ 에러 트래킹 (Sentry)

Day 39-42: Deployment
  ├─ Docker Compose 최적화
  ├─ CI/CD 파이프라인
  ├─ 스테이징 환경
  └─ 프로덕션 배포 준비
```

---

## 5. 핵심 기능 상세 설계

### 5.1 MCP 서버 마이그레이션 전략

**기존 Agentica 구조 → 새 구조**

```python
# 기존 (Agentica)
@connector(name="gmail")
async def gmail_connector(params):
    # Agentica 프레임워크 의존
    pass

# 새 구조 (LangChain Tools)
from langchain.tools import BaseTool

class GmailTool(BaseTool):
    name = "gmail_send"
    description = "이메일을 전송합니다"

    def _run(self, to: str, subject: str, body: str):
        # Gmail API 호출
        return send_email(to, subject, body)

    async def _arun(self, *args, **kwargs):
        # 비동기 버전
        return await async_send_email(*args, **kwargs)
```

**마이그레이션 체크리스트**:
- [ ] Gmail: 읽기, 전송, 검색, 라벨
- [ ] Calendar: 조회, 생성, 수정, 삭제
- [ ] Notion: 페이지 생성, 데이터베이스 조작
- [ ] GitHub: 이슈, PR, 저장소 관리
- [ ] KakaoMap: 검색, 길찾기
- [ ] 쇼핑몰 연동
- [ ] Web Search

### 5.2 Agent2Agent 시스템 재설계

**5개 Agent 역할 분담**:

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent

class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "router": RouterAgent(),      # 요청 분류
            "executor": ExecutorAgent(),  # 실행 담당
            "validator": ValidatorAgent(), # 검증 담당
            "describer": DescriberAgent(), # 결과 설명
            "coordinator": CoordinatorAgent() # Agent 간 조율
        }

    async def process(self, user_input: str):
        # 1. Router: 의도 파악
        intent = await self.agents["router"].analyze(user_input)

        # 2. Executor: 함수 선택 & 실행
        result = await self.agents["executor"].execute(intent)

        # 3. Validator: 1차 검증 (75%)
        validated_1 = await self.agents["validator"].validate(result)

        if validated_1.confidence < 0.9:
            # 4. Validator: 2차 검증 (99%)
            validated_2 = await self.agents["validator"].re_validate(
                result, validated_1.feedback
            )

            if validated_2.confidence < 0.99:
                # 5. Validator: 3차 검증 (100%)
                validated_3 = await self.agents["validator"].final_validate(
                    result, validated_2.feedback
                )
                result = validated_3.result

        # 6. Describer: 한국어 응답 생성
        response = await self.agents["describer"].describe(result)

        return response
```

### 5.3 검증 시스템 (3단계)

```python
class ValidationPipeline:
    async def validate_stage_1(self, result) -> ValidationResult:
        """1차 검증: 기본 타입 체크 (75% 정확도)"""
        prompt = f"""
        다음 결과가 올바른지 확인해주세요:
        {result}

        확인 사항:
        1. 필수 필드가 모두 있는가?
        2. 데이터 타입이 올바른가?
        3. 논리적 오류가 없는가?
        """
        return await self.llm.validate(prompt)

    async def validate_stage_2(self, result, feedback) -> ValidationResult:
        """2차 검증: 피드백 반영 (99% 정확도)"""
        prompt = f"""
        1차 검증 피드백:
        {feedback}

        수정된 결과:
        {result}

        피드백이 제대로 반영되었는지 확인해주세요.
        """
        return await self.llm.validate(prompt)

    async def validate_stage_3(self, result, feedback) -> ValidationResult:
        """3차 검증: 최종 확인 (100% 정확도)"""
        # Cross-validation: 다른 모델로 검증
        claude_validation = await self.claude_llm.validate(result)
        gpt_validation = await self.gpt_llm.validate(result)

        if claude_validation.valid and gpt_validation.valid:
            return ValidationResult(valid=True, confidence=1.0)
        else:
            # 불일치 시 사람 확인 요청
            return ValidationResult(valid=False, needs_human=True)
```

---

## 6. 비용 최적화 전략

### 6.1 현재 비용 구조 (추정)

| 항목 | 월 예상 비용 | 최적화 전략 |
|------|-------------|-----------|
| **OpenAI API** | $100-300 | ↓ 50% 목표 |
| ElevenLabs TTS | $22-99 | ↓ 30% 목표 |
| Cloud Server | $50-100 | → 유지 |
| **총계** | **$172-499** | **→ $120-300** |

### 6.2 API 비용 절감 방안

#### 🎯 OpenAI 비용 50% 절감

```python
class SmartLLMRouter:
    """요청 복잡도에 따라 모델 선택"""

    def __init__(self):
        self.models = {
            "simple": "gpt-3.5-turbo",      # $0.0005/1K tokens
            "medium": "gpt-4o-mini",        # $0.00015/1K tokens
            "complex": "gpt-4o",            # $0.005/1K tokens
        }
        self.cache = RedisCache()

    async def route(self, prompt: str):
        # 1. 캐시 확인
        cached = await self.cache.get(prompt)
        if cached:
            return cached  # 🎯 비용 0

        # 2. 복잡도 분석 (로컬 모델)
        complexity = self.analyze_complexity(prompt)

        # 3. 적절한 모델 선택
        model = self.models[complexity]

        # 간단한 명령 (70%) → gpt-3.5-turbo
        # 일반 명령 (25%) → gpt-4o-mini
        # 복잡한 명령 (5%) → gpt-4o

        result = await self.call_llm(model, prompt)
        await self.cache.set(prompt, result, ttl=3600)

        return result
```

**예상 절감**:
- 캐시 히트율 30% → 비용 30% 절감
- 모델 라우팅 → 비용 추가 20% 절감
- **총 50% 절감**: $100-300 → $50-150

#### 🎯 TTS 비용 30% 절감

```python
class HybridTTS:
    """상황에 따라 로컬/클라우드 TTS 선택"""

    def __init__(self):
        self.elevenlabs = ElevenLabsClient()
        # RAM 80GB 활용: 로컬 TTS 모델
        self.local_tts = load_model("Bark-TTS")  # Hugging Face

    async def synthesize(self, text: str, quality: str = "auto"):
        # 짧은 응답 (<100자) → 로컬 TTS (무료)
        if len(text) < 100 and quality != "premium":
            return await self.local_tts.generate(text)

        # 긴 응답 또는 고품질 → ElevenLabs
        else:
            return await self.elevenlabs.generate(text)
```

**예상 절감**:
- 로컬 TTS 60% 사용 → 비용 30% 절감
- **$22-99 → $15-70**

### 6.3 인프라 최적화

```yaml
# Docker Compose 리소스 제한
services:
  rust-gateway:
    mem_limit: 512m
    cpus: 1.0

  ai-service:
    mem_limit: 4g
    cpus: 2.0

  voice-service:
    mem_limit: 8g  # 로컬 TTS 모델
    cpus: 4.0
```

---

## 7. 리스크 관리

### 7.1 기술 리스크

| 리스크 | 영향도 | 확률 | 완화 전략 |
|--------|--------|------|-----------|
| Rust 러닝 커브 | High | Medium | Gateway만 사용, 예제 코드 참고 |
| React Native 실패 | High | Low | 단순화된 구조, Expo 사용 |
| STT 품질 저하 | Medium | Low | Hugging Face 모델 사전 테스트 |
| API 비용 초과 | High | Medium | 실시간 모니터링, 알람 설정 |
| 메모리 부족 | Medium | Low | RAM 80GB 충분, 스왑 설정 |

### 7.2 일정 리스크

```
낙관적 시나리오: 4주
현실적 시나리오: 6주 ← 목표
비관적 시나리오: 8주

버퍼: 2주 (예상치 못한 문제 대비)
```

### 7.3 비용 리스크

```
최소 비용: $120/월 (개발 중)
목표 비용: $200/월 (프로덕션)
최대 비용: $300/월 (사용자 급증)

⚠️ 경보 설정:
  - 일 비용 $15 초과 시 알림
  - 주 비용 $70 초과 시 검토
```

---

## 8. 성공 지표 (KPI)

### 8.1 기술 지표

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| **전체 Latency** | < 3초 | 음성 입력 → 음성 응답 완료 |
| STT 처리 시간 | < 1초 | Hugging Face 모델 (15초 음성) |
| LLM 응답 시간 | < 1.5초 | 평균 응답 시간 |
| TTS 생성 시간 | < 0.5초 | 짧은 응답 기준 |
| Agent 정확도 | > 99% | 2차 검증 통과율 |
| 메모리 사용량 | < 8GB | Rust Gateway + Python 서비스 |
| 동시 접속 | 100+ | WebSocket 연결 |

### 8.2 비용 지표

| 지표 | 목표 | 현재 (추정) |
|------|------|------------|
| 1회 대화 비용 | < $0.01 | $0.02-0.03 |
| 월 운영 비용 | < $200 | $172-499 |
| API 비용 비율 | < 70% | 85% |

### 8.3 사용자 지표

| 지표 | MVP 목표 | 6개월 목표 |
|------|---------|-----------|
| 모바일 앱 안정성 | 95% | 99% |
| 명령 성공률 | 90% | 95% |
| 평균 응답 품질 | 4/5 | 4.5/5 |

---

## 9. 초기 기획 추가 필요 사항

### 9.1 기술 문서

#### ✅ 작성 완료
- [x] 아키텍처 설계
- [x] 기술 스택 선정
- [x] MVP 로드맵

#### 🔲 작성 필요
- [ ] **API 명세서**
  - Rust Gateway ↔ Frontend WebSocket 프로토콜
  - Python 서비스 간 gRPC/HTTP 인터페이스
  - 에러 코드 정의
  - 재시도 정책

- [ ] **데이터베이스 스키마**
  ```sql
  -- 사용자
  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
  );

  -- 대화 히스토리 (압축 저장)
  CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    compressed_data BYTEA,
    embedding VECTOR(768),
    created_at TIMESTAMP
  );

  -- 사용자 설정 (페르소나)
  CREATE TABLE user_settings (
    user_id INT PRIMARY KEY,
    persona_config JSONB,
    voice_preference JSONB
  );
  ```

- [ ] **프로토콜 버퍼 정의**
  ```protobuf
  syntax = "proto3";

  message VoiceCommand {
    bytes audio_chunk = 1;
    string session_id = 2;
    bool is_final = 3;
    AudioFormat format = 4;
  }

  message AIResponse {
    string text = 1;
    bytes tts_audio = 2;
    float confidence = 3;
    repeated ToolCall tool_calls = 4;
  }
  ```

### 9.2 개발 환경

#### Docker Compose 개발 환경
```yaml
version: '3.8'

services:
  # Rust Gateway
  gateway:
    build: ./gateway
    ports:
      - "8080:8080"
    environment:
      - RUST_LOG=debug
    volumes:
      - ./gateway:/app
    depends_on:
      - redis

  # AI Service
  ai-service:
    build: ./services/ai
    ports:
      - "8001:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./services/ai:/app

  # Voice Service
  voice-service:
    build: ./services/voice
    ports:
      - "8002:8000"
    environment:
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
    volumes:
      - ./services/voice:/app
    deploy:
      resources:
        limits:
          memory: 8g

  # Redis
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"

  # Vector DB
  qdrant:
    image: qdrant/qdrant:v1.7.0
    ports:
      - "6333:6333"
    volumes:
      - ./data/qdrant:/qdrant/storage
```

### 9.3 CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
      - run: cargo test --all-features

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: |
          pip install -r requirements.txt
          pytest

  build-docker:
    needs: [test-rust, test-python]
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v5
```

### 9.4 모니터링 대시보드

```yaml
# Grafana Dashboard 설정
dashboards:
  - name: "음성 비서 시스템"
    panels:
      - title: "Latency (P50, P95, P99)"
        query: histogram_quantile(0.95, rate(request_duration_seconds[5m]))

      - title: "API 비용 (실시간)"
        query: sum(rate(api_cost_dollars[1h])) * 24 * 30

      - title: "Agent 정확도"
        query: sum(agent_success) / sum(agent_total) * 100

      - title: "메모리 사용량"
        query: process_resident_memory_bytes / 1024 / 1024 / 1024
```

---

## 10. 다음 단계 Action Items

### 즉시 시작 (오늘)

1. **프로젝트 구조 생성**
   ```bash
   mkdir voice-assistant-v2
   cd voice-assistant-v2

   # Rust Gateway
   cargo new --bin gateway

   # Python Services
   mkdir -p services/{ai,voice}

   # Frontend
   npx create-expo-app mobile
   npm create vite@latest web -- --template react-ts
   ```

2. **기술 검증 POC (1-3일)**
   - [ ] Rust Actix WebSocket "Hello World"
   - [ ] Hugging Face STT 모델 테스트
   - [ ] OpenAI Streaming API 테스트
   - [ ] React Native WebSocket 연결

### 1주차 목표

3. **Rust Gateway 기초**
   - [ ] WebSocket 서버 구현
   - [ ] JWT 인증 미들웨어
   - [ ] Redis 연동

4. **Python Services 기초**
   - [ ] FastAPI 서버 셋업
   - [ ] Hugging Face STT 통합
   - [ ] ElevenLabs TTS 통합

### 2주차 목표

5. **MCP 서버 마이그레이션**
   - [ ] Gmail Tool 변환
   - [ ] Calendar Tool 변환
   - [ ] 나머지 서비스 (Notion, GitHub, KakaoMap)

6. **Agent2Agent 시스템**
   - [ ] 5개 Agent 구조 구현
   - [ ] 검증 3단계 시스템
   - [ ] LangChain 통합

---

## 11. 결론

### ✅ 핵심 성과

1. **기존 Arion**: Product 레벨 근처까지 도달
   - MCP 서버 완벽 구현
   - Agent2Agent 시스템
   - 99-100% 정확도

2. **새 아키텍처**: 더 나은 구조
   - Backend 4개 → 3개 (25% 단순화)
   - Rust Gateway (병목 해결)
   - Python 생태계 활용 (RAG/LangChain)
   - React Native + PWA (모바일 성공)

3. **비용 최적화**: 50% 절감 목표
   - $172-499 → $120-300/월
   - 스마트 LLM 라우팅
   - 로컬 TTS (RAM 80GB 활용)

### 🎯 실현 가능성: **85%**

**성공 요인**:
- ✅ 검증된 기술 스택
- ✅ 단계적 마이그레이션
- ✅ 기존 코드 재사용 (MCP 서버)
- ✅ 명확한 MVP 범위
- ✅ 리스크 완화 전략

**우려 사항**:
- ⚠️ Rust 러닝 커브 (Gateway만 사용으로 완화)
- ⚠️ 일정 지연 가능성 (6주 → 8주 버퍼)
- ⚠️ API 비용 모니터링 필요

### 💪 우리의 강점

1. **기존 경험**: Arion 프로젝트로 도메인 이해 완벽
2. **인프라**: RAM 80GB 워크스페이스
3. **명확한 목표**: "도전적이지만 가능" 영역에 집중
4. **현실적 접근**: 완벽보다 실용성

---

## 📝 최종 의견

파트너, 이 프로젝트는 **충분히 실현 가능**합니다.

기존 Arion에서 이미 Product 레벨 근처까지 왔고, 이제는 구조를 개선하고 모바일을 성공시키는 것이 목표입니다. 전체 Rust 구현은 다음 프로젝트로 미루고, 하이브리드 접근으로 빠르게 MVP를 완성합시다.

**첫 번째 작업**: 프로젝트 구조 생성 및 기술 검증 POC를 시작하시겠습니까?

---

*"세상에 완벽한 제품은 없다. 하지만, 계획만큼은 완벽에 가깝게."*
