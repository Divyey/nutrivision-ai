# Diet Recommendation

**Purpose:** Given ingredient / meal-type / vegan / allergy / time-of-day features, predict a **meal name** from a closed list.

This **is** a trained ML model: `sklearn.tree.DecisionTreeClassifier`.

Do not confuse it with food-image recognition. It never sees a photo.

---

## Model type

`sklearn.tree.DecisionTreeClassifier` (`criterion="gini"`, other hyperparameters left as sklearn defaults: unlimited depth, `splitter="best"`, no `max_depth` / `class_weight`).

**Chefboost** is imported in the notebook (`decisiontreemodel.ipynb`) and **never used**. The trained object is sklearn.

Pickle strings in `model1` confirm: `sklearn.tree._classes.DecisionTreeClassifier`, `criterion`, `n_features_in_`, `n_classes_`, `monotonic_cst` (sklearn ≥ 1.4).

---

## Model file

`/Users/divyey007/Downloads/Food Recogntion 2024 (1)/Code/model1`  
Size 2,380,258 bytes. Dated 9 Nov 2024.

Loaded at request time:

```1054:1054:/Users/divyey007/Downloads/Food Recogntion 2024 (1)/Code/app.py
			model = pickle.load(open('model1','rb'))
```

The `pickle.load` sits **inside** `for i in dataset_encoded:` so it reloads once per column (9 times per request).

---

## Dataset

| File | Used by | Rows | Columns |
|---|---|---|---|
| `dietdataset.csv` | **Runtime** `app.py` L1046 | 5047 | 9 |
| `dietdataset1.csv` | **Training** notebook `pd.read_csv('dietdataset1.csv')` | 5047 | 9 |

Same schema: `meal_name,carb,meat,vege,fruit,type,vegan,allergy,time`.

Files are **not identical** (340 differing lines). Example: runtime CSV has `Chicken Spaghetti,...pasta...`; training CSV has `Chicken Rice,...pasta...` on the same ingredient row. Encoding at inference is refit on `dietdataset.csv`, while the tree was fit on encoded `dietdataset1.csv`. **Partially verified mismatch risk.**

The table is a **cartesian-style expansion**: each dish template is repeated across vegan yes/no and allergy values (`None`, egg, lactose, seafood, bean/nuts, gluten). That inflates row count without adding new meals.

### Dataset size (runtime CSV)

- 5047 rows
- **227 unique `meal_name` values** (matches pickle `n_classes_ = 227` = `0xe3`)
- Time: Lunch 1819, Dinner 1720, Breakfast 811, Snack 697
- Vegan: no 3907 / yes 1140
- Cuisine character: toast, burrito, taco, smoothie, spaghetti-like pasta, stir-fry, oatmeal — **not** the Indian dishes in YOLO `class_mapping`

---

## Features (X) and target (y)

Notebook:

```python
X = dataset_encoded.iloc[:,1:10]  # columns carb..time (8 cols)
y = dataset_encoded.iloc[:,0]     # meal_name encoded
```

Pickle: `n_features_in_ = 8`, `n_outputs_ = 1`, `n_classes_ = 227`.

| # | Feature | Example values |
|---|---|---|
| 1 | carb | bread, rice, oats, None, … (12) |
| 2 | meat | chicken, beef, None, … (9) |
| 3 | vege | spinach, tomato, None, … (15) |
| 4 | fruit | apple, avocado, None, … (9) |
| 5 | type | toast, soup, stir-fried, … (11) |
| 6 | vegan | yes / no |
| 7 | allergy | None, egg, lactose, … (6) |
| 8 | time | Breakfast / Lunch / Snack / Dinner |

**Target:** `meal_name` (227 labels), e.g. `Avocado Toast`, `Chicken Burrito`, `Oatmeal with Banana`.

The tree is a **meal-name classifier from ingredients**, not a calorie optimizer and not a sequential meal-plan generator.

---

## Preprocessing

Each column is independently `LabelEncoder().fit_transform`’d (`app.py` L1049–1052, notebook same). One `le` object is reused, so only the last column’s encoder remains in `le`. Inference does **not** use that object; it re-encodes by scanning the dataframe (`input_encode`).

**Leakage:** encoders and the tree see labels derived from the **full** table, then `train_test_split(test_size=0.3)` is applied. Split is not stratified. No `random_state`.

Missing ingredient `"None"` must exist in that column or `input_encode` falls back to `0`.

---

## Training process

`decisiontreemodel.ipynb`:

```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
model = DecisionTreeClassifier(criterion="gini")
model.fit(X_train.values, y_train)
pickle.dump(model, open('model1', 'wb'))
```

Checkpoint `decisiontreemodel-checkpoint.ipynb` is an older autosave that reads `dietdataset.csv` instead of `dietdataset1.csv`. Same algorithm.

Tree `node_count` in `model1` ≈ **1265** (`0x04f1`).

---

## Hyperparameters

Only `criterion="gini"` is set. Defaults imply a fully grown tree (easy to memorize duplicated rows).

---

## Evaluation metrics (notebook outputs)

| Metric | Value | Notes |
|---|---|---|
| Accuracy | 0.831 | `accuracy_score` on 1515 test rows |
| Weighted F1 | 0.832 | classification_report weighted avg |
| Macro P/R/F1 | ~0.83 | many classes have support 1–4 |
| Average precision (macro) | **0.006** | misused API on multiclass IDs; **not a useful number** |

Several classes have precision/recall **0** with tiny support. Accuracy is inflated by:

- duplicated meal rows (allergy/vegan copies)
- label encoding fitted before split
- unlimited-depth tree

There is **no** cross-validation, no holdout by unique `meal_name`, no comparison to a majority-class or “exact ingredient lookup” baseline. A non-ML lookup of (carb, meat, vege, fruit, type, time) → meal_name would likely be strong because the table is essentially a recipe catalog.

---

## Inference process (application)

Route: `POST /recommendation` (`app.py` L1040). Form: `recommendsetup.html`.

User inputs:

- Dish **type** per meal (breakfast/lunch/snack/dinner `<select>`)
- Checkboxes: vege, meat, carb, fruit
- Session: `u_info` vegan flag and allergy

Then for breakfast/lunch the app `random.choice`s one checkbox value per group (so recommendations change on refresh). Encodes each field via table lookup. Predicts four times (breakfast, lunch, snack, dinner).

**Snack and dinner feature vectors are wrong** (`app.py` L1214–1219):

```python
snack_input = [snack_encode, snack_encode, snack_encode, snack_encode, snack_encode, vegan_encode, allergy_encode, snack_time_encode]
dinner_input = [dinner_encode, ...]  # type ID copied into carb/meat/vege/fruit/type
```

Those meals ignore the user’s ingredient checkboxes and stuff the **type** encoding into five feature slots.

Decode: `input_decode` maps the predicted class integer back to `meal_name`.

Displayed macros (bf_cal, protein, …) are **percentage splits of the user’s TDEE**, not nutrition of the predicted meal.

---

## Example prediction

Notebook attempted `model.predict([datainput])` and hit `Warning: 'None' not found in dataset column 1` when a carb of `'None'` was passed. No successful printed example meal name is stored in the executed cells.

Qualitatively, a breakfast vector like `(bread, None, None, avocado, toast, yes, None, Breakfast)` corresponds to rows labeled `Avocado Toast` in the CSV.

---

## What recommendations it actually produces

A **single meal title string** per slot (breakfast/lunch/snack/dinner), chosen from the 227 Western/generic names in the CSV. It does not:

- respect calorie budget of that meal
- output recipes, grams, or alternatives
- prefer Indian dishes (those exist only on the YOLO side)
- guarantee the predicted meal uses the selected ingredients (tree can split on other features; snack/dinner vectors are corrupted)

---

## Where the application calls it

Only `/recommendation` POST. `/recommend_setup` GET only renders the form.

---

## Known limitations

- Closed 227-name catalog, mostly non-Indian
- Synthetic repeated rows
- Train/runtime CSV mismatch
- LabelEncoder + unlimited tree + non-stratified split → optimistic 83%
- Random ingredient pick hides multi-select intent
- Snack/dinner inference bug
- Allergy is a single session value, not a list
- No personalization beyond vegan + one allergy + today’s checkboxes
- Cannot “expand to regional cuisine” without a new labeled table and a new model (or replacing this with retrieval)

---

## Suitability for the current product

**Weak fit** for NutriVision if the product story is Indian food photos + calorie tracking:

- Image model: 30 Indian dishes
- Recommender: avocado toast / burrito / oatmeal world
- Photo path never feeds the tree
- Macros shown next to recommendations are unrelated to the predicted meal

It can still demo “pick ingredients → get a meal name.” It is **not** a regional, calorie-aware, or multi-objective recommender.

---

## Data / modeling concerns (evidence-based)

| Issue | Evidence |
|---|---|
| Class imbalance | Lunch/dinner dominate; many meal names have few distinct templates |
| Duplication | Same meal_name × vegan × allergy |
| Leakage | Encode-all-then-split |
| Overfitting risk | Full-depth tree, 1265 nodes, duplicated X |
| No proper baseline | 83% not compared to dictionary lookup |
| Feature bugs at serve | snack/dinner vectors |
| CSV drift | dietdataset vs dietdataset1 |
