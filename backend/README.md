# NutriVision AI backend

Run from this directory (`backend/`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set DATABASE_URL and JWT_SECRET_KEY
alembic upgrade head
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Tests:

```bash
pytest
```

## FastAPI Cloud

Public API: https://nutrivision-ai-backend.fastapicloud.dev/

CI runs `fastapi deploy backend` from the repo root, so the uploaded app root is `backend/` (`main.py`, `pyproject.toml`). In the FastAPI Cloud dashboard, leave **Application Directory empty**. If it is set to `backend`, the builder looks for `backend/backend` and fails with `No such file or directory`.

Configure `DATABASE_URL`, `JWT_SECRET_KEY`, and `CORS_ORIGINS` (must include https://nutrivision-ai-green.vercel.app).

GitHub Actions runs tests on `development` and deploys from `production`. Secrets: `FASTAPI_CLOUD_TOKEN`, `FASTAPI_CLOUD_APP_ID`. See [deploy tokens](https://fastapicloud.com/docs/advanced-features/deploy-tokens/).
