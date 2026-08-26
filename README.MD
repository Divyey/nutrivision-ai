# NutriVision AI

Photograph a plate. Log the meal.

A personal ML project: a web app that detects Indian dishes in a food photo, then lets you confirm them and keep a simple calorie diary.

**Live app (production):** [prod-nutrivision-ai.vercel.app](https://prod-nutrivision-ai.vercel.app/)
**Dev preview:** [dev-nutrivision-ai.vercel.app](https://dev-nutrivision-ai.vercel.app/)

---

## What it is

NutriVision is an end-to-end food recognition + tracking prototype.

1. **Scan** — take or upload a photo of a meal.
2. **Detect** — a computer-vision model finds dishes in the frame (labels + bounding boxes).
3. **Log** — you confirm what was found, pick a meal slot, and save it.
4. **Track** — a daily diary shows calories and macros from a food table, not from guessing portion size from the photo.

The model is trained for a fixed set of Indian dishes. It will miss foods outside that set. Typed search exists so you can still log those meals.

This is a personal project, not a product or medical tool. Nutrition numbers are estimates for learning and demo.

---

## Idea (ML)

Classic applied-ML loop, not a notebook-only experiment:

- Object detection on meal photos (exported **ONNX**, CPU inference in the API).
- The API returns detections only (class, confidence, box). Calories are applied later when you log, from a nutrition catalog.
- Frontend is a mobile-first React app; backend is FastAPI; data lives in Postgres.

Stack in short:

| Layer | Choice |
|---|---|
| App | React, TypeScript, Vite, Ant Design |
| API | FastAPI, SQLAlchemy, JWT |
| ML | ONNX Runtime (food detector) |
| Data | PostgreSQL (Neon) |
| Hosting | Vercel (app), FastAPI Cloud (API) |

---

## Local setup (developers)

You need **Python 3.12**, **Node.js 20+**, **pnpm**, and a Postgres URL (Neon works).

### 1. Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # set DATABASE_URL and JWT_SECRET_KEY
alembic upgrade head
uvicorn main:app --reload
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend

```bash
cd frontend
pnpm install
cp .env.example .env        # VITE_API_BASE_URL=http://127.0.0.1:8000
pnpm dev
```

App: [http://localhost:5173](http://localhost:5173)

Register a user, finish profile setup, then use Scan and Tracking.

### Tests

```bash
cd backend && pytest
```

More detail: [backend/README.md](backend/README.md), [frontend/README.md](frontend/README.md).

---

## Repo layout

```text
frontend/    React app
backend/     FastAPI, ML weights, migrations
docs/        architecture and task notes
```

Feature work targets `development`. Production deploys from `production`.

---

## Links

- Production: https://prod-nutrivision-ai.vercel.app/
- Development: https://dev-nutrivision-ai.vercel.app/
- API: https://nutrivision-ai-backend.fastapicloud.dev/
- API health: https://nutrivision-ai-backend.fastapicloud.dev/health
