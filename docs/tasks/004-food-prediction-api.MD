---
name: 004 Food Prediction API
overview: "YELLOW plan: in-process ONNX Runtime for local+prod (no torch in prod). Export+parity is a hard gate. 004 returns detections only (no kcal). Split liveness vs food readiness. FakeDetector in CI."
todos:
  - id: export-gate
    content: "GATE (do first): export best.pt→best.onnx; record Ultralytics version, imgsz, nms flag, output tensors; Pillow letterbox vs Ultralytics; box remap; conf>0.4; side-by-side vs predict(); CPU latency + RSS (no invented numbers)"
    status: completed
  - id: food-api
    content: Food service matching auth/users layers; JWT predict; Fake/Onnx/Unavailable detectors; lifespan session; threadpool; lock
    status: completed
  - id: health-split
    content: GET /health stays DB+auth+users (liveness of API). GET /api/v1/food/health is readiness. Predict 503 if model down. Amend ML health rule.
    status: completed
  - id: tests
    content: CI unit/API tests with FakeDetector (no .onnx). Skipped integration if FOOD_ONNX_SMOKE=1. No torch in CI.
    status: completed
  - id: frontend-results
    content: Type detections-only contract; Results overlay+list+confidence; empty/503; object-fit contain. No kcal UI. Analyzing % unchanged.
    status: completed
  - id: docs-deploy
    content: Tracker 004 detections-only; kcal deferred; Cloud RAM after measured RSS; 1 worker; FOOD_MODEL_PATH; tsc/lint/pytest
    status: completed
isProject: false
---

# 004 Food Prediction API (revised after codebase review)

**Verdict: YELLOW.** Architecture is the right V1. Do not treat the previous plan as implementable until the ONNX export gate passes, and do not ship kcal on this ticket.

Legend used below: **FACT** (repo/legacy), **REC** (engineering), **ASSUMPTION** (unmeasured), **GATE** (must validate).

---

## Decisions already made (you)

1. **Kcal is out of 004.** Response is detections only. Nutrition/lookup calories are a later domain (not silently “one box = one serving” on the wire).
2. **Health is split.** `GET /health` stays process + DB + auth/users. Missing `best.onnx` must **not** 503 the whole app. `GET /api/v1/food/health` + `POST /predict` return 503 if inference cannot run. **Amend** `.cursor/rules/backend-service-health.mdc` for ML services.

## Do not create a separate “ONNX optimization” 005

Tracker **005 is meal logging**, **006 is feedback**. A draft **NV-005 Food Model Production Optimization** duplicates 004’s export/parity/ORT slice and is written as if NutriVision already serves PyTorch YOLO (**FACT: it does not**).

**REC:** Keep ONNX as **004 step 1** (same FastAPI + ORT CPU locally and in prod). Do **not** ship 004 on torch then “optimize” to ONNX. YOLO26 stays a **later** ticket with a number that does not collide with 005/006 (e.g. NV-010).

---

## Facts verified in this repo / legacy

- No backend food service, no `UploadFile`, no `.pt`/`.onnx` in NutriVision, no food tables. Only `users`.
- Frontend **FACT:** `DetectionService.analyze` → `POST /api/v1/food/predict`, multipart field **`image`**, JWT via `http()`. `FoodPredictResponse = unknown`. Phases include `completing`. `ResultsPhase.tsx` is a stub. Analyzing % is UI-only. JPEG/PNG/WebP (+ `image/jpg`).
- Auth **FACT:** `get_current_user`; 401 `"Not authenticated"` / `"Could not validate credentials"`.
- Health **FACT:** `GET /health` 503 if any `SERVICE_CHECKS` entry is unhealthy. Auth/users checks are DB only.
- Layers **FACT:** `routes/` + `controller/` + `schema/` + `services/` + `{domain}_health.py`.
- Legacy **FACT:** `/Users/divyey007/Downloads/Food Recogntion 2024 (1)/Code/best.pt` (~22.5 MB). `YOLO(path)` **per request**. `predict(conf=0.25)` then keep `conf > 0.4`. `class_mapping` 0–29 kebab labels + undocumented int “calories”. Photo kcal = count(boxes) × int; **not** USDA, **not** per-100g, **not** box area. Total has a dead string-key add. Viz resize 800×400 is **draw-only**. No ONNX in legacy. No `requirements.txt`.
- Tracker **FACT:** 004 text still says kcal; this ticket **narrows** that. 005 is meal log.

---

## What was wrong in the previous 004 plan

- **`nms=True` in-graph:** **ASSUMPTION.** YOLOv8s ONNX NMS is version-sensitive. **GATE:** try it; if the graph/output is not simple boxes, use **numpy NMS** (still no OpenCV, no torch).
- **Pillow “equals YOLO preprocess”:** **ASSUMPTION.** Must match Ultralytics letterbox (ratio, stride-32 pad, 114, RGB/255/CHW) and **export `imgsz`**. Training imgsz in docs is 800; live Flask did not pass `imgsz` (**possible 640 vs 800 mismatch in legacy itself**).
- **Box remap:** required if letterbox is used. **GATE.**
- **PyTorch vs ONNX parity:** **GATE**, not optional docs.
- **“~2 GB RAM”:** **ASSUMPTION, not a measurement.** Size the Cloud instance from **measured RSS** after the smoke test. 512 MB may or may not work.
- **kcal on the JSON:** product-inaccurate. **Out of 004** per your decision.
- **Registering food on aggregator `/health`:** would mark auth “down” if the model file is missing. **Do not.**
- **`food_preprocess.py` as its own layer:** skip unless the letterbox function is large; keep it next to the ONNX detector.
- **Torch as local server path:** **REC:** local `uvicorn` uses the same ONNX path as prod. Ultralytics only in an export venv.

---

## V1 architecture (**REC**, good)

```text
React  →  FastAPI  →  food_service  →  FoodDetector (Protocol)
                                         ├─ OnnxFoodDetector   # local + prod
                                         ├─ FakeFoodDetector   # CI
                                         └─ UnavailableDetector
                                              → onnxruntime CPU + best.onnx
```

- Protocol: yes (matches test override style; later HTTP detector without changing the route).
- Load `InferenceSession` once in **lifespan**. Inject via `app.state` or a getter.
- **Threadpool:** yes (`run_in_threadpool`) — `session.run` blocks.
- **Lock:** yes around `session.run` (ORT session is not a documented concurrent API). Cheap at V1 QPS.
- **1 worker:** **REC** until measured; each worker duplicates the session.
- **No microservice** until CPU/RAM/QPS evidence.
- **onnxruntime** (CPU), not `onnxruntime-gpu`. FastAPI Cloud has no GPU.
- **No OpenCV** unless the export gate proves Pillow letterbox cannot match (unexpected).
- **numpy:** required (ORT + NMS fallback).
- **Pillow:** decode/validate/letterbox.
- **No torch/ultralytics** in `requirements.txt` / Cloud install.

Export (dev venv only):

```text
best.pt  →  ultralytics+torch  →  best.onnx  →  git  →  local/prod session
```

---

## API contract (004)

`POST /api/v1/food/predict`  
Auth: JWT. Field: `image`. Types: jpeg/png/webp.

```json
{
  "image_width": 3024,
  "image_height": 4032,
  "items": [
    {
      "class_id": 6,
      "label": "gulab-jamun",
      "confidence": 0.872,
      "box": { "x1": 120.5, "y1": 40.0, "x2": 510.2, "y2": 388.1 }
    }
  ]
}
```

- `box`: original image pixels, `x1 < x2`, `y1 < y2`, floats OK.
- `confidence`: model score in `(0.4, 1]` after the same `> 0.4` rule as legacy.
- `label`: kebab slug from the mapping (display title-case on the client).
- `class_id`: keep (debug + later nutrition join). No `id` UUID in V1.
- **No `kcal`, no `total_kcal`.** Empty plate: **200** `items: []`.

Errors: **401** unauthenticated; **415** bad MIME; **400** undecodable/too many pixels; **413** over byte cap (~8 MB); **503** model not loaded; **422** missing `image`. Do not leak paths/ORT internals.

---

## Files (match auth/users; no extra layers)

```text
backend/services/food/
  routes/food_routes.py
  controller/food_controller.py
  schema/food_schema.py
  services/food_service.py
  services/food_health.py
  services/food_detector.py      # Protocol, Onnx, Fake, Unavailable, letterbox helpers
  services/food_classes.py       # id → slug only (no kcal)
backend/scripts/export_food_onnx.py   # not imported by the app
backend/models/food/best.pt            # export source (optional in git)
backend/models/food/best.onnx          # served artifact
```

Settings: `FOOD_MODEL_PATH`, `FOOD_MAX_IMAGE_BYTES`, `FOOD_MAX_PIXELS`, `FOOD_CONFIDENCE_MIN=0.4`.

---

## Tests

| Kind | Where | Model file |
|---|---|---|
| Unit | letterbox math, box remap, conf filter, class labels | no |
| API | 401/415/400/413/200 empty/200 items/503 | FakeDetector autouse |
| Contract | Pydantic + TS types match | no |
| Model validation | skipped unless `FOOD_ONNX_SMOKE=1` | yes, local |
| Deploy smoke | authenticated predict after Cloud deploy | yes |

CI: `pytest -q` never requires `.onnx` or torch. Installing `onnxruntime` in CI via requirements is OK; do not `InferenceSession` in unit tests.

---

## Security (this ticket only)

In-memory bytes (no temp file). MIME allow-list + Pillow verify. Max bytes + max pixels (decompression bomb). JWT. 1 inference lock. Starlette upload limit. Timeouts via Cloud/proxy. Generic 503/400 messages.

---

## Frontend

Keep capture → review → analyzing → completing → results. Type `FoodPredictResponse`. Overlay boxes on `object-fit: contain` using `%` of `image_width/height`. List: label + confidence as **text**. Empty copy. 503 → existing error phase, clearer message. **No kcal. No Confirm & Log.** Do not touch analyzing Progress.

---

## Deployment

Same inference path locally and on FastAPI Cloud. Commit `best.onnx` (GitHub warn ≥50 MB — **FACT of GitHub**, actual onnx size **GATE**). Cloud install must **not** pip torch. Worker count 1 until measured. RAM: **set after RSS benchmark**, not “2 GB” as gospel.

---

## Acceptance

1. Export gate notes checked in (commands, ultralytics version, output schema, parity summary, latency/RSS as measured).
2. CI green without `.onnx`.
3. Local Scan: boxes + labels + confidence on Results; analyzing % ≠ confidence; empty 200; 401 without token.
4. `/health` 200 if DB up even when model missing; `/api/v1/food/health` 503 if model missing; predict 503 then.
5. Cloud predict works **or** ticket blocked on instance size with measured RSS — not by installing PyTorch.
6. No kcal in JSON or Results.

---

## Implementation order

1. Export gate (fail 004 here if ONNX is not faithful).
2. `food_classes` + schema (no kcal) + Protocol + FakeDetector.
3. Routes/controller/service + JWT + validation; tests on Fake.
4. OnnxFoodDetector + lifespan + threadpool/lock; local smoke.
5. Health split + rule amend + test_health still auth/users-only on aggregator.
6. Frontend types + Results overlay.
7. Docs/tracker (kcal deferred) + Cloud config from measurements.
8. `tsc` / `lint` / `pytest`.
