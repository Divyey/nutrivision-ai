---
applyTo: "frontend/**/*.ts,frontend/**/*.tsx"
---

# Frontend

This app is React 19, TypeScript, Vite, Ant Design 6, React Router 7. Package manager: pnpm. Entry `src/main.tsx`. Routes: `src/routes/AppRoutes.tsx`.

Product contracts (predict JSON, analyzing %, kcal on Scan) live in the root Copilot instructions. Change them only if the ticket says so.

## Organization

- `pages/` — screens (`LoginPage`, `DetectionPage`, and other `*Page` files).
- `services/{Name}Service/{Name}Service.ts` — API clients. Today: `AuthService`, `UserService`, `DetectionService` (food predict client). Do not rename `DetectionService` to `FoodService` unless the ticket asks; the backend class is already `FoodService`.
- `components/layout/` — `AppLayout`, `PublicLayout`, `DetectionLayout`, `BottomNavigationBar`, `PageSpinner`.
- There is no `components/ui/` folder. Do not create Ant Design wrapper folders (`Button.tsx`, `Form.tsx`, etc.). Use Ant Design primitives directly; put NutriVision-specific layout/widgets in `layout/` or next to the page that owns them.
- `hooks/` — `useAuth` / `AuthProvider`. HTTP: `lib/http.ts`. JWT: `lib/token.ts` (sessionStorage).
- `types/` — DTOs that match backend JSON (`auth.ts`, `user.ts`, `detection.ts`). Keep them in sync when the API changes.
- Do not add `features/`, `container/`, `atoms/`, `molecules/`, or `organisms/`.
- PascalCase for pages, services, and components; camelCase for hooks and utils.

## UI

- Use Ant Design for buttons, forms, layout, lists, tags, modals, and feedback. Do not rebuild those primitives.
- Scan phases today: capture → camera review → analyzing → results, plus `completing` and `error` (`types/detection.ts`). Gallery and drop skip review. Scan is fullscreen (`DetectionLayout`, no bottom nav). Other signed-in tabs use `AppLayout`.
- Always cover loading, error, and empty states (analyzing, retry, “No dishes detected.”).
- Stay usable on a phone-width screen. Camera review uses `object-fit: cover`. Analyzing and results use `object-fit: contain`.
- Keep accessible names on icon-only controls (see Results back button).

## TypeScript and data flow

- Do not use `any`. Share API shapes in `types/` and call them from services.
- All HTTP goes through `http()` in `lib/http.ts` (JSON or `FormData`; Bearer token unless `auth: false`). Do not duplicate fetch/auth headers in pages.
- Keep API and conversion logic in services/`types` helpers (`isAllowedImageFile`, profile unit helpers), not in presentational components.
- Auth is `AuthProvider` + `useAuth`, plus `PrivateRoute` / `GuestRoute` / `RequireCompleteProfile` / `RequireIncompleteProfile`. Do not add Redux or Zustand unless a ticket requires a store.

## Image upload and detection

- `DetectionService.analyze` posts `FormData` field `image` to `POST /api/v1/food/predict` and returns `FoodPredictResponse`.
- Allow jpeg/png/webp only (`ALLOWED_IMAGE_TYPES`).
- **Analyzing % is request UI**, not YOLO confidence. Do not bind it to `item.confidence`.
- Results draw boxes from `payload.items`, positioned with `image_width` / `image_height`. No placeholder boxes. Captions may show label + rounded confidence.
- Do not add kcal, portion, or meal-log UI on Scan / predict results unless the ticket includes it. Profile may already show `target_calories`; that is not Scan.
- Honor `AbortSignal` when leaving or canceling analyze (`DetectionPage`).

## Config and quality

- API host is `VITE_API_BASE_URL` only. Do not hardcode deployed URLs.
- Keep `tsc` and lint clean. Match neighboring Scan and Profile files.
- If a new library or global store is proposed, explain why Ant Design and current hooks are not enough.
