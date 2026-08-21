# Business problems

These are concrete problems implied by the legacy product, its gaps, and the market around photo food logging. They are **candidates**, not a committed product thesis.

Grounding: the running app already tries to (1) detect Indian dishes in photos, (2) log food via Nutritionix, (3) recommend a meal name from a Western ingredient table, (4) set a calorie goal from BMI/BMR. Competitors such as MyFitnessPal, Lose It, HealthifyMe Snap, Cal AI, Foodvisor, and SnapCalorie already occupy parts of this space.

---

### Problem 1 — Manual food logging friction

**Who:** People who try to track calories or macros daily.  
**Why it matters:** Search-and-portion entry is slow; missing meals destroy data quality and people quit.  
**Alternatives:** MyFitnessPal, Lose It, Cronometer, restaurant menus, spreadsheets.  
**Gap:** Even with barcodes, mixed homemade / canteen plates still require guessing. The legacy `/add_food` flow is still typed Nutritionix queries.

### Problem 2 — Weak coverage of Indian / regional plated food

**Who:** Users eating dal, roti, sabzi, rice, sweets, mixed thalis.  
**Why it matters:** Western databases under-specify regional names, oil, and gravy; photo models trained on burgers/salads miss the plate.  
**Alternatives:** HealthifyMe Snap (claims large Indian coverage), manual entry, local dietitians.  
**Gap:** This codebase’s detector is only **30** dishes; the recommender catalog is mostly toast/burrito/oatmeal, not the YOLO classes. HealthifyMe is a full wellness platform, not a student-rebuildable core.

### Problem 3 — Portion and oil are the real calorie error

**Who:** Anyone logging curry, fried snacks, or “one plate.”  
**Why it matters:** Identity of the dish can be right while kcal is off by 2× because of oil, ghee, and serving size.  
**Alternatives:** Food scales, dietitian estimates, SnapCalorie-style portion research, “small/medium/large” pickers.  
**Gap:** Legacy photo path is **count × fixed kcal**. Box area is unused. Marketing says “estimate calorie intake accurately”; the implementation does not estimate mass.

### Problem 4 — Mixed plates and overlapping foods

**Who:** Thali / tiffin / family-style eaters.  
**Why it matters:** Multiple items, sauces, and shared bowls break single-label classifiers.  
**Alternatives:** Tap-to-select regions (HealthifyMe Snap), multi-box detectors, sequential photos.  
**Gap:** YOLO can emit multiple boxes, but calories still assume each box is one standard serving of one class. No user correction UI beyond looking at the annotated JPEG.

### Problem 5 — Photo log is disconnected from the diary

**Who:** Users who both snap a meal and want a history.  
**Why it matters:** Recognition that does not write `tracking` is a demo, not a tracker.  
**Alternatives:** Apps that snap → confirm → save in one flow.  
**Gap:** `POST /prediction1` does not insert into SQLite; `/add_successful` never calls YOLO.

### Problem 6 — Nutrition data provenance and trust

**Who:** People managing weight, diabetes, or training, plus anyone comparing apps.  
**Why it matters:** Wrong kcal erodes trust faster than a slightly slower UX.  
**Alternatives:** USDA FoodData Central, Nutritionix, INDB / IFCT Indian tables, branded restaurant data.  
**Gap:** Photo path uses anonymous integers; manual path uses Nutritionix without showing source, serving basis, or uncertainty.

### Problem 7 — Recommendations that ignore the user’s actual diet and goals

**Who:** Users who filled vegan/allergy/BMI and still get a random meal title.  
**Why it matters:** A “recommendation” that can violate ingredients (snack/dinner bug) or calorie budget is not useful and can be unsafe for allergies.  
**Alternatives:** Dietitian plans, HealthifyMe Ria, generic chatbots, cookbook search.  
**Gap:** Tree predicts a name from a Western table; macros shown are TDEE slices, not the meal’s nutrients. Indian detection classes never enter the tree.

### Problem 8 — Allergen handling is a single flag, not a constraint solver

**Who:** Users with lactose, gluten, nuts, egg, seafood restrictions.  
**Why it matters:** One wrong dish is a health incident, not a UX bug.  
**Alternatives:** Dedicated allergen filters in grocery apps; dietitian review.  
**Gap:** Dataset repeats meals across allergy columns so the tree can still emit a meal that “exists” in another allergy slice. Encoding is not a hard filter.

### Problem 9 — Calorie goals from BMI are crude and sometimes contradictory

**Who:** Beginners who accept whatever the signup form prints.  
**Why it matters:** A blanket 500 kcal deficit, imperial BMR, and two different meal-split formulas can underfuel or confuse.  
**Alternatives:** MacroFactor, RP Diet, clinical RDN targets, Mifflin with lean mass.  
**Gap:** Setup uses `(TDEE-500)` for meal splits; recommendation page splits full TDEE. No goal type (lose/maintain/gain) beyond implicit cut.

### Problem 10 — Adherence and incomplete days

**Who:** Anyone whose weekly average is computed from logged days only.  
**Why it matters:** Skipping logs looks like a deficit; the UI can reward missing data.  
**Alternatives:** Reminders, wearable intake proxies, photo-from-lock-screen (HealthifyMe).  
**Gap:** Weekly logic averages days with `track_calorie != 0`; empty days disappear.

### Problem 11 — Privacy and secret handling in a food-photo product

**Who:** Users photographing kitchen/home; developers deploying APIs.  
**Why it matters:** Meal photos are sensitive; Nutritionix keys in source can be stolen and billed.  
**Alternatives:** On-device models, user-owned DB, proper secret managers.  
**Gap:** Keys hardcoded; MD5 passwords; model path local to one laptop.

### Problem 12 — “Scan packaged food” vs “scan a home-cooked plate”

**Who:** Urban shoppers vs home cooks.  
**Why it matters:** Barcodes and packaged-food models are a different (easier) problem than homemade Indian food.  
**Alternatives:** MyFitnessPal barcode, HealthifyMe packaged-food claims.  
**Gap:** This project has neither barcode nor packaged-goods training; only plated-dish detection + typed search.

### Problem 13 — Feedback loop missing for wrong detections

**Who:** Users who see a wrong box and have no way to fix the model.  
**Why it matters:** Without corrections, a 30-class detector cannot improve after launch.  
**Alternatives:** HealthifyMe human-in-the-loop review; user “this is actually X”.  
**Gap:** No correction table, no active learning, no stored images of failures.

### Problem 14 — Cost of accurate photo-ML vs a student/low-cost deploy

**Who:** The team targeting FastAPI + cheap cloud.  
**Why it matters:** GPU inference, Nutritionix quotas, and data labeling dominate cost; a 22 MB YOLO on CPU may be OK, a VLM may not.  
**Alternatives:** On-device TFLite, batched jobs, API-only nutrition.  
**Gap:** Model is reloaded every request; no quantization/export story in repo.

### Problem 15 — Identity vs habit: tracking without coaching

**Who:** Users who log but do not change meals.  
**Why it matters:** Logs without a closed loop (plan → eat → compare → next meal) tend to be abandoned.  
**Alternatives:** Noom-style coaching, human dietitians, simple if-then rules.  
**Gap:** Progress pages show weight and kcal averages; they do not close the loop with the photo model or the tree.
