# Model inventory

Source of truth: legacy app at `Food Recogntion 2024 (1)/Code/`. Claims are tagged by verification.

| Purpose | Model/System | File | Type | Dataset | Input | Output | Used By | Status |
|---|---|---|---|---|---|---|---|---|
| Food recognition (production) | YOLOv8s object detection | `Code/best.pt` | Trained ML — **detection** | `/content/datasets/Food-recognition-1/data.yaml` (not in repo; Roboflow-style) | Photo (jpg/png) | Boxes + class ID 0–29 | `POST /prediction1` `detect_and_visualize` | **Verified** (checkpoint + app) |
| Human labels + photo calories | `class_mapping` dict | `Code/app.py` L42–73 | Hardcoded lookup — **not ML** | n/a | Class ID | Indian dish name + fixed kcal | Same as above | **Verified** |
| Fruit/veg classifier (notebook only) | YOLOv8n-cls | Colab `runs/classify/train/weights/best.pt` (missing) | Trained ML — classification | Kaggle fruit-and-vegetable, 36 classes | 224px image | Class probs | **Not used by app** | **Deprecated / unused** |
| Meal-name recommendation | `DecisionTreeClassifier` | `Code/model1` | Trained ML — sklearn tree | `dietdataset1.csv` train / `dietdataset.csv` serve (5047 rows, 227 meals) | 8 categorical features | `meal_name` string | `POST /recommendation` | **Verified** model; **partial** CSV match |
| Manual log nutrition | Nutritionix Track API v2 | HTTP in `add_successful` | External API — **not ML** | Nutritionix DB | `{portion} {unit} {name}` | kcal, protein, carb, fat | `POST /add_successful` | **Verified** usage; quality **unknown** |
| Unused Nutritionix SDK | `nutritionix.Nutritionix` | import only | Client library | n/a | n/a | n/a | nowhere | **Unused** |
| Daily calorie goal | Mifflin–St Jeor + activity × 500-kcal deficit | `profilesetup` | Formula — **not ML** | n/a | age, sex, height, weight, activity | TDEE, macros | `/setup`, `/track`, `/recommendation` display | **Verified** |
| Body fat % | Deurenberg-style BMI formula | `profilesetup` | Formula — **not ML** | n/a | BMI, age, sex | integer % | user row | **Verified** |
| Diary aggregates | sums / averages | `daily_detail`, `weekly_detail` | Arithmetic — **not ML** | SQLite `tracking` | logged days | consumed vs goal | progress UI | **Verified** |
| Chefboost | imported, never fit | notebook | Unused library | n/a | n/a | n/a | nowhere | **Unused** |
| LLM / embeddings | none | — | — | — | — | — | — | **None found** |

## Status legend

- **Verified** — confirmed from source, checkpoint bytes, or notebook outputs
- **Partially verified** — some artifacts conflict or are missing
- **Unknown** — cannot be confirmed from this repo
- **Not actually an ML model** — lookup, API, or formula
- **Deprecated / unused** — trained or imported but not on the live path

## Conflicts worth remembering

1. Filename `best.pt` + notebook `train_Using_YOLOV8.ipynb` look related. They are **not**. Production `best.pt` is YOLOv8s **detect**, 30 classes, 22 MB. Notebook trained YOLOv8n-**cls**, 36 classes, 3.1 MB.
2. Decision tree is real ML, but snack/dinner vectors in `app.py` do not match the trained feature layout.
3. Photo calories ≠ Nutritionix calories ≠ TDEE goal. Three independent systems.
