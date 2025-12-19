# Moonlight Development Start Script (PowerShell)

Write-Host "🌙 Moonlight Development Environment Starting..." -ForegroundColor Cyan

# 1. Start Docker (PostgreSQL + Redis)
Write-Host "`n📦 Starting Docker services..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\..\docker
docker-compose up -d

# 2. Wait for services
Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Instructions
Write-Host "`n✅ Docker services started!" -ForegroundColor Green
Write-Host @"

Next steps:

1. Start AI Core:
   cd packages/ai-core
   python -m pip install uv
   python -m uv pip install -e .
   python -m uv run -m uvicorn src.main:app --host 0.0.0.0 --port 8000

2. Start Web UI:
   cd packages/web-ui
   npm install
   npm run dev

3. Open http://localhost:5173

🌙 Happy coding!
"@


