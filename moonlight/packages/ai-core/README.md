# moonlight-ai-core

Moonlight AI Core (FastAPI) package.

- Entry: `src/main.py`
- API base path: `/api`

## Dependency management (uv)

From this directory:

```powershell
python -m pip install uv
python -m uv pip install -e .
python -m uv run -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Database migrations (Alembic)

Alembic is configured to read the database URL from `src.config.get_settings()`.

```powershell
python -m uv pip install alembic sqlalchemy

# Create initial migration (after you add ORM models under src/)
python -m uv run -m alembic -c alembic.ini revision --autogenerate -m "init"

# Apply migrations
python -m uv run -m alembic -c alembic.ini upgrade head
```

This file exists to satisfy `pyproject.toml` metadata (`readme = "README.md"`).
