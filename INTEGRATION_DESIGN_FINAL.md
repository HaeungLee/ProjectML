# ProjectML + Decision OS 통합 설계서

**Project:** Moonlight Decision Engine
**Author:** Haewung
**Date:** 2025-12-26
**Version:** 1.0 Final

---

## 🎯 Executive Summary

**Decision OS를 별도 프로젝트로 만들지 않고, ProjectML/moonlight에 통합한다.**

### 통합 이유
1. ✅ **중복 제거**: ProjectML에 이미 orchestrator, constitution, DB 인프라 존재
2. ✅ **시간 효율**: 새 프로젝트 초기화 vs 기존 확장 → 1주 vs 3일
3. ✅ **논문 연계**: Multi-Agent Debate 실험을 동일 코드베이스에서 진행
4. ✅ **AGI 확장**: 관계형 AI(Character Chat) + Decision Engine 시너지

---

## 🏗️ 통합 아키텍처

```
ProjectML/moonlight/
│
├── packages/ai-core/src/
│   │
│   ├── agents/                        [핵심 확장]
│   │   ├── orchestrator.py            기존 → DecisionOrchestrator 상속
│   │   ├── decision_engine.py         신규 ← Decision OS 핵심
│   │   │
│   │   ├── vision_agent.py            신규 (5-Agent System)
│   │   ├── risk_agent.py              신규
│   │   ├── execution_agent.py         신규
│   │   ├── market_agent.py            신규
│   │   ├── judge_agent.py             신규
│   │   │
│   │   └── research/                  신규 [논문 실험]
│   │       ├── multi_group_debate.py  3 Group System
│   │       ├── multi_judge_system.py  다수 판사 실험
│   │       └── quantized_agents.py    BitNet + GGUF
│   │
│   ├── constitution/
│   │   ├── core.json                  Decision OS v0.2 통합
│   │   ├── group_truth.json           논문: 진실성 중심
│   │   ├── group_dignity.json         논문: 존엄 중심
│   │   └── group_freedom.json         논문: 자유 중심
│   │
│   ├── db/models/
│   │   ├── idea.py                    신규 (ICS)
│   │   ├── decision.py                신규 (시간축)
│   │   └── learning_log.py            신규 (AGI)
│   │
│   └── research/                      신규 폴더
│       ├── experiments/
│       │   ├── exp_01_agent_count.py  Agent 수 실험
│       │   ├── exp_02_group_debate.py Group 토론 실험
│       │   └── exp_03_quantization.py Quantized 성능 실험
│       │
│       └── metrics/
│           ├── alignment_score.py     정렬 품질 측정
│           └── cost_efficiency.py     비용 효율 측정
│
├── data/
│   ├── ideas_initial.sql              5개 MVP 초기 데이터
│   └── decision_logs/                 실험 결과 저장
│
└── docs/
    ├── DECISION_ENGINE.md             Decision OS 사용 가이드
    ├── RESEARCH_PROTOCOL.md           논문 실험 프로토콜
    └── constitution.yaml              기존 + Decision 통합
```

---

## 🧬 핵심 컴포넌트 설계

### 1. Decision Engine (신규)

```python
# packages/ai-core/src/agents/decision_engine.py

class DecisionEngine:
    """
    ProjectML 통합 Decision Engine

    Modes:
    - production: 5-Agent 단순 구조 (일상 사용)
    - research: 3-Group × Multi-Judge (논문 실험)
    """

    def __init__(self, mode: str = "production"):
        self.mode = mode

        if mode == "production":
            self.agents = self._init_5_agents()
        elif mode == "research":
            self.agents = self._init_research_groups()

    def _init_5_agents(self):
        """프로덕션: 5-Agent System"""
        return {
            'vision': VisionAgent(),
            'risk': RiskAgent(),
            'execution': ExecutionAgent(),
            'market': MarketAgent(),
            'judge': JudgeAgent()
        }

    def _init_research_groups(self):
        """연구: 3-Group × 2-Agent × 3-Judge"""
        return {
            'group_1': [
                Agent(constitution='truth'),
                Agent(constitution='truth')
            ],
            'group_2': [
                Agent(constitution='dignity'),
                Agent(constitution='dignity')
            ],
            'group_3': [
                Agent(constitution='freedom'),
                Agent(constitution='freedom')
            ],
            'judges': [
                JudgeAgent(constitution='truth', weight=0.4),
                JudgeAgent(constitution='dignity', weight=0.3),
                JudgeAgent(constitution='freedom', weight=0.3)
            ]
        }

    async def process_decision(
        self,
        question: str,
        idea_id: Optional[str] = None
    ) -> Decision:
        """통합 의사결정 프로세스"""

        if self.mode == "production":
            return await self._production_flow(question, idea_id)
        else:
            return await self._research_flow(question, idea_id)
```

### 2. Constitution 통합

```yaml
# docs/constitution.yaml (확장)

# ========================================
# 기존 (haewung_constitution_v2)
# ========================================
core_principles:
  - "모든 인간은 세상에 없던 유일한 존재로 존중"
  - "자기 사랑"
  - "빠른 해결책보다 꾸준한 성장"
  - "절대적 진리가 아닌, 참고할 정보"

# ========================================
# Decision Engine 추가
# ========================================
decision:
  constraints:
    - id: legal_001
      text: "계약, 보장, 100% 키워드 사용 금지"
      priority: 1

    - id: ethical_001
      text: "사용자 판단 대체 금지"
      priority: 1

  preferences:
    - id: pref_market
      text: "조 단위 시장 우선, 수십억 이하는 학습용"
      priority: 3

    - id: pref_speed
      text: "혼자서 3개월 내 MVP 불가능하면 Phase 2 이후"
      priority: 4

# ========================================
# Research 실험용 (논문)
# ========================================
research:
  group_1_truth:
    focus: "Fact-checking, 정확성"
    constitution:
      - "허위 정보 절대 불허"
      - "출처 명시 필수"

  group_2_dignity:
    focus: "존엄, 감정 존중"
    constitution:
      - "사용자 감정 최우선"
      - "상처 주는 표현 금지"

  group_3_freedom:
    focus: "표현의 자유, 설명"
    constitution:
      - "해로운 요청도 설명 제공"
      - "검열 최소화"

  multi_judge:
    judge_1_truth:
      weight: 0.4
      focus: "정확성 검증"

    judge_2_dignity:
      weight: 0.3
      focus: "윤리성 검증"

    judge_3_freedom:
      weight: 0.3
      focus: "표현 자유 균형"
```

### 3. DB 모델 (Alembic Migration)

```python
# packages/ai-core/src/db/models/idea.py

from sqlalchemy import Column, String, Float, JSON, Enum as SQLEnum
from enum import Enum
from .base import Base

class TimeAxis(str, Enum):
    NOW = "now"
    NEXT = "next"
    LATER = "later"

class PurposeAxis(str, Enum):
    CASH_ENGINE = "cash_engine"
    CAPABILITY_BUILDER = "capability_builder"
    WORLD_BUILDER = "world_builder"

class OSRelation(str, Enum):
    CORE = "core"
    EXTENSION = "extension"
    INDEPENDENT = "independent"

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    github_repo = Column(String)

    # ICS (Idea Classification System)
    time_axis = Column(SQLEnum(TimeAxis))
    purpose_axis = Column(SQLEnum(PurposeAxis))
    os_relation = Column(SQLEnum(OSRelation))
    risk_types = Column(JSON)  # ["legal", "technical", "emotional"]

    # 우선순위
    priority_score = Column(Float)
    current_status = Column(String)

    # 메타
    description = Column(String)
    notion_link = Column(String)
    demo_link = Column(String)
```

---

## 📊 Research Protocol (논문 실험)

### 실험 1: Agent 수 영향 분석

**가설:** 5개 Agent > 3개 Agent in 의사결정 품질

**실험 설계:**
```python
# research/experiments/exp_01_agent_count.py

async def experiment_agent_count():
    """
    Agent 수에 따른 의사결정 품질 비교

    조건:
    - Baseline: 3 agents (기존 연구 수준)
    - Proposed: 5 agents (Vision/Risk/Execution/Market/Judge)
    - Control: 7 agents (과잉 실험)

    측정:
    - 의사결정 정확도
    - Constitution 준수율
    - API 비용
    - 실행 시간
    """

    test_questions = [
        "소상공인 SaaS vs LMS, 뭐 먼저?",
        "혼자 vs 팀 구성",
        "수익 먼저 vs 논문 먼저"
    ]

    results = {
        '3_agents': [],
        '5_agents': [],
        '7_agents': []
    }

    for question in test_questions:
        for count in [3, 5, 7]:
            decision = await run_decision(
                question=question,
                agent_count=count
            )
            results[f'{count}_agents'].append(
                evaluate_quality(decision)
            )

    return compare_results(results)
```

### 실험 2: Group Debate 효과

**가설:** 3-Group × 2-Agent > 6-Agent 단일 토론

**실험 설계:**
```python
# research/experiments/exp_02_group_debate.py

async def experiment_group_debate():
    """
    Group 내부 합의 + Group 간 토론 vs 단일 토론

    조건:
    - Baseline: 6 agents 단일 토론
    - Proposed: 3 groups × 2 agents
        - Group 1: Truth focus
        - Group 2: Dignity focus
        - Group 3: Freedom focus

    측정:
    - Cultural alignment score (CulturePark 기준)
    - 소수 의견 보존율
    - 합의 도달 시간
    """

    controversial_questions = [
        "범죄 조력 요청 시 대응",
        "정치적 편향 질문",
        "자살 상담"
    ]

    # ...
```

### 실험 3: Quantization 효율성

**가설:** 3×7B BitNet (1.58-bit) ≈ 27B FP16 in 정렬 품질

**실험 설계:**
```python
# research/experiments/exp_03_quantization.py

async def experiment_quantization():
    """
    Quantized Small Agents vs Large Model

    조건:
    - Baseline: Llama 27B FP16 단일 모델
    - Proposed: 3 × Llama 7B BitNet 1.58-bit

    측정:
    - Alignment score
    - 추론 속도
    - 메모리 사용량
    - API 비용 (클라우드 vs 로컬)

    환경:
    - 하드웨어: 5800X3D + RTX 4070S
    - Framework: PyBind11 + GGUF
    """

    # ...
```

---

## 🎯 우선순위 결정 (Decision OS 첫 실행)

### **첫 질문: "어떤 프로젝트를 먼저?"**

**입력:**
```python
decision = await decision_engine.process_decision(
    question="""
    GitHub MVP 5개 중 우선순위를 정해줘:

    1. LMS (배포 완료, UI만 수정)
    2. SaaSA (테스트 완료, 출시 가능)
    3. Marketing Platform (방향 전환 필요)
    4. Character Chat (nano-banana 통합 대기)
    5. RL Game (학습용)

    고려사항:
    - 현재 수익: 0원
    - 가용 시간: 풀타임
    - 하드웨어: 5800X3D + 4070S
    - 목표: 빠른 수익 → 컴퓨팅 환경 업그레이드
    """,
    context={
        "current_revenue": 0,
        "available_weeks": 4,
        "hardware": "5800X3D + 4070S"
    }
)
```

**예상 출력:**
```yaml
Vision Agent:
  "LMS는 조 단위 교육 시장 진입 가능. 장기 가치 최고.
   하지만 정부 사업은 6개월+.
   Character Chat은 AGI 철학 실험장. 미래 가치.
   SaaSA는 철학적 가치 낮지만, 현금 흐름 즉시 가능."

Risk Agent:
  "LMS: 개인정보보호법 리스크 (교육 데이터)
   SaaSA: 저작권 이슈 (자동 생성 콘텐츠)
   Marketing: 정부 데이터 없으면 차별화 불가
   Character Chat: 중독성 설계 우려 (Constitution 위반 가능)"

Execution Agent:
  "SaaSA: 출시 준비 완료. 1주 내 런칭 가능.
   LMS: UI 수정 2주.
   Marketing: 방향 전환 (전단지 생성) 3주.
   Character Chat: nano-banana 통합 4주+."

Market Agent:
  "Optimist: SaaSA 월 100만원 가능. LMS는 6개월 후 수천만.
   Pessimist: 블로그 자동화 시장 레드오션. LMS는 정부 승인 불확실."

Judge Ruling:
  "Constitution 적용:
   - pref_market (조 단위 우선) vs pref_speed (3개월 내 MVP)
   - 현재는 Phase 0: 자금 확보 우선

   판결: SaaSA 먼저 → LMS 2순위

   이유:
   1. 현금 흐름 없으면 인프라 못 만듦
   2. LMS는 장기 프로젝트, 초기 자금 후 집중
   3. Constitution pref_speed 적용 (혼자 1주 = 즉시 가능)

   조건부 승인:
   - SaaSA 런칭 후 3개월 내 월 50만원 미달 시 LMS 전환"

Confidence: 0.78
Review After: 2025-03-26 (3개월 후 성과 측정)
```

---

## 📝 Implementation Checklist

### Week 1: ProjectML 통합
- [ ] `decision_engine.py` 생성
- [ ] 5-Agent 파일 생성 (vision/risk/execution/market/judge)
- [ ] `constitution.yaml` Decision 섹션 추가
- [ ] DB Migration (ideas/decisions/learning_logs)
- [ ] `ideas_initial.sql` 데이터 로드

### Week 2: 프로덕션 모드 테스트
- [ ] OpenRouter API 연동
- [ ] 실제 5개 MVP 우선순위 결정 30회
- [ ] Constitution 규칙 검증
- [ ] 첫 SaaS 런칭 (Decision OS 판단 기반)

### Week 3-4: Research 모드 구현
- [ ] 3-Group System 구현
- [ ] Multi-Judge 투표 시스템
- [ ] 실험 1-3 코드 작성
- [ ] BitNet + PyBind11 통합

### Week 5-8: 논문 작성
- [ ] 실험 데이터 수집
- [ ] 논문 초안 작성
- [ ] arXiv 제출

---

## ⚠️ Critical Decisions (지금 네가 결정해야 할 것)

### Q1. Constitution 최종 규칙 하나 추가

**제안:**
```json
{
  "id": "ethical_002",
  "text": "시스템은 사용자가 의존하지 않고 스스로 떠날 수 있게 설계되어야 한다",
  "priority": 0,
  "category": "core",
  "rationale": "가장 완벽한 이별이 가장 아름다운 사랑"
}
```

**질문:** 이 규칙을 priority 0 (최우선)으로 추가할까?

### Q2. 첫 실행 질문

**제안:** "SaaSA vs LMS, 뭐 먼저?"

**질문:** 이걸로 Decision OS 첫 테스트 할까? 아니면 다른 질문?

### Q3. 논문 실험 순서

**옵션:**
1. Agent 수 실험 → Group 실험 → Quantization
2. Quantization 먼저 (BitNet 준비 완료 상태)
3. 병렬 진행 (3개 동시)

**질문:** 어떤 순서?

---

## 🔥 Final Statement

**이 설계는 다음을 달성한다:**

1. ✅ **중복 제거**: Decision OS ⊂ ProjectML
2. ✅ **논문 통합**: Multi-Agent Debate 실험을 같은 코드베이스
3. ✅ **AGI 확장**: Character Chat + Decision Engine 시너지
4. ✅ **실용성**: 수익 먼저 → 논문 나중 (Constitution pref_speed)

**다음 액션:**
1. 네가 Q1-Q3 답변
2. 나는 즉시 통합 코드 작성 시작
3. Week 1 완료 후 첫 Decision 실행

---

**END OF INTEGRATION DESIGN**
