# Other models / ML-adjacent components

Search of the legacy project (`Code/`, notebooks, pickles, templates) besides food recognition and the decision tree.

---

## 1. `train_Using_YOLOV8.ipynb` — unused classification experiment

| | |
|---|---|
| Type | Trained ML (classification) |
| Architecture | YOLOv8n-cls (`yolov8n-cls.pt`) |
| Dataset | Kaggle `kritikseth/fruit-and-vegetable-image-recognition` (3115 train / 351 val / 359 test, **36** fruit/veg classes) |
| Train | 20 epochs, imgsz 224, Ultralytics 8.2.30, Colab T4 |
| Metrics | top1 0.966, top5 0.997 on that val set (`ClassifyMetrics`) |
| Artifact | Colab `runs/classify/train/weights/best.pt` (3.1 MB) — **not present** in this repo |
| Used by app? | **No.** App loads the 22 MB detection `best.pt` |

**Status:** Deprecated / unused relative to the running product. Do not treat as the production food model.

---

## 2. Nutritionix Track API

**Not an ML model.** External US-centric nutrition NLP. Legacy typed add-food called `POST https://trackapi.nutritionix.com/v2/natural/nutrients`. The PyPI `nutritionix` client was imported and unused.

**005 does not call Nutritionix.** Production values for the 30 detect classes come from INDB in `backend/data/dish_nutrition.csv` (27 rows). ghevar, jalebi, and bhature stay empty until a cited fill exists. Live Nutritionix lookup is out of scope. Registry: `backend/data/DISH_NUTRITION.md`.

---

## 3. BMI / BMR / TDEE / macro formulas

**Not ML.** Mifflin–St Jeor + activity multipliers + 500 kcal deficit. See `calorie-estimation.md` pipeline C.

---

## 4. Password hashing

`pwd_encode` uses **MD5** (`app.py` L509+). Not ML. Weak by modern auth standards.

---

## 5. SQLite tracking / progress

`tracking`, `progress`, `progress_week` store diary and weight. Averages and deficits are arithmetic (`daily_detail`, `weekly_detail`). **Not ML.**

---

## 6. Chefboost

Imported in `decisiontreemodel.ipynb` only. No `chef.fit` / `chef.predict`. **Unused import.**

---

## 7. Embeddings / NLP / LLM

**None found.** No transformers, OpenAI, sentence-transformers, or vector store.

---

## 8. Other checkpoints

| File | Role |
|---|---|
| `Code/model1` | Decision tree (production recommender) |
| `Code/best.pt` | YOLO detection (production recognizer) |
| `.ipynb_checkpoints/decisiontreemodel-checkpoint.ipynb` | Jupyter autosave of the tree notebook |

No `.onnx`, `.h5`, `.joblib`, or extra `.pt` files in `Code/`.

---

## 9. Rule-based systems sometimes described as “AI”

Marketing copy on `index1.html` says the system “predicts food items and calculates calorie content.” Calorie content for photos is a **lookup table**, not a learned estimator.

Random `random.choice` on checkbox lists is not a recommender policy; it is noise in front of the tree.
