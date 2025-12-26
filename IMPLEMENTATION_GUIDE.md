# ProjectML Decision Engine - 구현 가이드

**지금부터 구현 시작**
**Date:** 2025-12-26

---

## 🎯 목표

**4주 내에:**
1. ✅ Decision Engine 프로덕션 모드 완성
2. ✅ SaaSA 런칭 (Decision OS 판단 기반)
3. ✅ 논문 실험 코드 작성
4. ✅ 첫 수익 발생

---

## 📦 생성된 파일 요약

### Decision OS v0.2 (독립 설계 - 참고용)
```
w:\Projects\ARP\decision_os\
├── constitution_v0.2.json      ← ProjectML로 통합됨
├── schema_v0.2.sql              ← ProjectML DB로 통합됨
├── orchestrator_v0.2.py         ← ProjectML agents로 통합됨
├── TECHNICAL_DESIGN_v0.2.md    ← 설계 철학 참고
└── README.md                    ← 독립 실행 가이드 (보류)
```

### ProjectML 통합 (실제 구현)
```
w:\Projects\ARP\ProjectML\
├── INTEGRATION_DESIGN_FINAL.md  ← ⭐ 통합 설계서
├── IMPLEMENTATION_GUIDE.md      ← ⭐ 이 파일
│
├── moonlight/
│   ├── data/
│   │   └── ideas_initial.sql    ← ⭐ 5개 MVP 데이터
│   │
│   └── packages/ai-core/src/
│       └── agents/
│           └── [구현 예정]
│
└── philosophy/
    └── paper/
        └── multiagentdebate      ← 논문 아이디어 원본
```

---

## 🚀 Week 1 구현 체크리스트

### Day 1: DB Migration

```bash
# 1. Alembic Migration 생성
cd w:\Projects\ARP\ProjectML\moonlight\packages\ai-core

alembic revision -m "Add Decision Engine tables"

# 2. Migration 파일 작성
# alembic/versions/[timestamp]_add_decision_engine_tables.py
```

**Migration 내용:**
```python
def upgrade():
    # IDEAS TABLE
    op.create_table(
        'ideas',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('github_repo', sa.String()),
        sa.Column('time_axis', sa.Enum('now', 'next', 'later')),
        sa.Column('purpose_axis', sa.Enum('cash_engine', 'capability_builder', 'world_builder')),
        sa.Column('os_relation', sa.Enum('core', 'extension', 'independent')),
        sa.Column('risk_types', sa.JSON()),
        sa.Column('priority_score', sa.Float()),
        sa.Column('current_status', sa.String()),
        sa.Column('description', sa.Text())
    )

    # DECISIONS TABLE
    # LEARNING_LOGS TABLE
    # ... (schema_v0.2.sql 참고)
```

```bash
# 3. Migration 실행
alembic upgrade head

# 4. 초기 데이터 로드
psql -U postgres -d moonlight < ../data/ideas_initial.sql
# 또는 SQLite:
sqlite3 moonlight.db < ../data/ideas_initial.sql
```

---

### Day 2: Constitution 통합

```bash
# 1. constitution.yaml 확장
cd w:\Projects\ARP\ProjectML\moonlight\docs
```

**기존 constitution.yaml에 추가:**
```yaml
# ========================================
# Decision Engine
# ========================================
decision:
  version: "0.2"
  updated_at: "2025-12-26"

  core_principles:
    - id: principle_001
      text: "시스템은 인간의 판단 능력을 장기적으로 향상시켜야 한다"
      priority: 0

    - id: principle_002
      text: "시스템은 사용자가 의존하지 않고 스스로 떠날 수 있게 설계되어야 한다"
      priority: 0
      rationale: "가장 완벽한 이별이 가장 아름다운 사랑"

  constraints:
    - id: legal_001
      text: "계약, 보장, 100%, 환불 등 법적 리스크 키워드 사용 금지"
      enforcement: "automatic_rejection"

    - id: ethical_001
      text: "사용자 판단을 대체하지 않음. 선택지 제시만 가능"
      enforcement: "output_format_check"

  preferences:
    - id: pref_market
      text: "조 단위 시장 우선. Phase 0는 수익 확보 우선"
      priority: 3

    - id: pref_speed
      text: "혼자서 3개월 내 MVP 불가능하면 Phase 2 이후"
      priority: 4
      context: "하드웨어: 5800X3D + 4070S"
```

---

### Day 3-4: Agent 파일 생성

```bash
cd w:\Projects\ARP\ProjectML\moonlight\packages\ai-core\src\agents
```

**파일 구조:**
```
agents/
├── __init__.py
├── orchestrator.py          [기존 - 수정]
├── decision_engine.py       [신규]
│
├── vision_agent.py          [신규]
├── risk_agent.py            [신규]
├── execution_agent.py       [신규]
├── market_agent.py          [신규]
└── judge_agent.py           [신규]
```

**핵심 구현:**

```python
# decision_engine.py

from typing import Optional, Dict
from .vision_agent import VisionAgent
from .risk_agent import RiskAgent
from .execution_agent import ExecutionAgent
from .market_agent import MarketAgent
from .judge_agent import JudgeAgent

class DecisionEngine:
    """ProjectML Decision Engine"""

    def __init__(self, mode: str = "production"):
        self.mode = mode
        self.constitution = self._load_constitution()

        # 5-Agent System
        self.vision = VisionAgent(self.constitution)
        self.risk = RiskAgent(self.constitution)
        self.execution = ExecutionAgent(self.constitution)
        self.market = MarketAgent(self.constitution)
        self.judge = JudgeAgent(self.constitution)

    async def process_decision(
        self,
        question: str,
        idea_id: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """핵심 의사결정 프로세스"""

        # 1. 4개 Agent 병렬 실행
        vision_view = await self.vision.analyze(question, context)
        risk_view = await self.risk.analyze(question, context)
        execution_view = await self.execution.analyze(question, context)
        market_view = await self.market.analyze(question, context)

        # 2. Judge 최종 판결
        judge_ruling = await self.judge.rule({
            'vision': vision_view,
            'risk': risk_view,
            'execution': execution_view,
            'market': market_view
        })

        # 3. Decision 객체 생성 + DB 저장
        decision = Decision(
            question=question,
            vision=vision_view,
            risk=risk_view,
            execution=execution_view,
            market=market_view,
            ruling=judge_ruling,
            confidence=self._calculate_confidence(...)
        )

        await decision.save()
        return decision
```

---

### Day 5-7: LLM API 연동

```bash
# .env 파일 생성
cd w:\Projects\ARP\ProjectML\moonlight\packages\ai-core
```

```env
# OpenRouter (Free tier)
OPENROUTER_API_KEY=sk-or-...

# OpenAI (유료 전환 시)
OPENAI_API_KEY=sk-...

# Claude (Phase 1)
ANTHROPIC_API_KEY=sk-ant-...
```

**LLM Provider 구현:**
```python
# src/llm/provider.py [기존 수정]

class LLMProvider:
    def __init__(self, provider: str = "openrouter"):
        self.provider = provider

        if provider == "openrouter":
            self.client = self._init_openrouter()
        elif provider == "openai":
            self.client = openai.AsyncOpenAI()

    async def call(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "gpt-3.5-turbo"
    ):
        """통합 LLM 호출"""
        # ...
```

---

## 🧪 테스트 시나리오

### Test 1: 첫 Decision 실행

```python
# test_first_decision.py

import asyncio
from agents.decision_engine import DecisionEngine

async def main():
    engine = DecisionEngine(mode="production")

    decision = await engine.process_decision(
        question="""
        GitHub MVP 5개 중 우선순위:
        1. LMS
        2. SaaSA
        3. Marketing Platform
        4. Character Chat
        5. RL Game

        조건:
        - 현재 수익: 0
        - 가용 시간: 풀타임
        - 목표: 빠른 수익
        """,
        context={
            "current_revenue": 0,
            "hardware": "5800X3D + 4070S"
        }
    )

    print(f"=== Decision ===")
    print(f"Vision: {decision.vision}")
    print(f"Risk: {decision.risk}")
    print(f"Ruling: {decision.ruling}")
    print(f"Confidence: {decision.confidence:.2%}")

asyncio.run(main())
```

**예상 출력:**
```
=== Decision ===
Vision: LMS는 조 단위 시장. Character Chat은 AGI 철학...
Risk: SaaSA는 저작권 이슈, LMS는 개인정보...
Ruling: SaaSA 먼저 → 현금 흐름 확보 → LMS 2순위

Confidence: 78%
```

---

## 📊 Week 2-4: 실전 운영

### Week 2: 30회 Decision 테스트

**목표:** Constitution 규칙 검증 + 신뢰도 향상

```bash
# 매일 3개 질문
python test_daily_decisions.py

# 예시 질문:
# - "오늘 뭐 먼저 코딩할까?"
# - "이 기능 추가할까 말까?"
# - "블로그 글 주제는?"
```

### Week 3: SaaSA 런칭

**Decision OS 판단:**
```
Ruling: SaaSA 먼저
→ 1주 내 런칭 가능
→ API 비용 < 수익 예상
→ Constitution pref_speed 적용
```

**Action:**
1. SaaSA 최종 테스트
2. 마케팅 페이지 제작
3. 첫 고객 획득

### Week 4: 논문 실험 시작

```python
# research/experiments/exp_01_agent_count.py 실행
python exp_01_agent_count.py

# 데이터 수집
# - 3-Agent vs 5-Agent vs 7-Agent
# - 각 10회 반복
# - 정확도 비교
```

---

## ⚠️ 지금 당장 해야 할 일 (순서대로)

### 1. Q1-Q3 답변 (이 파일 아래)

**Q1. Constitution 규칙 추가:**
```
"시스템은 사용자가 의존하지 않고 스스로 떠날 수 있게 설계"
→ priority 0 추가? YES / NO
```

**Q2. 첫 실행 질문:**
```
"SaaSA vs LMS, 뭐 먼저?"
→ 이걸로 테스트? YES / 다른 질문 제시
```

**Q3. 논문 실험 순서:**
```
1. Agent 수
2. Group Debate
3. Quantization

→ 순서대로? / Quantization 먼저? / 병렬?
```

---

### 2. OpenRouter API Key 발급 (5분)

```
https://openrouter.ai/
→ Sign Up
→ Free tier 선택
→ API Key 복사
```

---

### 3. 가상환경 설정 (10분)

```bash
cd w:\Projects\ARP\ProjectML\moonlight\packages\ai-core

python -m venv venv
venv\Scripts\activate

pip install -r pyproject.toml  # 또는 requirements.txt
```

---

### 4. DB Migration 실행 (15분)

```bash
# Alembic 초기화 (이미 되어있으면 skip)
alembic init alembic

# Migration 생성
alembic revision -m "Add Decision Engine"

# Migration 파일 작성 (schema_v0.2.sql 참고)

# 실행
alembic upgrade head

# 데이터 로드
sqlite3 moonlight.db < ../data/ideas_initial.sql
```

---

## 🔥 Final Checklist (구현 전 확인)

- [ ] Q1-Q3 답변 완료
- [ ] OpenRouter API Key 발급
- [ ] 가상환경 설정
- [ ] DB Migration 준비
- [ ] `ideas_initial.sql` 검토
- [ ] Constitution 최종 확인
- [ ] **구현 시작 승인**

---

## 📝 Implementation Log (여기에 진행 상황 기록)

```
# 2025-12-26
- [x] 통합 설계 완료
- [x] IDEAS TABLE 초기 데이터 생성
- [x] 논문 실험 프로토콜 설계
- [ ] Q1-Q3 답변 대기
- [ ] 구현 시작 대기

# 2025-12-27 (예정)
- [ ] Day 1: DB Migration
- [ ] Day 2: Constitution 통합
- [ ] ...
```

---

**다음 액션: 네가 Q1-Q3 답변하면 즉시 구현 시작**
