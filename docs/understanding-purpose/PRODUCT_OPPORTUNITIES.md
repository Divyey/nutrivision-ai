# Product opportunities (research options)

Not a decision. Each row is something you can independently compare. Technical notes refer to the **current** legacy system.

Competitors cited where public: HealthifyMe Snap / Ria, MyFitnessPal, Lose It, Cal AI, Foodvisor, SnapCalorie, Cronometer, Samsung Food.

---

## O1 — Confirm-and-save Indian plate scanner

- **Problem:** 1, 2, 5  
- **Solution:** Photo → YOLO boxes → user confirms/edits → write diary (Postgres) with macros.  
- **Target user:** Students / home cooks eating a small set of repeated Indian dishes.  
- **Value:** Cuts logging time for a closed personal menu.  
- **Alternatives:** HealthifyMe Snap, Cal AI.  
- **Differentiation:** Tiny dish list done *well*, local foods, honest uncertainty, cheap self-host.  
- **Feasibility:** High if you keep 30 classes and add a confirm UI. FastAPI + React is enough.  
- **Data/ML:** Current `best.pt` + `class_mapping`; need a real nutrition table (not count×kcal).  
- **Risks:** 30 classes is too small for a public app; mapping IDs to names still unverified vs original `data.yaml`.  
- **Validate:** 20 people, 5 meals/day, measure time-to-log and correction rate.

## O2 — Portion-aware calories (scale, utensils, or user slider)

- **Problem:** 3  
- **Solution:** Keep detection; add small/medium/large or grams; optional reference object.  
- **Target user:** Anyone who already knows the dish name.  
- **Value:** This is where photo-kcal products actually fail.  
- **Alternatives:** SnapCalorie (portion research), food scale + Cronometer.  
- **Differentiation:** Indian serving heuristics (katori, roti count, “1 ladle dal”) instead of US cups.  
- **Feasibility:** Medium. No portion model exists today.  
- **Data/ML:** Need labeled portions or a rules table; optional depth/segmentation later.  
- **Risks:** Users hate extra taps; bad defaults recreate the current integer table.  
- **Validate:** Compare slider vs weigh-ins for 10 dishes.

## O3 — Regional nutrition database (IFCT / INDB + user recipes)

- **Problem:** 2, 6  
- **Solution:** Drop Nutritionix as the only source; map dishes to Indian food composition + homemade recipes.  
- **Target user:** Indian / diaspora home cooks.  
- **Value:** Names and oil/ghee assumptions match the kitchen.  
- **Alternatives:** Nutritionix, USDA, HealthifyMe DB.  
- **Differentiation:** Recipe-level (your dal vs restaurant dal).  
- **Feasibility:** High as engineering; legal/licensing of tables must be checked.  
- **Data/ML:** Mostly data modeling, not ML.  
- **Risks:** Licensing; endless recipe variants.  
- **Validate:** Dietitian review of 30 core dishes vs current integers.

## O4 — Retrieval recommender instead of the decision tree

- **Problem:** 7, 8  
- **Solution:** Filter the meal catalog with **hard** vegan/allergy/time/kcal constraints; rank by ingredients on hand. Delete or freeze `model1`.  
- **Target user:** Same as current `/recommendation`.  
- **Value:** Correctness over fake 83% accuracy.  
- **Alternatives:** Cookbook apps, ChatGPT meal plans, HealthifyMe Ria.  
- **Differentiation:** Constraints first; optional Indian catalog aligned with YOLO classes.  
- **Feasibility:** High. The CSV is already a recipe table.  
- **Data/ML:** SQL/filters; ML optional later (learn-to-rank).  
- **Risks:** Catalog is Western; swapping cuisine is a content project.  
- **Validate:** Allergy-safe rate 100% on a test matrix; user preference vs tree.

## O5 — Personal closed-set model (“my 15 meals”)

- **Problem:** 2, 13, 14  
- **Solution:** Few-shot / fine-tune on the user’s repeated tiffin photos.  
- **Target user:** Repeat eaters, not tourists of cuisine.  
- **Value:** Accuracy on *their* kadhai beats a 150k-class generic model.  
- **Alternatives:** Generic Snap/Cal AI.  
- **Differentiation:** Personalization as the product.  
- **Feasibility:** Medium. Needs upload+label UX and storage.  
- **Data/ML:** Fine-tune YOLO or a lightweight classifier; start with 15 classes.  
- **Risks:** Cold start; overfitting to one lighting setup.  
- **Validate:** Within-user accuracy after 10 labeled images/class.

## O6 — Correction loop / weak supervision

- **Problem:** 13  
- **Solution:** Every wrong box becomes a labeled sample; periodic retrain.  
- **Target user:** Power users + you as operator.  
- **Value:** Only path to improve a 30-class detector after launch.  
- **Alternatives:** HealthifyMe human review.  
- **Differentiation:** Transparent “help train the model” for a learning-portfolio product.  
- **Feasibility:** Medium. Product + MLOps, not just a notebook.  
- **Data/ML:** Store crops, labels, versioned `best.pt`.  
- **Risks:** Garbage labels; privacy of stored plates.  
- **Validate:** mAP before/after one correction cycle.

## O7 — Voice / WhatsApp logging for Indian food names

- **Problem:** 1, 12  
- **Solution:** “do tin roti, ek katori dal” → parser → diary. Photo optional.  
- **Target user:** Users who will not tap through forms.  
- **Value:** Matches how people already describe meals.  
- **Alternatives:** HealthifyMe WhatsApp/Snap adjacent features, generic LLM chat.  
- **Differentiation:** Hindi/English serving language + local units.  
- **Feasibility:** Medium (LLM API cost vs rules).  
- **Data/ML:** NLP/LLM or grammar; nutrition DB still required.  
- **Risks:** Cost, hallucination, allergy mistakes.  
- **Validate:** 50 spoken logs vs weighed truth.

## O8 — Honest “assistant for learning nutrition,” not a medical tracker

- **Problem:** 6, 15, 9  
- **Solution:** Always show range + source; teach oil/portion; never claim lab accuracy.  
- **Target user:** Learners, including you documenting the rebuild.  
- **Value:** Trust; fits a portfolio/teaching product.  
- **Alternatives:** Cronometer (source-heavy), TikTok misinformation.  
- **Differentiation:** Explainability of YOLO + tables.  
- **Feasibility:** High (UX + copy).  
- **Data/ML:** None new.  
- **Risks:** Less viral than “snap = exact kcal.”  
- **Validate:** User trust survey vs Cal AI-style claims.

## O9 — On-device / cheap-cloud inference

- **Problem:** 11, 14  
- **Solution:** Export YOLOv8s to ONNX/TFLite; load once; no per-request `YOLO()`.  
- **Target user:** Self-hosters; mobile later.  
- **Value:** Latency, cost, privacy.  
- **Alternatives:** Server VLM APIs.  
- **Differentiation:** Low-cost architecture as a feature.  
- **Feasibility:** High for CPU YOLO-s; hard for large VLMs.  
- **Data/ML:** Export + benchmark; no new training required.  
- **Risks:** Accuracy drop on export; Apple/Android split.  
- **Validate:** p95 latency and energy vs current Flask path.

## O10 — Multi-item thali editor

- **Problem:** 4  
- **Solution:** Show all boxes; user merges/splits/names leftovers; calories sum with portions.  
- **Target user:** Thali / mess food.  
- **Value:** Matches real plates better than one-class photos.  
- **Alternatives:** Snap multi-item tap.  
- **Differentiation:** Thali-first UX.  
- **Feasibility:** Medium (frontend heavy).  
- **Data/ML:** Current detector + interaction; later segmentation.  
- **Risks:** UX complexity.  
- **Validate:** Time-to-correct vs single-shot Cal AI on thali photos.

## O11 — Goal engine that is not a hidden 500 kcal cut

- **Problem:** 9, 10, 15  
- **Solution:** Explicit lose/maintain/gain; protein floor; don’t hide unloaded days.  
- **Target user:** Beginners.  
- **Value:** Safer than silent deficit.  
- **Alternatives:** MacroFactor, clinical RDN.  
- **Differentiation:** Transparent math (you already have the formulas).  
- **Feasibility:** High. **Not ML.**  
- **Data/ML:** None.  
- **Risks:** Still not medical advice.  
- **Validate:** Dietitian sanity-check of defaults.

---

## How to use this list

Shortlist 2–3 opportunities, then for each write: user, constraint (cost/privacy/cuisine), and a one-week validation. The rebuild (React + FastAPI + Postgres) should follow that shortlist, not the other way around.
