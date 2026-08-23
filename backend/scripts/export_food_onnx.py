"""Dev-only: export models/food/best.pt to best.onnx.

Not imported by the FastAPI app. Requires a separate venv with ultralytics+torch.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PT = ROOT / "models" / "food" / "best.pt"
DEFAULT_ONNX = ROOT / "models" / "food" / "best.onnx"
IMGSZ = 800
CONF_MIN = 0.4


def export_onnx(pt_path: Path, nms: bool) -> Path:
    from ultralytics import YOLO

    model = YOLO(str(pt_path))
    names = model.names
    print(f"ultralytics loaded; classes={len(names)} names={names}")
    print(f"export format=onnx imgsz={IMGSZ} nms={nms}")
    out = model.export(format="onnx", imgsz=IMGSZ, nms=nms, simplify=True, opset=12)
    return Path(str(out))


def inspect_onnx(onnx_path: Path) -> dict:
    import onnxruntime as ort

    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    inputs = [
        {"name": i.name, "shape": i.shape, "type": i.type} for i in session.get_inputs()
    ]
    outputs = [
        {"name": o.name, "shape": o.shape, "type": o.type}
        for o in session.get_outputs()
    ]
    return {"inputs": inputs, "outputs": outputs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pt", type=Path, default=DEFAULT_PT)
    parser.add_argument("--no-nms", action="store_true")
    args = parser.parse_args()
    if not args.pt.is_file():
        print(f"missing weights: {args.pt}", file=sys.stderr)
        return 1

    nms = not args.no_nms
    started = time.perf_counter()
    try:
        onnx_path = export_onnx(args.pt, nms=nms)
    except Exception as exc:
        if nms:
            print(f"export with nms=True failed ({exc!r}); retrying without NMS")
            onnx_path = export_onnx(args.pt, nms=False)
            nms = False
        else:
            raise
    elapsed = time.perf_counter() - started
    if onnx_path.resolve() != DEFAULT_ONNX.resolve() and onnx_path.is_file():
        DEFAULT_ONNX.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_ONNX.write_bytes(onnx_path.read_bytes())
        onnx_path = DEFAULT_ONNX

    meta = {
        "ultralytics": _ultralytics_version(),
        "imgsz": IMGSZ,
        "nms_in_graph": nms,
        "conf_min": CONF_MIN,
        "pt": str(args.pt),
        "onnx": str(onnx_path),
        "onnx_bytes": onnx_path.stat().st_size if onnx_path.is_file() else None,
        "export_seconds": round(elapsed, 2),
        "session": inspect_onnx(onnx_path),
    }
    notes = ROOT / "models" / "food" / "EXPORT.md"
    notes.write_text(_render_notes(meta), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(f"wrote {notes}")
    return 0


def _ultralytics_version() -> str:
    import ultralytics

    return getattr(ultralytics, "__version__", "unknown")


def _render_notes(meta: dict) -> str:
    session = meta["session"]
    return f"""# Food ONNX export

This file is produced by `scripts/export_food_onnx.py` (dev venv with Ultralytics).
The FastAPI app loads `{Path(meta["onnx"]).name}` with ONNX Runtime CPU only.

| Field | Value |
|---|---|
| Ultralytics | {meta["ultralytics"]} |
| imgsz | {meta["imgsz"]} |
| NMS in graph | {meta["nms_in_graph"]} |
| conf keep | > {meta["conf_min"]} (legacy second threshold) |
| ONNX size | {meta["onnx_bytes"]} bytes |
| Export wall time | {meta["export_seconds"]} s |

## Session

Inputs: `{session["inputs"]}`

Outputs: `{session["outputs"]}`

## Parity / RSS

Fill in after a local smoke (`FOOD_ONNX_SMOKE=1 pytest` or Scan a meal photo):

- PyTorch vs ONNX class IDs / extra-or-missing boxes:
- CPU `session.run` latency:
- Process RSS after load:
"""


if __name__ == "__main__":
    raise SystemExit(main())
