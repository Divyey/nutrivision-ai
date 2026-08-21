# Frontend

React + TypeScript + Vite + Ant Design.

```bash
pnpm install
pnpm dev
```

Vite proxies `/auth` and `/health` to FastAPI at `http://127.0.0.1:8000`. Run the backend first.

V1 screens: Home, Login, Register, Dashboard (JWT). Architecture: `docs/architecture/FRONTEND.md`.

## Vercel

Production: https://nutrivision-ai-green.vercel.app/

Set the project **Root Directory** to `frontend`. Set `VITE_API_BASE_URL` to `https://nutrivision-ai-backend.fastapicloud.dev`. Put `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` in GitHub Actions secrets. `VERCEL_TOKEN` must be a **team or account** token (Create Token → scope the team `divyeys-projects`). A project-only token (`vcp_…`) makes `vercel pull` fail with “Could not retrieve Project Settings”. `vercel.json` turns off Vercel Git auto-deploy so Actions owns deploys: preview from `development` / PRs, production from `production`.
