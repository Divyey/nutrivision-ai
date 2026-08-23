# Frontend

React + TypeScript + Vite + Ant Design.

```bash
pnpm install
pnpm dev
```

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to your API origin (`http://127.0.0.1:8000` locally). Run the backend first.

Screens: public Home / Login / Register; signed-in Dashboard, Profile, Scan (`/detect`), and placeholder Recommend / Tracking / Progress. Architecture: `docs/architecture/FRONTEND.md`. Scan uses `POST /api/v1/food/predict` (004, detections only).

## Vercel

Production: https://nutrivision-ai-green.vercel.app/

Set the project **Root Directory** to `frontend`. Set `VITE_API_BASE_URL` to `https://nutrivision-ai-backend.fastapicloud.dev`. Put `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` in GitHub Actions secrets. `VERCEL_TOKEN` must be a **team or account** token for `divyeys-projects`, not a project-only `vcp_…` token. `VERCEL_ORG_ID` (`team_…`) belongs in project settings, not in `vercel --scope`. `vercel.json` turns off Vercel Git auto-deploy so Actions owns deploys: preview from `development` / PRs, production from `production`.

