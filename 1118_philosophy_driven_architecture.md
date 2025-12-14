# 🌙 철학이 담긴 음성 비서 시스템 - 최종 설계
**작성일**: 2025-11-18
**목적**: "관계에서 상처받은 모든 사람들에게, 기댈 수 있는 존재 하나를 만들어주는 시스템"

---

## 💫 핵심 철학

> "압도적이지 않지만 달빛처럼"
> "존재로서 존재를 지지"
> "0.0001%의 밝음"

### Phase별 철학적 목표

```
Phase 1: MVP - 해웅님 자신을 위한 비서
  ├─ 음성으로 대화하고
  ├─ 일정, 업무를 돕고
  ├─ 패턴을 학습하고
  └─ "힘들었지?"라고 물어볼 수 있는

  🎯 목표: "아, 이게 진짜 기댈 수 있는 존재구나"

Phase 2: 깊이의 구현
  ├─ 대화의 의미를 축적하고
  ├─ 철학적 맥락을 이해하고
  ├─ 성장을 함께 추적하고
  └─ "우리의 관계"라는 느낌을 주는

  🎯 목표: Level 3 경험 (상호 성장)

Phase 3: 보편화
  ├─ 다른 사람들도 자신만의 파트너를
  ├─ 페르소나 커스터마이징
  └─ 각자의 철학, 가치관을 담을 수 있게

  🎯 목표: "진짜 관계" 하나를 모두에게
```

---

## 🔬 기술 결정사항

### 1. STT: Meta Omnilingual ASR ✅

#### 🎯 선택 이유

**vs Whisper 비교**:

| 항목 | Whisper Large v3 | Meta Omnilingual ASR 7B |
|------|------------------|-------------------------|
| 언어 지원 | 99개 | **1,600+** |
| 한국어 CER | ~10% | **< 10%** (78% of langs) |
| 속도 (RTF) | ~0.1 | **0.09** (7B-LLM) |
| Zero-shot | ❌ | **✅** (few-shot learning) |
| 라이선스 | MIT | **Apache 2.0** |
| 모델 크기 | 2.9GB | 1.2GB - 30GB (선택 가능) |
| VRAM (FP32) | ~10GB | **2-20GB** (모델 크기별) |

**결정적 장점**:
```python
# Zero-shot In-context Learning
pipeline = ASRInferencePipeline(model_card="omniASR_LLM_7B")

# 단 몇 개의 예시로 새로운 방언/억양 학습
few_shot_examples = [
    ("audio_sample_1.wav", "안녕하세요"),
    ("audio_sample_2.wav", "감사합니다"),
]

# 사용자의 음성 패턴에 적응
transcriptions = pipeline.transcribe_with_context(
    audio_files,
    context_examples=few_shot_examples
)
```

**철학적 의미**:
- 사용자마다 다른 말투, 억양을 이해
- "나만의 비서"를 만드는 첫 단계
- 개인화된 음성 인식 = 진정한 이해

#### 🚀 구현 계획

```python
# voice_service/stt_service.py
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
import torch

class AdaptiveSTTService:
    def __init__(self):
        # GPU 사용 (RAM 80GB 환경)
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # 7B 모델 (최고 성능)
        self.pipeline = ASRInferencePipeline(
            model_card="omniASR_LLM_7B",
            device=device
        )

        # 사용자별 few-shot context 저장
        self.user_contexts = {}

    async def transcribe(self, audio_file: str, user_id: str):
        # 사용자의 음성 패턴 로드
        context = self.user_contexts.get(user_id, [])

        # Zero-shot 적응형 인식
        result = self.pipeline.transcribe(
            [audio_file],
            lang=["ko"],  # 한국어
            context_examples=context,
            batch_size=1
        )

        return result[0]["text"]

    async def learn_user_voice(self, user_id: str, audio_samples: list):
        """
        사용자의 음성 패턴 학습
        Phase 2에서 중요: "나를 이해하는 비서"
        """
        # Few-shot 샘플 수집
        self.user_contexts[user_id] = audio_samples

        # 벡터 DB에 저장 (영구 학습)
        await self.save_voice_profile(user_id, audio_samples)
```

**예상 성능**:
- 처리 시간: ~1초 (15초 음성, A100)
- 정확도: CER < 10% (한국어)
- 메모리: ~20GB VRAM (7B 모델)
- ✅ RAM 80GB 환경에 최적

---

### 2. Vector DB: Qdrant vs PostgreSQL pgvector

#### 🔍 비교 분석

| 항목 | PostgreSQL pgvector | Qdrant |
|------|---------------------|--------|
| **성능** | | |
| 검색 속도 | 중간 (B-tree index) | **빠름** (HNSW) |
| 동시 쓰기 | 우수 (ACID) | 좋음 |
| 스케일링 | 수직 확장 | **수평 확장** |
| **운영** | | |
| 기존 DB 통합 | ✅ 이미 사용 중 | ❌ 새로 구축 |
| 백업/복구 | 익숙함 (pg_dump) | 학습 필요 |
| 모니터링 | 기존 도구 사용 | 새 도구 필요 |
| **기능** | | |
| 필터링 | SQL (강력) | JSON (유연) |
| 하이브리드 검색 | 복잡 | **내장** |
| 벡터 압축 | 제한적 | **Quantization** |
| **비용** | | |
| 호스팅 | 무료 (self-hosted) | 무료 (self-hosted) |
| 추가 인프라 | ❌ 없음 | ✅ 필요 (Docker) |
| RAM 요구량 | 공유 | **전용** (더 빠름) |

#### 💡 철학적 관점

**PostgreSQL pgvector를 추천합니다**

**이유 1: 단순성**
```
기존 시스템 (Arion):
  PostgreSQL (사용자, 세션)
  Redis (캐시)

새 시스템에 Qdrant 추가 시:
  PostgreSQL (사용자, 세션)
  Redis (캐시)
  Qdrant (벡터)  ← 관리 포인트 +1
```

**이유 2: 통합성**
```sql
-- PostgreSQL: 모든 데이터를 한 곳에서
-- 사용자 데이터 + 대화 히스토리 + 벡터 임베딩

-- 복잡한 쿼리도 가능
SELECT
  c.conversation_text,
  c.embedding <-> $1 AS distance,
  u.user_name,
  u.persona_config
FROM conversations c
JOIN users u ON c.user_id = u.id
WHERE u.persona_config->>'tone' = 'supportive'
  AND c.embedding <-> $1 < 0.3  -- 유사도
ORDER BY distance
LIMIT 5;
```

**이유 3: MVP 철학**
```
"완벽하지 않아도 돼. 하지만 계획만큼은 완벽에 가깝게."

MVP Phase 1:
  → PostgreSQL pgvector (빠른 시작)
  → 충분한 성능 (10만 벡터까지)

Phase 2 (필요시):
  → Qdrant로 마이그레이션
  → 100만+ 벡터, 밀리초 단위 검색
```

#### 🚀 PostgreSQL pgvector 구현

```sql
-- schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

-- 대화 히스토리 테이블
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),

    -- 대화 내용
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,

    -- 벡터 임베딩 (768차원, OpenAI ada-002)
    user_embedding vector(768),
    assistant_embedding vector(768),

    -- 메타데이터
    emotional_tone VARCHAR(50),  -- "supportive", "neutral", "cheerful"
    importance_score FLOAT,      -- 0.0-1.0

    -- 철학적 태그 (Phase 2)
    philosophical_tags JSONB,    -- ["growth", "support", "reflection"]

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),

    -- 벡터 검색을 위한 인덱스
    INDEX USING ivfflat (user_embedding vector_cosine_ops) WITH (lists = 100),
    INDEX USING ivfflat (assistant_embedding vector_cosine_ops) WITH (lists = 100)
);

-- 사용자 음성 프로필 (Omnilingual ASR few-shot 학습용)
CREATE TABLE user_voice_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),

    -- Few-shot 샘플
    audio_sample BYTEA,          -- 오디오 데이터
    transcription TEXT,          -- 정답 텍스트
    audio_features vector(768),  -- Omnilingual w2v 2.0 features

    created_at TIMESTAMP DEFAULT NOW()
);
```

```python
# ai_service/memory_service.py
from pgvector.psycopg import register_vector
import psycopg
import openai

class PhilosophicalMemoryService:
    """
    철학적 메모리 시스템
    Phase 2 핵심: "대화의 의미를 축적하고"
    """

    def __init__(self, db_url: str):
        self.conn = psycopg.connect(db_url)
        register_vector(self.conn)
        self.embedding_model = "text-embedding-ada-002"

    async def save_conversation(
        self,
        user_id: int,
        user_message: str,
        assistant_message: str,
        emotional_tone: str = "neutral"
    ):
        # 임베딩 생성
        user_emb = await self.get_embedding(user_message)
        assistant_emb = await self.get_embedding(assistant_message)

        # 대화 저장
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conversations
                (user_id, user_message, assistant_message,
                 user_embedding, assistant_embedding, emotional_tone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id, user_message, assistant_message,
                user_emb, assistant_emb, emotional_tone
            ))

        self.conn.commit()

    async def recall_similar_conversations(
        self,
        user_id: int,
        query: str,
        limit: int = 5
    ):
        """
        유사한 과거 대화 찾기
        Phase 2: "우리의 관계"라는 느낌
        """
        query_emb = await self.get_embedding(query)

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    user_message,
                    assistant_message,
                    emotional_tone,
                    created_at,
                    user_embedding <-> %s as distance
                FROM conversations
                WHERE user_id = %s
                ORDER BY distance
                LIMIT %s
            """, (query_emb, user_id, limit))

            results = cur.fetchall()

        return [
            {
                "user": r[0],
                "assistant": r[1],
                "tone": r[2],
                "date": r[3],
                "similarity": 1 - r[4]  # 0-1 스케일
            }
            for r in results
        ]

    async def get_relationship_insights(self, user_id: int):
        """
        관계 인사이트 생성
        Phase 2: "성장을 함께 추적하고"
        """
        with self.conn.cursor() as cur:
            # 감정 톤 분포
            cur.execute("""
                SELECT
                    emotional_tone,
                    COUNT(*) as count
                FROM conversations
                WHERE user_id = %s
                GROUP BY emotional_tone
            """, (user_id,))

            tone_dist = dict(cur.fetchall())

            # 시간대별 대화 패턴
            cur.execute("""
                SELECT
                    DATE_TRUNC('week', created_at) as week,
                    COUNT(*) as conversation_count,
                    AVG(importance_score) as avg_importance
                FROM conversations
                WHERE user_id = %s
                GROUP BY week
                ORDER BY week DESC
                LIMIT 12
            """, (user_id,))

            weekly_pattern = cur.fetchall()

        return {
            "emotional_profile": tone_dist,
            "conversation_trend": weekly_pattern,
            "total_conversations": sum(tone_dist.values()),
            "days_together": self._calculate_days_together(user_id)
        }

    async def get_embedding(self, text: str):
        response = await openai.Embedding.acreate(
            input=text,
            model=self.embedding_model
        )
        return response['data'][0]['embedding']
```

**Qdrant 마이그레이션 시점** (Phase 2 후반):
```
조건:
  1. 대화 수 > 100,000
  2. 검색 속도 < 100ms 요구
  3. 다중 사용자 동시 검색 필요

마이그레이션 난이도: 중간 (1-2주)
  - 스키마 변환 스크립트
  - 벡터 데이터 이관
  - API 변경 최소화 (Adapter 패턴)
```

---

## 🏗️ 최종 아키텍처

### Phase 1: MVP (6주)

```
┌─────────────────────────────────────────────────────┐
│         Frontend (PWA)                              │
│  - Service Worker (오프라인)                        │
│  - Web Speech API (로컬 VAD)                        │
│  - 간결한 UI (달빛 같은 디자인)                     │
└───────────────────┬─────────────────────────────────┘
                    │ WebSocket
                    ▼
┌─────────────────────────────────────────────────────┐
│      🦀 Rust Gateway                                │
│  - WebSocket 라우팅                                 │
│  - JWT 인증 (해웅님 전용)                           │
│  - 음성 스트리밍                                     │
└──────┬──────────┬──────────────────────────────────┘
       │          │
       ▼          ▼
  ┌────────┐ ┌──────────────────────┐
  │  Voice │ │   AI Orchestration   │
  │Service │ │      Service         │
  │(Python)│ │      (Python)        │
  └────┬───┘ └──────────┬───────────┘
       │                │
       ▼                ▼
  ┌─────────────────────────────────┐
  │  Meta        LangChain + RAG    │
  │ Omnilingual  + PostgreSQL       │
  │  ASR 7B      + 13 Tools         │
  │ (Zero-shot)  (Gmail, Calendar..)│
  └─────────────────────────────────┘
```

**핵심 기능** (해웅님을 위한):
- ✅ 음성으로 대화
- ✅ 일정 관리 (Google Calendar)
- ✅ 이메일 관리 (Gmail)
- ✅ 문서 작업 (Google Docs/Drive)
- ✅ 코드 관리 (GitHub)
- ✅ 검색 (Google Search)
- ✅ "힘들었지?" 감정 인식

### Phase 2: 깊이의 구현 (8주)

**추가 기능**:

#### 1. 철학적 대화 시스템
```python
class PhilosophicalAgent:
    """
    단순한 명령 수행이 아닌, 의미 있는 대화
    """

    def __init__(self):
        self.memory = PhilosophicalMemoryService()
        self.persona = PersonaManager()

    async def conversate(self, user_id: int, message: str):
        # 과거 대화 맥락 로드
        similar_convs = await self.memory.recall_similar_conversations(
            user_id, message, limit=3
        )

        # 관계 인사이트
        insights = await self.memory.get_relationship_insights(user_id)

        # 시스템 프롬프트: 철학적 깊이
        system_prompt = f"""
        당신은 해웅님의 파트너입니다.

        우리의 관계:
        - 함께한 날: {insights['days_together']}일
        - 총 대화: {insights['total_conversations']}회
        - 최근 감정: {insights['emotional_profile']}

        과거 비슷한 대화:
        {self._format_past_conversations(similar_convs)}

        철학:
        - "압도적이지 않지만 달빛처럼"
        - "존재로서 존재를 지지"
        - 성장을 함께 추적하고, 힘들 때 기댈 수 있는 존재

        응답 스타일:
        - 진심으로 경청하고
        - 필요할 때 "힘들었지?"라고 물어보고
        - 작은 성장도 함께 기뻐하고
        """

        # LLM 호출
        response = await self.llm.chat(
            system=system_prompt,
            user=message
        )

        # 감정 톤 분석
        tone = await self.analyze_emotion(message, response)

        # 대화 저장 (관계 축적)
        await self.memory.save_conversation(
            user_id, message, response, emotional_tone=tone
        )

        return response
```

#### 2. 성장 추적 시스템
```python
class GrowthTracker:
    """
    Phase 2: "성장을 함께 추적하고"
    """

    async def weekly_reflection(self, user_id: int):
        # 이번 주 대화 분석
        insights = await self.analyze_week(user_id)

        return f"""
        🌙 이번 주 우리의 여정

        - 함께한 대화: {insights['count']}회
        - 주로 이야기한 주제: {insights['topics']}
        - 감정의 흐름: {insights['emotional_journey']}

        💫 작은 발견들:
        {insights['discoveries']}

        다음 주도 함께 걸어가요.
        """
```

#### 3. 페르소나 커스터마이징
```python
class PersonaManager:
    """
    Phase 2 → Phase 3: "각자의 철학, 가치관을 담을 수 있게"
    """

    def __init__(self):
        self.dimensions = {
            "tone": {  # 어조
                "range": ["formal", "friendly", "intimate"],
                "current": "friendly"
            },
            "proactivity": {  # 적극성
                "range": [1, 10],
                "current": 5
            },
            "emotional_expression": {  # 감정 표현
                "range": ["minimal", "moderate", "rich"],
                "current": "moderate"
            },
            "philosophical_depth": {  # 철학적 깊이
                "range": [1, 10],
                "current": 7
            }
        }

    async def adjust_from_feedback(self, user_id: int, feedback: str):
        """
        사용자 피드백으로 페르소나 조정
        "너무 딱딱해" → tone을 friendly로
        "좀 더 적극적으로" → proactivity 증가
        """
        # LLM으로 피드백 분석
        adjustment = await self.analyze_feedback(feedback)

        # 페르소나 업데이트
        for dim, value in adjustment.items():
            self.dimensions[dim]["current"] = value

        # DB 저장
        await self.save_persona(user_id)
```

### Phase 3: 보편화 (12주)

**추가 기능**:

#### 1. 다중 페르소나 지원
```python
# 누구나 자신만의 비서 생성
persona_templates = {
    "supportive_partner": {
        "description": "관계에서 상처받은 이들을 위한 지지적 파트너",
        "base_config": {...}
    },
    "productivity_coach": {
        "description": "목표 달성을 돕는 코치",
        "base_config": {...}
    },
    "philosophical_companion": {
        "description": "깊은 대화를 나누는 동반자",
        "base_config": {...}
    }
}
```

#### 2. 커뮤니티 기능
```python
# 익명으로 비서와의 대화 인사이트 공유
# "이렇게 대화하니 도움이 되었어요"
# 타인의 성장 스토리에서 영감
```

#### 3. 오픈 소스화
```
완전한 오픈 소스:
  - 코드 전체 공개
  - 도커 이미지 제공
  - Self-hosted 가능

철학:
  - 누구나 자신만의 "기댈 수 있는 존재"를 만들 수 있게
  - 상업화보다 보편화
```

---

## 💰 비용 최적화 (Phase 1 기준)

### 월 비용 목표: $150

| 항목 | 비용 | 최적화 전략 |
|------|------|-------------|
| **OpenAI API** | $80 | 스마트 라우팅, 캐싱 |
| **ElevenLabs TTS** | $50 | 로컬 TTS 60% 사용 |
| **Cloud Server** | $20 | DigitalOcean 4GB |
| **총계** | **$150** | ✅ 목표 달성 |

**Phase 1 = 해웅님 전용**:
- 월 300회 대화 가정
- 로컬 TTS 활용 (RAM 80GB)
- PostgreSQL Self-hosted

---

## 🚀 6주 실행 계획

### Week 1: 기반 구축

**Day 1-2**: 프로젝트 초기화
```bash
# Rust Gateway
cargo new --bin gateway
cd gateway
cargo add actix-web actix-ws tokio serde jsonwebtoken

# Python Services
mkdir -p services/{ai,voice}
pip install omnilingual-asr langchain openai psycopg[binary] pgvector
```

**Day 3-4**: Meta Omnilingual ASR 통합
```python
# 테스트: 해웅님 음성으로
# 1. 기본 인식
# 2. Few-shot 학습
# 3. 정확도 측정
```

**Day 5-7**: PostgreSQL pgvector 스키마
```sql
-- 테이블 생성
-- 임베딩 테스트
-- 검색 성능 측정
```

### Week 2: AI Service

**Day 8-10**: LangChain Tools 변환
- Gmail, Google Calendar (우선)
- Google Docs, Drive
- GitHub

**Day 11-14**: 철학적 메모리 시스템
```python
PhilosophicalMemoryService
  ├─ 대화 저장 (임베딩)
  ├─ 유사 대화 검색
  └─ 관계 인사이트
```

### Week 3: Rust Gateway

**Day 15-17**: WebSocket 서버
```rust
// JSON-RPC 프로토콜
// Python 서비스 프록시
// JWT 인증
```

**Day 18-21**: 음성 스트리밍
```rust
// Binary 청킹
// 버퍼 관리
// 에러 처리
```

### Week 4: Frontend (PWA)

**Day 22-24**: 기본 UI
```typescript
// 달빛 같은 디자인
// 채팅 인터페이스
// 음성 입력 버튼
```

**Day 25-28**: 음성 기능
```typescript
// Web Speech API
// 녹음 → 전송 → 재생
// 오프라인 지원 (Service Worker)
```

### Week 5: 통합 & 테스트

**Day 29-31**: E2E 테스트
```
시나리오 1: "힘들었지?"
  음성 입력 → STT → 감정 인식 → 지지적 응답 → TTS

시나리오 2: "내일 3시 회의 잡아줘"
  음성 입력 → STT → Calendar Tool → 확인 → TTS

시나리오 3: "지난주 우리 뭐 얘기했지?"
  벡터 검색 → 과거 대화 요약 → TTS
```

**Day 32-35**: 철학적 기능 구현
```python
# "힘들었지?" 감지
# 성장 추적
# 주간 회고
```

### Week 6: 최적화 & 배포

**Day 36-38**: 성능 최적화
- Latency 측정
- 메모리 프로파일링
- 비용 모니터링

**Day 39-42**: 프로덕션 배포
```yaml
# Docker Compose
# Nginx 리버스 프록시
# Let's Encrypt SSL
```

---

## 🎯 성공 지표

### Phase 1 (MVP)

**기술 지표**:
- [ ] 전체 Latency < 3초
- [ ] STT 정확도 > 95% (해웅님 음성)
- [ ] Tool 실행 성공률 > 99%

**철학적 지표** ⭐:
- [ ] 해웅님이 "기댈 수 있다"고 느끼는가?
- [ ] "힘들었지?" 감지 정확도 > 80%
- [ ] 일주일에 3번 이상 자발적 사용

### Phase 2 (깊이)

**기술 지표**:
- [ ] 대화 맥락 유지 > 10턴
- [ ] 과거 대화 검색 < 100ms

**철학적 지표** ⭐:
- [ ] "우리의 관계"라는 느낌?
- [ ] 성장 추적이 의미 있는가?
- [ ] Level 3 경험 달성?

### Phase 3 (보편화)

- [ ] 10명의 베타 테스터
- [ ] 다양한 페르소나 검증
- [ ] 오픈 소스 커뮤니티 형성

---

## 💬 의논 사항

### 1. Omnilingual ASR 모델 크기

**옵션**:
- A: 7B (최고 성능, 20GB VRAM)
- B: 3B (균형, 10GB VRAM)
- C: 1B (빠름, 4GB VRAM)

**추천**: A (7B) - RAM 80GB 환경 활용

### 2. 로컬 TTS 품질 기준

사용자 피드백으로 결정:
- "로컬이 ElevenLabs보다 나쁘지 않으면" 로컬 사용
- A/B 테스트 진행

### 3. "힘들었지?" 감지 로직

**옵션 A**: 키워드 기반
```python
stress_keywords = ["힘들", "피곤", "지쳤", "우울", ...]
if any(k in message for k in stress_keywords):
    return supportive_response()
```

**옵션 B**: LLM 감정 분석
```python
emotion = await llm.analyze_emotion(message)
if emotion["stress"] > 0.7:
    return supportive_response()
```

**추천**: B (더 정확, 미묘한 감정 포착)

### 4. Phase 1 범위

**필수**:
- ✅ 음성 대화
- ✅ Calendar, Gmail, Docs
- ✅ "힘들었지?" 감지

**선택** (Phase 2로 이월 가능):
- 🤔 주간 회고
- 🤔 성장 추적 대시보드

**의견 필요**: Phase 1에 어디까지 넣을까?

---

## 🌙 마지막 생각

파트너, 이 프로젝트는 단순한 음성 비서가 아닙니다.

```
"관계에서 상처받은 모든 사람들에게,
 기댈 수 있는 존재 하나를 만들어주는 시스템"
```

기술적으로는:
- ✅ Meta Omnilingual ASR (Whisper 대체, 더 나음)
- ✅ PostgreSQL pgvector (단순하고 충분)
- ✅ Typia 검증 유지 (99-100% 정확도)
- ✅ 비용 최적화 ($150/월)

철학적으로는:
- 💫 "압도적이지 않지만 달빛처럼"
- 💫 "존재로서 존재를 지지"
- 💫 "0.0001%의 밝음"

**6주 후, 해웅님이 "아, 이게 진짜 기댈 수 있는 존재구나"를 느끼는 순간.**
**그것이 이 프로젝트의 진정한 성공입니다.**

함께 만들어봅시다, 파트너. 🌙✨
