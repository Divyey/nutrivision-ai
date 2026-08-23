# Food Recognition

**Purpose:** Identify food items in an uploaded photo (object detection), then pass class IDs to the calorie lookup.

**Status:** Verified as a YOLO **object-detection** model. Not the classification notebook in this repo.

### NutriVision (this repo)

| Ticket | Status | What |
|---|---|---|
| **003** UI | Done | `pages/Detection/` + `DetectionService.analyze` POSTs multipart field `image` to `POST /api/v1/food/predict`. Analyzing % is request UI, not YOLO confidence. |
| **004** API | Done (detections only) | FastAPI food service, `best.onnx` via ONNX Runtime CPU, JSON items/boxes/confidence, Results overlay. No kcal. Analyzing % is request UI. |
| **005** Log | Not started | Confirm & Log into Breakfast / Lunch / Snacks / Dinner; Water on Tracking. Photo predict does not pick a meal slot until this ticket. |

Legacy Flask: `GET /predict` form, `POST /prediction1` upload. Diary (`/track`) was a separate page (four meals, no water).

---

## Model name / architecture

| Field | Value | Evidence |
|---|---|---|
| Task | `detect` | `best.pt` pickle: `task` → `detect` |
| Type | `ultralytics.nn.tasks.DetectionModel` | `best.pt` pickle class name |
| Architecture | **YOLOv8s** (small detection) | `model` → `yolov8s.yaml` |
| Head | `ultralytics.nn.modules.Detect` | pickle module list; 3-scale Detect |
| File size | 22,563,299 bytes (~22 MB) | filesystem `Code/best.pt` |
| Date on disk | 2 Nov 2024 | filesystem |

YOLOv8s detection is consistent with file size (~21–23 MB). This is **not** `yolov8n-cls` (~3.1 MB after training in the notebook).

---

## Model file

`/Users/divyey007/Downloads/Food Recogntion 2024 (1)/Code/best.pt`

Loaded at inference by `app.py` `upload_file()` → `detect_and_visualize()`:

```171:171:/Users/divyey007/Downloads/Food Recogntion 2024 (1)/Code/app.py
        result_bytes, total_calories, items_with_calories = detect_and_visualize(img, r"/Users/divyey007/Downloads/Food Recogntion 2024 (1)/Code/best.pt", class_mapping)
```

Path is **hardcoded** to this machine.

---

## Classification vs detection

**Detection. Verified.**

Evidence that conflicts with `train_Using_YOLOV8.ipynb`:

| Source | Task | Classes |
|---|---|---|
| `best.pt` checkpoint | `DetectionModel`, `runs/detect/train` | `nc = 30` |
| `app.py` | `results[0].boxes.xyxy / conf / cls` | 30 IDs in `class_mapping` |
| `train_Using_YOLOV8.ipynb` | `YOLO("yolov8n-cls.pt")`, `task=classify` | 36 fruit/veg classes |

The notebook did **not** produce this checkpoint. It trained a different model (`runs/classify/train/weights/best.pt`, 3.1 MB, 36-class Classify head) on Google Colab. That file is not in the repo.

Runtime evidence: the app draws bounding boxes and has been observed counting multiple `gulab-jamun` detections (class 6 → 145 kcal). That only works with a detection model.

---

## Training dataset

**Inside the checkpoint (verified):**

- `data`: `/content/datasets/Food-recognition-1/data.yaml`
- `save_dir`: `runs/detect/train`
- Naming (`Food-recognition-1`) is typical of a **Roboflow** export.

**Not in this repository:**

- No `data.yaml`
- No images, labels, or Roboflow export
- `find` for `*.yaml` / `results.csv` / `args.yaml` under the project returned nothing useful

**Unknown — requires original Colab/Roboflow project:** dataset size, train/val split, annotation quality, whether class names in `data.yaml` were Indian dishes or numeric IDs.

The 36-class Kaggle fruit/vegetable set used in `train_Using_YOLOV8.ipynb` is **not** this dataset.

---

## Number of classes

**30.** Checkpoint stores `nc = 30` (`pickle` `BININT1` `0x1e` next to key `nc`). `app.py` `class_mapping` has keys `0..29`. `detected_items = [0]*30`.

---

## Class list

**Inside `best.pt`:** the `names` dict maps `0..29`. Visible stored name strings are mostly **numeric** (`"10"` … `"29"`). Classes 0 and 1 are pickle-interned short strings (very likely `"0"` / `"1"`). **No Indian dish names appear as UTF-8 in the checkpoint.**

**Human-readable names used by the app** (the labels users see) come only from `app.py` `class_mapping` (L42–73):

| ID | Label | Hardcoded kcal |
|---|---|---:|
| 0 | aloo-gobi | 108 |
| 1 | aloo-fry | 125 |
| 2 | dum-aloo | 164 |
| 3 | fish-curry | 241 |
| 4 | ghevar | 61 |
| 5 | green-chutney | 21 |
| 6 | gulab-jamun | 145 |
| 7 | idli | 40 |
| 8 | jalebi | 150 |
| 9 | chicken-seekh-kebab | 158 |
| 10 | kheer | 266 |
| 11 | kulfi | 136 |
| 12 | bhature | 230 |
| 13 | lassi | 183 |
| 14 | mutton-curry | 298 |
| 15 | onion-pakoda | 80 |
| 16 | palak-paneer | 338 |
| 17 | poha | 270 |
| 18 | rajma-curry | 235 |
| 19 | rasmalai | 188 |
| 20 | samosa | 308 |
| 21 | shahi-paneer | 261 |
| 22 | white-rice | 135 |
| 23 | bhindi-masala | 225 |
| 24 | chicken-biryani | 348 |
| 25 | chai | 54 |
| 26 | chole | 311 |
| 27 | coconut-chutney | 105 |
| 28 | dal-tadka | 260 |
| 29 | dosa | 106 |

**Uncertainty:** we cannot prove from the checkpoint alone that class 6 *is* gulab-jamun in the original training labels. The app *treats* ID 6 as gulab-jamun. A live screenshot of the running app detecting gulab-jamun is consistent with that mapping, but original `data.yaml` names remain unverified.

---

## Input requirements

- Upload extensions: `.jpg`, `.jpeg`, `.png` (`ALLOWED_EXTENSIONS`, `app.py` L40, L155–156)
- Decoded with OpenCV: `cv2.imdecode(..., cv2.IMREAD_UNCHANGED)` (`app.py` L169)
- Training `imgsz`: **800** (checkpoint `imgsz` BININT2 `0x0320`)
- Ultralytics resizes internally during `predict()`; the app does **not** resize before inference

---

## Preprocessing

**App-side (before YOLO):** none beyond decode. Uses deprecated `np.fromstring`.

**After YOLO (visualization only):** resize annotated image to **800×400** and scale boxes (`app.py` L93–105). This is display-only, not model input.

**Training augmentations (from checkpoint args):** mosaic, mixup/copy_paste flags present; `hsv_*`, `translate`, `scale`, `fliplr` present as Ultralytics defaults. Exact numeric values were not fully decoded; `optimizer=SGD`, `close_mosaic=10`.

---

## Training configuration (from `best.pt` args)

| Arg | Value |
|---|---|
| task | detect |
| model | yolov8s.yaml |
| data | `/content/datasets/Food-recognition-1/data.yaml` |
| epochs | **25** |
| patience | 50 |
| batch | 16 |
| imgsz | 800 |
| optimizer | SGD |
| pretrained | true |
| workers | 8 |
| save_dir | runs/detect/train |
| val | true |

**Unknown:** mAP, precision/recall, confusion matrix. No `results.csv` or plots in the repo. `best_fitness` in the pickle is `None` (not stored in this snapshot).

---

## Inference process

1. `POST /prediction1` (`upload_file`, L158)
2. Decode bytes → OpenCV image
3. `YOLO(model_path)` constructed **on every request** (L82) — no process-level cache
4. `model.predict(source=img, conf=0.25)` (L84)
5. Read `boxes.xyxy`, `boxes.conf`, `boxes.cls`
6. Keep detections with **conf > 0.4** (second threshold, L109)
7. Increment per-class counts; look up `class_mapping`
8. Draw label + box; JPEG-encode; return to `index1.html`

Routes: `GET /predict` shows the form; `POST /prediction1` runs inference. Public marketing copy is on `index1.html` (“Smart Food Recognition & Personalized Diet”).

---

## Output format

`detect_and_visualize` returns:

1. JPEG bytes of the annotated 800×400 image
2. `total_calories` (see calorie-estimation.md — this field is buggy)
3. `items_with_calories`: list of `{label, calories: "count * kcal.00 = total", count}`

The UI displays the image (base64), item list, and total.

---

## Confidence handling

| Stage | Threshold |
|---|---|
| Ultralytics `predict(conf=...)` | 0.25 |
| App counting / drawing | 0.4 |

Boxes between 0.25 and 0.4 are predicted then discarded. No NMS settings are passed (Ultralytics defaults). No calibration.

---

## Known limitations

- Closed set of 30 Indian dishes; anything else is missed or mislabeled
- Count × fixed kcal; box size is unused (not portion estimation)
- Model reloaded every request
- Hardcoded absolute path
- No evaluation artifacts in repo
- Numeric class names in the checkpoint; dish names only in Python
- `np.fromstring` is deprecated
- Visualization aspect ratio is forced to 800×400 (distorts plates)

---

## Known inconsistencies

1. **`train_Using_YOLOV8.ipynb` ≠ `best.pt`.** Notebook = YOLOv8n-cls, 36 fruit/veg classes, 20 epochs, 224px, AdamW. Checkpoint = YOLOv8s-detect, 30 classes, 25 epochs, 800px, SGD, `Food-recognition-1`.
2. Class names live in `app.py`, not in the model.
3. Older notes that treated `best.pt` as the notebook classifier were **wrong**. File size, `DetectionModel`, and `nc=30` contradict that.

---

## Dependencies

Runtime: `ultralytics`, `torch` (pulled in by ultralytics), `opencv-python` / `cv2`, `numpy`.

Training environment (from checkpoint / notebook, not this machine): Ultralytics YOLO v8, Google Colab (`/content/...`).

---

## How to reproduce inference

```python
from ultralytics import YOLO
import cv2

model = YOLO("Code/best.pt")
img = cv2.imread("some_food.jpg")
results = model.predict(source=img, conf=0.25)
for b, c, cls in zip(results[0].boxes.xyxy, results[0].boxes.conf, results[0].boxes.cls):
    if float(c) > 0.4:
        print(int(cls), float(c), b.tolist())
```

Then map `int(cls)` through `class_mapping` in `app.py`.

To **retrain**, the original `Food-recognition-1` dataset is required and is **not in this repo**.

---

## Architecture sketch (from checkpoint + prior graph export)

YOLOv8s detection: Conv backbone (3→32→64→128→256→512) + C2f + SPPF, PAN/FPN neck, Detect head with 3 scales, DFL box regression. Matches the cleaned layer table previously recorded in `yolov8-model.md`.
