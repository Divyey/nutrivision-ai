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

Set Application Directory to `backend`. Configure `DATABASE_URL`, `JWT_SECRET_KEY`, and `CORS_ORIGINS` (must include https://nutrivision-ai-green.vercel.app).

GitHub Actions runs tests on `development` and deploys to FastAPI Cloud from `production`. Secrets: `FASTAPI_CLOUD_TOKEN`, `FASTAPI_CLOUD_APP_ID`. Point the Cloud deploy token at branch `production` (`fastapi cloud setup-ci --secrets-only --branch production`). See [deploy tokens](https://fastapicloud.com/docs/advanced-features/deploy-tokens/).
