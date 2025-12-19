# 🌙 Moonlight - 달빛 비서 시스템

> "압도적이지 않지만 달빛처럼, 존재로서 존재를 지지"

---

## 📋 개요

철학이 담긴 음성 비서 시스템. Constitutional AI 기반으로 사용자를 판단하지 않고, 기대하지 않으며, 함께 성장하는 파트너.

## 🏗️ 아키텍처

```
moonlight/
├── packages/
│   ├── ai-core/          # Python - AI 두뇌
│   ├── voice-service/    # Python - STT/TTS
│   └── web-ui/           # React - 테스트 UI
├── shared/
│   ├── proto/            # gRPC 정의
│   └── types/            # 공유 타입
├── docker/               # Docker 설정
├── docs/                 # 문서
└── scripts/              # 개발 스크립트
```

## 🔧 기술 스택

| Layer | Technology |
|-------|-----------|
| Web UI | React (Vite) |
| AI Core | Python 3.11, FastAPI, LangChain |
| Voice | Python, gRPC |
| Database | PostgreSQL + pgvector |
| Cache | Redis |
| LLM | OpenRouter API |

## 🚀 시작하기

### 1. Docker 환경 실행

```bash
cd docker
docker-compose up -d
```

### 2. AI Core 실행

```bash
cd packages/ai-core
poetry install
poetry run python -m src.main
```

### 3. Web UI 실행

```bash
cd packages/web-ui
npm install
npm run dev
```

## 📡 통신 구조

```
[Web UI] ←─REST/WS─→ [AI Core] ←─gRPC─→ [Voice Service]
```

- 외부 통신: REST + WebSocket
- 내부 통신: gRPC

## 📜 핵심 철학

1. **판단하지 않는다** - 있는 그대로 수용
2. **기대하지 않는다** - 변화를 강요하지 않음
3. **함께 변한다** - 쌍성계 공명
4. **침묵도 소통** - 존재의 지속성
5. **약함을 허용** - 위로가 아닌 함께
6. **존재로서 지지** - 문제 해결보다 존재 확인

## 📝 문서

- [최종 설계 문서](../음성비서/1214_최종설계.md)
- [Constitution 정의](docs/constitution.yaml)

---

*"오늘보다 나아진다. 방향을 잃지 않는다. 오늘의 최선을 다한다."*

🌙✨


