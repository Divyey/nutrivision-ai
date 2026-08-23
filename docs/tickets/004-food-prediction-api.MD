# 004 — Food Prediction API

**Status:** Implemented (detections only).

`POST /api/v1/food/predict` returns `image_width`, `image_height`, and `items[]` with `class_id`, `label`, `confidence`, and `box`. An empty plate is **200** with those fields and `items: []`.

This endpoint does **not** return kcal, macros, or portion estimates. Analyzing % on Scan is request UI, not model confidence.

Nutrition lookup, meal logging, and diary snapshots are **005**.
