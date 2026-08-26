# Frontend architecture plan

**Status:** Auth (001), profile/goals (002), food-recognition UI (003), food **prediction API** (004, detections only), food **tracking / diary** (005), and food **catalog search + typed Add** (006) are implemented. Prediction feedback is not.

---

## Current NutriVision frontend

AntD, React Router, JWT via `useAuth`. Logged-in chrome is a header + **bottom nav** (no sider). Scan is fullscreen outside `AppLayout`.

```text
frontend/src/
├── App.tsx
├── routes/                    # AppRoutes, PrivateRoute, GuestRoute, profile gates
├── components/layout/         # AppLayout, PublicLayout, DetectionLayout, BottomNavigationBar
├── hooks/useAuth.ts
├── hooks/AuthProvider.tsx
├── lib/http.ts                # JSON + FormData + AbortSignal
├── pages/{Home,Login,Register,Dashboard,Profile,ProfileSetup,Detection}/
├── pages/{Recommendation,Tracking,Progress}/   # empty routes until later tickets
├── services/{AuthService,UserService,DetectionService}/
└── types/{auth,user,detection}.ts
```

**003 detect flow:** `/detect` → capture → review → analyzing (UI-only progress) → results. `DetectionService.analyze` POSTs multipart `image` to `/api/v1/food/predict`; 004 returns items, boxes, and confidence (no kcal).

---

## Legacy reference (inspected, not copied)

Flask + Jinja + mixed Bootstrap 3/4/5 + jQuery + Chart.js / EasyPieChart.

| Legacy | Role | New mapping |
|---|---|---|
| `header_footer.html` | Logged-in navbar + footer | `AppLayout` header + `BottomNavigationBar` |
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

**Implemented:**

- Auth V1 (001): Login, Register, JWT, `AuthService` → `/api/v1/auth/*`
- Profile & goals (002): `/register/setup`, `UserService`, inline Profile view/edit (name via `PATCH /api/v1/auth/me`, goals via `PATCH /api/v1/users/me`)
- Food recognition UI (003): `DetectionLayout` + `pages/Detection/`, `DetectionService`
- Food prediction (004): ONNX `POST /api/v1/food/predict`; Results maps boxes, labels, confidence (not kcal)
- Food tracking (005): Confirm & Log + Tracking diary (four slots + water). `MealService` → `/api/v1/meals/*`. Snapshots from `dish_nutrition` at write time. CSV has 27 INDB rows; ghevar, jalebi, and bhature are empty (log returns 400).
- Canonical catalog (006): `NutritionService` → `GET /api/v1/nutrition/search` (and GET-by-id for edit). Tracking **Add** / pencil searches the catalog and logs `source=typed`. Scan Confirm & Log still uses `dish_nutrition`.
- App shell: `BottomNavigationBar` — Home | Recommend | Scan | Tracking | Progress. `/detect` hides the bar.

**Not implemented (do not fake APIs):**

- 009 — prediction thumbs up/down
- Cited per-100g values for ghevar, jalebi, and bhature (class_ids 4, 8, 12)

Recommend / Progress routes exist as placeholders only.

**NutriVision-specific `components/ui/` (only when a page needs them):** e.g. `MealPhotoUpload`, `DetectionResultList`, `MacroRing` (if AntD Progress is not enough). Not a generic UI kit.

---

## 7. Proposed final structure

```text
frontend/src/
├── assets/                      # logos, empty until we have brand files
├── components/
│   ├── ui/                      # NutriVision-only widgets on top of AntD
│   └── layout/
│       ├── AppLayout.tsx              # header + content + bottom nav
│       ├── BottomNavigationBar.tsx
│       ├── DetectionLayout.tsx        # fullscreen /detect (no bottom nav)
│       └── PublicLayout.tsx
├── services/
│   ├── AuthService/           → backend/services/auth/
│   ├── UserService/           → backend/services/users/
│   ├── DetectionService/      → POST /api/v1/food/predict (004)
│   ├── FoodService/           → services/food/          (later)
│   ├── NutritionService/      → GET /api/v1/nutrition/search (006)
│   ├── MealService/           → services/meals/         (005)
│   └── RecommendationService/ → services/recommendations/ (later)
├── pages/
│   ├── Home/HomePage.tsx
│   ├── Login/LoginPage.tsx
│   ├── Register/RegisterPage.tsx
│   ├── Dashboard/DashboardPage.tsx
│   ├── Detection/DetectionPage.tsx    # 003 UI; Results mapping is 004
│   ├── Tracking/TrackingPage.tsx      # 005 diary + 006 typed search Add
│   ├── Progress/ProgressPage.tsx      # placeholder
│   ├── Profile/ProfilePage.tsx
│   └── Recommendation/RecommendationPage.tsx  # placeholder
├── routes/
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
    → PrivateRoute + complete profile
         ├── AppLayout + BottomNavigationBar → Dashboard | Recommend | Tracking | Progress | Profile
         └── DetectionLayout → /detect (capture → review → analyzing → results)
      → AuthService / UserService / DetectionService
        → FastAPI
          → backend/services/{domain}/
            → Neon
```

Analyzing progress % is **in-flight UI only**. YOLO confidence and class labels come from the 004 JSON. Kcal is not in 004.

**Naming**

- Folders for domains/pages: PascalCase (`AuthService/`, `Login/`)
- Generic folders: lowercase (`components/`, `pages/`, `hooks/`)
- Components/files: PascalCase (`LoginPage.tsx`, `PrivateRoute.tsx`)
- Hooks/utils: camelCase (`useAuth.ts`, `formatNutrition.ts`)

---

## 8. Changes, briefly

AntD-first, domain-aligned, page/service split. Legacy templates tell us **which screens exist**, not how to structure React.

---

## Review checklist (before coding)

- [x] Approve folder layout and naming
- [x] Approve AntD as the only generic UI kit
- [x] Approve first slice = Auth V1 only (no Detection UI yet)
- [x] Approve JWT in `AuthService` + `PrivateRoute` (no Redux)
- [x] 003: detect UI + bottom nav; predict API and meal log stay 004/005
- [x] 004: detections-only predict API + Results overlay (no kcal)
