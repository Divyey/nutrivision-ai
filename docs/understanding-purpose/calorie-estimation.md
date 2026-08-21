# Calorie Estimation

**This is not a trained ML model.** Calories in the current app come from deterministic lookups, an external API, and formulas.

There are **three separate calorie pipelines**. They do not share a model.

---

## Pipeline A — Photo recognition (count × hardcoded kcal)

```
image
  → YOLO detection (best.pt)
  → class ID 0–29
  → app.py class_mapping[id].label + .calories
  → count detections with conf > 0.4
  → item total = count × fixed kcal
  → UI list + "total"
```

**Nutrition source:** hardcoded integers in `class_mapping` (`app.py` L42–73). Not USDA, not Nutritionix, not per-gram.

**Serving / quantity:** one “item” = one bounding box. No grams, no plate fraction, no box-area scaling.

**What the UI shows:** `items_with_calories` (`app.py` L127–131):

```text
{count} * {kcal}.00 = {count * kcal}
```

This matches observed runtime behavior (e.g. 9 × gulab-jamun × 145 = 1305).

**Bug in the returned `total_calories` field** (`app.py` L114–117):

1. Adds `calories` (the mapping integer) once.
2. Then calls `calculate_total_calories(class_label, count)` where `class_label` is a **string** (`'gulab-jamun'`).
3. `class_mapping.get('gulab-jamun')` misses (keys are ints) → 0.

So the function’s `total_calories` happens to equal count × kcal **only because the second add is zero**. The template total should be treated as unreliable; the per-item strings are the coherent calculation.

**Not ML:** mapping and multiply.

---

## Pipeline B — Manual food log (Nutritionix Track API)

Used when the user types a food on `/add_food` → `POST /add_successful` (`app.py` L589–644).

```
item_name + portion + portion_type (form)
  → POST https://trackapi.nutritionix.com/v2/natural/nutrients
  → foods[0].nf_calories / nf_protein / nf_total_carbohydrate / nf_total_fat
  → stored on SQLite `tracking` row
```

Query string: `"{foodPortion} {portion_type} {item_name}"`.

**Formula in code:**

```python
quantity = foodPortion
finalCalorie = (calories * foodPortion) / quantity  # == calories
```

This is an identity. Nutritionix already returned nutrients for the queried amount. The extra multiply/divide does nothing.

`from nutritionix import Nutritionix` is imported (`app.py` L9) and **never called**. The live path is raw `requests.post`.

App ID / app key are **hardcoded** in `app.py` L603–604 (secret in source). Do not copy them into new code; rotate if this repo is shared.

Coverage: whatever Nutritionix’s US-centric natural-language parser knows. Indian dish names may or may not resolve well — **not verified in this investigation**.

---

## Pipeline C — Daily calorie *goal* (BMR formula)

Set at profile setup (`app.py` `profilesetup`, L931–999). **Not food calories.**

1. BMI = `weight_lb / height_in² * 703`
2. BMR (Mifflin–St Jeor, imperial coefficients):
   - male: `(4.536 * lb) + (15.88 * inches) - (5 * age) + 5`
   - female: same with `- 161`
3. TDEE = BMR × activity factor (1.2 … 1.9)
4. Macros use **`calorie - 500`** (implicit 500 kcal deficit):
   - protein 30% / 4
   - carb 40% / 4
   - fat 30% / 9
   - fiber `calorie/1000 * 14`
5. Meal calorie splits: breakfast 30%, snack 10%, lunch 35%, dinner 25% of `(calorie-500)` at setup; the recommendation page later splits the **full** `u_calories` the same way (L1237–1240) — **inconsistent** with setup.

Body-fat estimate: Deurenberg-style `1.20*BMI + 0.23*age - {16.2|5.4}`.

**Not ML.**

---

## What is *not* happening

- No regression model from pixels → kcal
- No volume / depth / reference-object portion model
- No per-100g nutrition table in the database
- Photo calories are **not** written into `tracking` by `upload_file` (recognition page is separate from the diary)

---

## End-to-end (photo path, as implemented)

```
Food detected (YOLO boxes + class IDs)
  → class_mapping (Python dict)
  → nutrition lookup = dict integer
  → serving = 1 per box
  → calorie = count × integer
  → result rendered on index1.html
```

Manual diary path skips YOLO entirely and uses Nutritionix + SQLite.
