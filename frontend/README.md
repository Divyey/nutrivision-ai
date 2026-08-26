# Frontend

React + TypeScript + Vite + Ant Design.

```bash
pnpm install
pnpm dev
```

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to your API origin (`http://127.0.0.1:8000` locally). Run the backend first.

Screens: public Home / Login / Register; signed-in Dashboard, Profile, Scan (`/detect`), and placeholder Recommend / Tracking / Progress. Architecture: `docs/architecture/FRONTEND.md`. Scan uses `POST /api/v1/food/predict` (004, detections only).

## Vercel

| Env | Branch | URL |
|---|---|---|
| Production | `production` | https://prod-nutrivision-ai.vercel.app |
| Development | `development` | https://dev-nutrivision-ai.vercel.app |

GitHub Actions deploys Preview from `development` and Production from `production`. Production uses `vercel deploy --prod --skip-domain` then `vercel promote` because auto-assign custom production domains is off. Dashboard **Production Branch** should be `production` when Vercel lets you save it.

Set the project **Root Directory** to `frontend`. Set `VITE_API_BASE_URL` to `https://nutrivision-ai-backend.fastapicloud.dev`. Put `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` in GitHub Actions secrets.

