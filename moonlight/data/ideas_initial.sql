-- IDEAS Initial Data (상위 5개 MVP)
-- Generated: 2025-12-26

INSERT INTO ideas (
    id,
    title,
    github_repo,
    time_axis,
    purpose_axis,
    os_relation,
    risk_types,
    current_status,
    priority_score,
    description
) VALUES

-- ============================================
-- 1. LMS_MVP
-- ============================================
(
    'mvp_lms_001',
    'LMS 플랫폼 (AI Tutor 기반)',
    'https://github.com/haewung/LMS_MVP',  -- 실제 링크로 수정 필요
    'now',                              -- 배포 완료, UI만 수정
    'world_builder',                    -- 교육 시장 재편
    'extension',                        -- Decision OS 위에서 동작
    '["legal", "ethical"]'::json,       -- 교육 데이터 처리 리스크
    'mvp',                              -- 이미 배포됨
    0.85,                               -- 높은 우선순위
    '사용자 맞춤형 커리큘럼 생성, 진척도 추적, 약점 보강 퀴즈 자동 생성.
     정부 국비지원교육 시장 진입 가능.
     현재 상태: UI 세부 조정 필요, 핵심 기능 완성'
),

-- ============================================
-- 2. SaaSA (블로그 자동화 플랫폼)
-- ============================================
(
    'mvp_saasa_001',
    'SaaSA - 블로그 자동화 플랫폼',
    'https://github.com/haewung/SaaSA',
    'now',                              -- 테스트 완료, 출시 가능
    'cash_engine',                      -- 즉시 수익화 가능
    'independent',                      -- 독립 실행
    '["technical", "market"]'::json,
    'mvp',                              -- 테스트 완료
    0.90,                               -- 최고 우선순위 (빠른 수익)
    '블로그 콘텐츠 자동 생성 및 발행.
     SEO 최적화 자동화.
     현재 상태: 출시 준비 완료, 마케팅만 남음'
),

-- ============================================
-- 3. Marketing-Platform (소상공인 공모전 수상작)
-- ============================================
(
    'mvp_marketing_001',
    'Marketing Platform - 소상공인 마케팅 지원',
    'https://github.com/haewung/Marketing-Platform',
    'now',                              -- nano-banana 통합 후 강화
    'cash_engine',                      -- 정부 사업 가능성
    'extension',                        -- Decision OS + Video 생성
    '["legal", "market"]'::json,        -- 정부 데이터 접근 이슈
    'mvp',                              -- 공모전 수상
    0.75,                               -- 중상 우선순위
    '상권 분석 제외, 전단지/광고 영상 자동 생성에 집중.
     nano-banana + Veo3 통합 시 시장 장악 가능.
     현재 상태: 방향 전환 필요 (경영 분석 → 광고 제작)'
),

-- ============================================
-- 4. AI Character Chat Platform
-- ============================================
(
    'mvp_character_001',
    'AI 캐릭터 채팅 플랫폼',
    'https://github.com/haewung/ai-character-chat-platform',
    'next',                             -- nano-banana + video 시스템 통합 필요
    'world_builder',                    -- 엔터테인먼트 + 감정 연구
    'core',                             -- AGI 관계형 AI 실험
    '["emotional", "ethical"]'::json,   -- 중독성, 의존성 이슈
    'idea',                             -- 재미로 만들기 시작
    0.80,                               -- 높은 잠재력
    'nano-banana + video 시스템 통합 시 시장 장악 자신 있음.
     AGI "관계" 철학 실험장.
     현재 상태: 아이디어 단계, 기술 통합 대기'
),

-- ============================================
-- 5. Reinforcement (강화학습 게임)
-- ============================================
(
    'mvp_rl_game_001',
    'Reinforcement - Three.js 강화학습 실험',
    'https://github.com/haewung/Reinforcement',
    'later',                            -- 연구용
    'capability_builder',               -- 기술 학습
    'independent',
    '["technical"]'::json,
    'idea',                             -- 실험 단계
    0.30,                               -- 낮은 우선순위 (학습용)
    'Three.js 기반 강화학습 환경.
     수익화 목표 없음, 순수 기술 실험.
     현재 상태: 프로토타입 수준'
);

-- ============================================
-- PRIORITY SORTING (자동 계산)
-- ============================================
-- Decision OS가 자동으로 재계산할 예정
-- 현재는 수동 점수 기반

-- 예상 우선순위:
-- 1. SaaSA (0.90) - 빠른 수익
-- 2. LMS (0.85) - 조 단위 시장
-- 3. Character Chat (0.80) - 기술적 돌파구
-- 4. Marketing Platform (0.75) - 방향 전환 필요
-- 5. RL Game (0.30) - 학습용
