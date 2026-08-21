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
