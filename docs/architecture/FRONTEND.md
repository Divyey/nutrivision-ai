# Frontend architecture plan

**Status:** first slice implemented (Auth V1 UI). Detection/tracking/recommendations are not built yet.

---

## Current NutriVision frontend

Auth V1 is implemented: AntD, React Router, `AuthService`, Login/Register/Dashboard.

```text
frontend/src/
├── App.tsx
├── AppRoutes/
├── components/layout/
├── hooks/useAuth.ts
├── hooks/AuthProvider.tsx
├── lib/http.ts
├── pages/{Home,Login,Register,Dashboard}/
├── services/AuthService/
└── types/auth.ts
```

---

## Legacy reference (inspected, not copied)

Flask + Jinja + mixed Bootstrap 3/4/5 + jQuery + Chart.js / EasyPieChart.

| Legacy | Role | New mapping |
|---|---|---|
| `header_footer.html` | Logged-in navbar + footer | `components/layout/AppLayout.tsx` (AntD `Layout` + `Menu`) |
| `login.html` / `register.html` public nav | Marketing navbar | `components/layout/PublicLayout.tsx` |
| `form_headerfooter.html` | Ad-hoc progress bar | AntD `Progress` — do not port |
| `home.html` / `index1.html` | Landing + photo detect | `pages/Home/`, `pages/Detection/` |
| `login.html` / `register.html` | Auth forms | `pages/Login/`, `pages/Register/` |
| `profilesetup.html` | Age/weight/height (V2) | **Out of V1** — later `pages/ProfileSetup/` |
| `index.html` | Post-login home | `pages/Dashboard/` |
| `track.html` / `add_food.html` | Diary | `pages/Tracking/`, `pages/AddFood/` |
| `progress.html` / daily / weekly | Charts + history | `pages/Progress/` |
| `profile.html` / `edit_profile.html` | Profile | `pages/Profile/` |
| `recommendation.html` / `recommendsetup.html` | Meal recs | `pages/Recommendation/` |
| `about.html` / `service.html` | Marketing | `pages/About/` (optional) |
| Flask `session` + redirects | Auth gate | `AppRoutes/PrivateRoute.tsx` + JWT |
| `static/css`, Bootstrap | Generic UI | **AntD** — do not recreate |
| Chart.js / EasyPieChart | Calorie rings | AntD Charts / `Progress` / `Statistic` |

Legacy problems we will **not** copy: mixed Bootstrap versions, server-rendered forms, no API client, no TypeScript, calories-as-template-strings, public and private nav mixed in templates.

---

## 1. Compare to the proposed architecture

| Proposed | Current | Gap |
|---|---|---|
| AntD as UI kit | Missing | Add `antd`, `@ant-design/icons`; Charts only when Progress/Detection need it |
| `App.tsx` + `AppRoutes/` | Missing | Add React Router |
| `pages/` | Missing | Add as we ship features |
| `services/*Service/` | Missing | Start with `AuthService` only (backend V1 exists) |
| `components/layout/` | Missing | Public + authenticated layouts |
| `components/ui/` | Missing | Empty until a NutriVision widget is needed |
| `hooks/`, `lib/`, `types/`, `utils/` | Missing | Add thin folders when first used |
| `features/` / atomic design | Absent | Keep absent |
| Vite + React + TS | Present | Keep |

---

## 2. Keep

- Vite + React 19 + TypeScript + ESLint
- `frontend/index.html`, `vite.config.ts`, `tsconfig*.json`
- `src/main.tsx` as the single mount
- `public/favicon.svg` (replace later if we have a brand mark)
- Empty-src policy: no leftover Vite demo pages

---

## 3. Rename

- npm `name`: `"frontend"` → `"nutrivision-ai"` (optional, not blocking)
- README: replace “architecture pending” with this plan once approved
- Branding in UI: legacy **NutriTrack** → **NutriVision AI**

No source files need renaming today; there are almost none.

---

## 4. Move

Nothing to move. `src/` only has `main.tsx`.

When code appears:

- API calls live in `services/`, not inside pages
- AntD usage stays in pages/layout; wrappers only in `components/ui/` if NutriVision-specific

---

## 5. Remove

Already gone: `App.css`, Vite `App.tsx`, `index.css` demo, hero/react/vite SVGs, `public/icons.svg`.

Do **not** add later:

- Custom Button/Input/Modal/Table
- Bootstrap / jQuery / Chart.js / EasyPieChart
- `features/`, `container/`, `atoms/`, `molecules/`, `organisms/`
- Global Redux/Zustand until a real cross-tree state problem appears (JWT can live in `lib/http.ts` + `sessionStorage` / memory + `useAuth`)

---

## 6. Implementation status

**Dependencies:** `antd`, `@ant-design/icons`, `react-router-dom`. Add `@ant-design/charts` only when Dashboard/Progress charts ship.

**First implementation slice (Auth V1 — matches backend 001):**

- `App.tsx` — `ConfigProvider` (theme) + router
- `AppRoutes/AppRoutes.tsx`, `PrivateRoute.tsx`
- `pages/Login/LoginPage.tsx`, `pages/Register/RegisterPage.tsx`
- `pages/Dashboard/DashboardPage.tsx` — authenticated landing stub
- `services/AuthService/AuthService.ts` → `POST /auth/register`, `/auth/login`, `GET/PATCH /auth/me`
- `lib/http.ts` — `fetch`/`axios` wrapper, `Authorization` header, no secrets in logs
- `hooks/useAuth.ts`, `hooks/AuthProvider.tsx`
- `types/auth.ts`
- `components/layout/AppLayout.tsx`, `PublicLayout.tsx`
- AntD theme tokens in `index.css` / `ConfigProvider` (responsive via `Grid.useBreakpoint` / `Row`/`Col`)

**Later pages (backend not V1 yet):** Detection, Nutrition, Tracking, Progress, Profile (V2 fields), Recommendation. Folders may exist as empty placeholders **or** be created when the matching backend service exists. Prefer **create when needed** to avoid fake screens.

**NutriVision-specific `components/ui/` (only when a page needs them):** e.g. `MealPhotoUpload`, `DetectionResultList`, `MacroRing` (if AntD Progress is not enough). Not a generic UI kit.

---

## 7. Proposed final structure

```text
frontend/src/
├── assets/                      # logos, empty until we have brand files
├── components/
│   ├── ui/                      # NutriVision-only widgets on top of AntD
│   └── layout/
│       ├── AppLayout.tsx        # Header + Sidebar/Menu + Content (logged in)
│       └── PublicLayout.tsx     # marketing/auth chrome
├── services/
│   ├── AuthService/
│   │   └── AuthService.ts       → backend/services/auth/
│   ├── FoodService/             → services/food/          (later)
│   ├── DetectionService/        → services/detection/     (later)
│   ├── NutritionService/        → services/nutrition/     (later)
│   ├── MealService/             → services/meals/         (later)
│   └── RecommendationService/   → services/recommendations/ (later)
├── pages/
│   ├── Home/HomePage.tsx        # public landing (legacy home)
│   ├── Login/LoginPage.tsx
│   ├── Register/RegisterPage.tsx
│   ├── Dashboard/DashboardPage.tsx
│   ├── Detection/DetectionPage.tsx      # later
│   ├── Tracking/TrackingPage.tsx        # later
│   ├── Progress/ProgressPage.tsx        # later
│   ├── Profile/ProfilePage.tsx          # later
│   └── Recommendation/RecommendationPage.tsx  # later
├── AppRoutes/
│   ├── AppRoutes.tsx
│   └── PrivateRoute.tsx
├── hooks/                       # useAuth.ts, AuthProvider.tsx, …
├── lib/                         # http.ts, antd theme
├── types/
├── utils/
├── App.tsx
├── main.tsx
└── index.css                    # AntD reset + app tokens only
```

**Flow**

```text
main.tsx → App.tsx (ConfigProvider)
  → AppRoutes
    → PublicLayout → Login | Register | Home
    → PrivateRoute → AppLayout → Dashboard | …
      → AuthService (etc.)
        → FastAPI
          → backend/services/{domain}/
            → Neon
```

**Naming**

- Folders for domains/pages: PascalCase (`AuthService/`, `Login/`)
- Generic folders: lowercase (`components/`, `pages/`, `hooks/`)
- Components/files: PascalCase (`LoginPage.tsx`, `PrivateRoute.tsx`)
- Hooks/utils: camelCase (`useAuth.ts`, `formatNutrition.ts`)

---

## 8. Changes, briefly

The current app is an empty Vite shell. The new architecture is **AntD-first, domain-aligned, page/service split**, matching FastAPI `services/auth/` now and other backend services later.

We keep the toolchain, add React Router + AntD, and only custom-build NutriVision widgets. Legacy templates tell us **which screens exist**, not how to structure React. First build after approval: Login, Register, token-gated Dashboard stub — nothing else.

---

## Review checklist (before coding)

- [x] Approve folder layout and naming
- [x] Approve AntD as the only generic UI kit
- [x] Approve first slice = Auth V1 only (no Detection UI yet)
- [x] Approve JWT in `AuthService` + `PrivateRoute` (no Redux)
