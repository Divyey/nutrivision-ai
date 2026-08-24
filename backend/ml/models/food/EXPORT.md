# Food ONNX export

This file is produced by `scripts/export_food_onnx.py` (dev venv with Ultralytics).
The FastAPI app loads `best.onnx` with ONNX Runtime CPU only.

| Field | Value |
|---|---|
| Ultralytics | 8.3.73 |
| imgsz | 800 |
| NMS in graph | True |
| conf keep | > 0.4 (legacy second threshold) |
| ONNX size | 44894648 bytes (~42.8 MB) |
| Export wall time | 83.59 s |

## Session

Inputs: `[{'name': 'images', 'shape': [1, 3, 800, 800], 'type': 'tensor(float)'}]`

Outputs: `[{'name': 'output0', 'shape': [1, 300, 6], 'type': 'tensor(float)'}]`

Padded NMS rows use `confidence <= 0` as empty. Filter with `confidence > 0.4`.

NMS `class` ids are the **training ids** (same as Flask / `YOLO.predict()`). Ultralytics metadata `names` sorts `'0'`…`'29'` as strings (`{7: '15', 27: '7', …}`) — that is file metadata only. Remapping NMS ids through it mislabels idli (7) as onion-pakoda (15). The API uses training ids → Flask slugs.

## Preprocess

Pillow letterbox matches Ultralytics `LetterBox(new_shape=800, auto=False, center=True)` geometry: scale ratio, stride-independent pad because 800 % 32 == 0, pad value 114, RGB/255/CHW. Boxes are remapped from letterbox space to original pixels.

Resample is Pillow `BILINEAR` vs Ultralytics `cv2.INTER_LINEAR` (not bit-identical pixels).

## Parity / RSS (measured 2026-08-23, Mac CPU, Python 3.13, onnxruntime in the app venv)

- PyTorch vs ONNX class IDs / extra-or-missing boxes: **not measured**. The export venv (Ultralytics 8.3.73 + torch 2.2.2) cannot import torch against NumPy 2.1.1 (`_ARRAY_API not found`). Do not treat PT `predict()` as a passing gate until a NumPy 1.x export venv can run both.
- CPU `session.run` + decode/letterbox (640×480 JPEG, 5 runs after 1 warmup): **0.245–0.310 s**, median **0.264 s**.
- Process RSS (`ru_maxrss`): **14.8 MB** before import; **169.3 MB** after `InferenceSession` load (0.42 s); **300.3 MB** after one predict.

Cloud RAM: size from this RSS, not “2 GB”. **300 MB** after a small image is the measured floor; use **1 worker**. 512 MB may be tight once FastAPI, the DB driver, and larger photos are included; **1 GB** is a safer first instance size until production photos are measured.
