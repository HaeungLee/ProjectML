# Moonlight 실행법 (Windows 기준)

이 문서는 `moonlight/`를 **로컬에서 띄워서 E2E(Web UI → AI Core → OpenRouter)** 까지 확인하는 절차를 정리합니다.

---

## 0) 포트 정책 (충돌 방지)

여러 프로젝트가 Postgres/Redis를 공유하는 환경을 고려해서 Moonlight는 **기본 포트를 피해서** 씁니다.

- Postgres: `localhost:15433` → 컨테이너 `5432`
- Redis: `localhost:6381` → 컨테이너 `6379`
- AI Core(FastAPI): `http://localhost:8000`
- Web UI(Vite): `http://localhost:5173`

포트 매핑은 `docker/docker-compose.yml`에 반영되어 있습니다.

---

## 1) 준비물

- Docker Desktop
- Python 3.11
- Node.js 18+ (권장)

---

## 2) 환경변수 세팅 (OpenRouter Key)

- 파일: `packages/ai-core/.env`
- 필수:
  - `OPENROUTER_API_KEY` 값 설정

주의:
- `.env`는 커밋하지 마세요.
- 키가 외부에 노출되었다고 의심되면 OpenRouter에서 키를 재발급/폐기하세요.

---

## 3) 인프라(Postgres/Redis) 실행

```powershell
cd C:\Aprojects\ProjectML\moonlight\docker
docker-compose up -d
docker-compose ps
```

정상이라면 다음 포트로 떠 있어야 합니다.
- Postgres: `0.0.0.0:15433->5432`
- Redis: `0.0.0.0:6381->6379`

---

## 4) AI Core 실행

### uv 표준 (권장)

Windows에서 PATH 이슈를 피하기 위해 **`python -m uv`** 형태를 권장합니다.

```powershell
cd C:\Aprojects\ProjectML\moonlight\packages\ai-core

# uv 설치(최초 1회)
python -m pip install uv

# 의존성 설치 (개발용: editable)
python -m uv pip install -e .

# 서버 실행
python -m uv run -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 5) AI Core 동작 확인

### Healthcheck

```powershell
curl.exe http://localhost:8000/api/health
```

### Chat E2E

```powershell
$body = @{ user_id='dev_user'; message='안녕! 테스트야'; enable_tools=$true } | ConvertTo-Json
Invoke-RestMethod -Method Post http://localhost:8000/api/chat -ContentType 'application/json' -Body $body
```

참고:
- Windows PowerShell/콘솔 환경에 따라 한글이 깨져 보일 수 있습니다(출력 인코딩 이슈). 실제 응답은 Web UI에서 확인하는 것을 권장합니다.

---

## 6) Web UI 실행 (E2E 최종 확인)

```powershell
cd C:\Aprojects\ProjectML\moonlight\packages\web-ui
npm install
npm run dev
```

브라우저에서 접속:
- http://localhost:5173

Web UI는 Vite proxy로 AI Core에 붙습니다.
- `/api/*` → `http://localhost:8000`

---

## 7) 종료

- Web UI: 실행 터미널에서 `Ctrl + C`
- AI Core: 실행 터미널에서 `Ctrl + C`
- Docker:

```powershell
cd C:\Aprojects\ProjectML\moonlight\docker
docker-compose down
```

---

## 8) 트러블슈팅

### (1) 포트가 이미 사용 중

- 현재 Docker 포트 점유 확인:

```powershell
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

- Moonlight 포트를 바꾸려면:
  1) `docker/docker-compose.yml`의 host 포트 수정
  2) `packages/ai-core/.env`의 `POSTGRES_PORT`, `REDIS_PORT`도 동일하게 수정

### (2) WebSocket 사용 시 경로

현재 AI Core WS 엔드포인트는 `/api/chat/ws` 입니다.
- Web UI에서 WS를 붙일 계획이면 `packages/web-ui/vite.config.ts`의 WS proxy 경로를 정합성 있게 맞춰야 합니다.

### (3) uv 명령이 안 잡힐 때

- `uv`가 PATH에 없어도 `python -m uv ...`는 동작합니다.
- 예: `python -m uv --version`
