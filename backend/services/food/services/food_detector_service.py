from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import numpy as np
from PIL import Image, UnidentifiedImageError

from core.config import settings
from services.food.services.food_classes_service import (
    class_id_for_onnx_index,
    label_for_class_id,
)

logger = logging.getLogger("nutrivision")

ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/jpg", "image/png", "image/webp"})
# Ultralytics LetterBox pad (114, 114, 114) before /255.
LETTERBOX_PAD_VALUE = 114.0
NMS_IOU_THRESHOLD = 0.45
XYXY_CONF_CLASS_WIDTHS = (6, 7)


@dataclass(frozen=True)
class FoodDetection:
    class_id: int
    label: str
    confidence: float
    box: tuple[float, float, float, float]


@dataclass(frozen=True)
class FoodPredictResult:
    image_width: int
    image_height: int
    items: list[FoodDetection]


class FoodError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class FoodDetector(Protocol):
    def is_ready(self) -> bool: ...

    def predict(self, image_bytes: bytes) -> FoodPredictResult: ...


@dataclass
class FakeFoodDetector:
    """CI / tests. Still decodes the photo so size and pixel limits apply."""

    image_width: int = 640
    image_height: int = 480
    items: list[FoodDetection] = field(
        default_factory=lambda: [
            FoodDetection(
                class_id=6,
                label="gulab-jamun",
                confidence=0.91,
                box=(80.0, 60.0, 280.0, 260.0),
            )
        ]
    )

    def is_ready(self) -> bool:
        return True

    def predict(self, image_bytes: bytes) -> FoodPredictResult:
        decode_image(image_bytes)
        return FoodPredictResult(self.image_width, self.image_height, list(self.items))


class UnavailableFoodDetector:
    def is_ready(self) -> bool:
        return False

    def predict(self, image_bytes: bytes) -> FoodPredictResult:
        del image_bytes
        raise FoodError(503, "Food analysis is not available")


class OnnxFoodDetector:
    def __init__(self, model_path: Path) -> None:
        import onnxruntime as ort

        self._image_size = settings.food_imgsz
        self._confidence_min = settings.food_confidence_min
        self._session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )
        self._input_name = self._session.get_inputs()[0].name
        self._output_names = [output.name for output in self._session.get_outputs()]
        self._has_in_graph_nms = self._output_is_nms_rows()
        # InferenceSession.run is not thread-safe; Scan uses a threadpool.
        self._session_lock = threading.Lock()

    def is_ready(self) -> bool:
        return True

    def predict(self, image_bytes: bytes) -> FoodPredictResult:
        image, width, height = decode_image(image_bytes)
        tensor, scale, pad_x, pad_y = letterbox_chw(image, self._image_size)
        with self._session_lock:
            outputs = self._session.run(self._output_names, {self._input_name: tensor})
        raw_rows = _parse_yolo_outputs(
            outputs, self._has_in_graph_nms, self._confidence_min
        )
        items = _map_detections(
            raw_rows, scale, pad_x, pad_y, width, height, self._confidence_min
        )
        return FoodPredictResult(width, height, items)

    def _output_is_nms_rows(self) -> bool:
        output = self._session.get_outputs()[0]
        shape = tuple(
            dimension if isinstance(dimension, int) else -1
            for dimension in output.shape
        )
        if len(shape) == 2 and shape[-1] in XYXY_CONF_CLASS_WIDTHS:
            return True
        if len(shape) == 3 and shape[-1] in XYXY_CONF_CLASS_WIDTHS:
            return True
        return False


_runtime_detector: FoodDetector | None = None


def set_food_detector(detector: FoodDetector) -> None:
    global _runtime_detector
    _runtime_detector = detector


def get_food_detector() -> FoodDetector:
    if _runtime_detector is None:
        return UnavailableFoodDetector()
    return _runtime_detector


def food_detector_health() -> dict[str, str]:
    if get_food_detector().is_ready():
        return {"status": "healthy", "model": "loaded"}
    return {"status": "unhealthy", "model": "unavailable"}


def create_food_detector() -> FoodDetector:
    mode = settings.food_detector
    if mode == "fake":
        return FakeFoodDetector()
    if mode == "unavailable":
        return UnavailableFoodDetector()
    model_path = settings.resolved_food_model_path
    if not model_path.is_file():
        logger.warning("Food ONNX model is not present")
        return UnavailableFoodDetector()
    try:
        detector = OnnxFoodDetector(model_path)
        logger.info("Food ONNX model loaded")
        return detector
    except Exception:
        logger.exception("Food ONNX model failed to load")
        return UnavailableFoodDetector()


def decode_image(image_bytes: bytes) -> tuple[np.ndarray, int, int]:
    from io import BytesIO

    try:
        with Image.open(BytesIO(image_bytes)) as verified:
            verified.verify()
        with Image.open(BytesIO(image_bytes)) as loaded:
            rgb = loaded.convert("RGB")
            width, height = rgb.size
            if width * height > settings.food_max_pixels:
                raise FoodError(400, "Image dimensions are too large")
            pixels = np.asarray(rgb, dtype=np.uint8)
    except FoodError:
        raise
    except UnidentifiedImageError as error:
        raise FoodError(400, "Could not read this image") from error
    except OSError as error:
        raise FoodError(400, "Could not read this image") from error
    return pixels, width, height


def letterbox_chw(
    image: np.ndarray,
    image_size: int,
) -> tuple[np.ndarray, float, float, float]:
    """Match Ultralytics LetterBox(new_shape=image_size, auto=False, center=True)."""
    height, width = image.shape[:2]
    scale = min(image_size / height, image_size / width)
    resized_width = int(round(width * scale))
    resized_height = int(round(height * scale))
    if (width, height) != (resized_width, resized_height):
        resized = Image.fromarray(image).resize(
            (resized_width, resized_height), Image.Resampling.BILINEAR
        )
        image = np.asarray(resized, dtype=np.uint8)
    pad_width = image_size - resized_width
    pad_height = image_size - resized_height
    pad_x = pad_width / 2
    pad_y = pad_height / 2
    canvas = np.full((image_size, image_size, 3), LETTERBOX_PAD_VALUE, dtype=np.float32)
    # Ultralytics uses round(pad - 0.1) so even pads split 50/50.
    left = int(round(pad_x - 0.1))
    top = int(round(pad_y - 0.1))
    canvas[top : top + resized_height, left : left + resized_width] = image.astype(
        np.float32
    )
    channels_first = np.transpose(canvas / 255.0, (2, 0, 1))
    batched = np.expand_dims(channels_first, 0).astype(np.float32)
    return batched, scale, float(left), float(top)


def _parse_yolo_outputs(
    outputs: list[np.ndarray],
    has_in_graph_nms: bool,
    confidence_min: float,
) -> list[tuple[int, float, tuple[float, float, float, float]]]:
    data = outputs[0]
    last_axis = data.shape[-1] if data.ndim >= 2 else 0
    nms_rows = has_in_graph_nms or last_axis in XYXY_CONF_CLASS_WIDTHS
    if nms_rows and data.ndim in (2, 3) and last_axis in XYXY_CONF_CLASS_WIDTHS:
        rows = data.reshape(-1, last_axis)
        return _rows_xyxy_conf_class(rows, confidence_min)
    # Raw Ultralytics export: (1, 4 + class_count, anchors) center-xywh + scores.
    if data.ndim == 3 and data.shape[1] >= 5:
        predictions = np.transpose(data[0], (1, 0))
        return _nms_xywh(predictions, confidence_min)
    raise FoodError(503, "Food analysis is not available")


def _rows_xyxy_conf_class(
    rows: np.ndarray,
    confidence_min: float,
) -> list[tuple[int, float, tuple[float, float, float, float]]]:
    parsed: list[tuple[int, float, tuple[float, float, float, float]]] = []
    for row in rows:
        box_x1 = float(row[0])
        box_y1 = float(row[1])
        box_x2 = float(row[2])
        box_y2 = float(row[3])
        if row.shape[0] >= 7:
            confidence = float(row[4]) * float(row[5])
            class_id = int(row[6])
        else:
            confidence = float(row[4])
            class_id = int(row[5])
        if confidence <= 0:
            continue
        if confidence > confidence_min:
            parsed.append((class_id, confidence, (box_x1, box_y1, box_x2, box_y2)))
    return parsed


def _nms_xywh(
    predictions: np.ndarray,
    confidence_min: float,
    iou_threshold: float = NMS_IOU_THRESHOLD,
) -> list[tuple[int, float, tuple[float, float, float, float]]]:
    xywh = predictions[:, :4]
    class_scores = predictions[:, 4:]
    class_ids = np.argmax(class_scores, axis=1)
    confidences = class_scores[np.arange(class_scores.shape[0]), class_ids]
    keep = confidences > confidence_min
    xywh = xywh[keep]
    class_ids = class_ids[keep]
    confidences = confidences[keep]
    if xywh.size == 0:
        return []
    boxes = _xywh_to_xyxy(xywh)
    order = np.argsort(-confidences)
    selected: list[int] = []
    while order.size > 0:
        current = int(order[0])
        selected.append(current)
        if order.size == 1:
            break
        overlaps = _intersection_over_union(boxes[current], boxes[order[1:]])
        order = order[1:][overlaps <= iou_threshold]
    parsed: list[tuple[int, float, tuple[float, float, float, float]]] = []
    for index in selected:
        box_x1, box_y1, box_x2, box_y2 = (float(value) for value in boxes[index])
        parsed.append(
            (
                int(class_ids[index]),
                float(confidences[index]),
                (box_x1, box_y1, box_x2, box_y2),
            )
        )
    return parsed


def _xywh_to_xyxy(xywh: np.ndarray) -> np.ndarray:
    center_x = xywh[:, 0]
    center_y = xywh[:, 1]
    box_width = xywh[:, 2]
    box_height = xywh[:, 3]
    return np.stack(
        (
            center_x - box_width / 2,
            center_y - box_height / 2,
            center_x + box_width / 2,
            center_y + box_height / 2,
        ),
        axis=1,
    )


def _intersection_over_union(box: np.ndarray, others: np.ndarray) -> np.ndarray:
    overlap_left = np.maximum(box[0], others[:, 0])
    overlap_top = np.maximum(box[1], others[:, 1])
    overlap_right = np.minimum(box[2], others[:, 2])
    overlap_bottom = np.minimum(box[3], others[:, 3])
    intersection = np.clip(overlap_right - overlap_left, 0, None) * np.clip(
        overlap_bottom - overlap_top, 0, None
    )
    box_area = max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])
    others_area = np.clip(others[:, 2] - others[:, 0], 0, None) * np.clip(
        others[:, 3] - others[:, 1], 0, None
    )
    union = box_area + others_area - intersection
    return np.divide(
        intersection, union, out=np.zeros_like(intersection), where=union > 0
    )


def _map_detections(
    raw_rows: list[tuple[int, float, tuple[float, float, float, float]]],
    scale: float,
    pad_x: float,
    pad_y: float,
    image_width: int,
    image_height: int,
    confidence_min: float,
) -> list[FoodDetection]:
    items: list[FoodDetection] = []
    for class_id, confidence, (box_x1, box_y1, box_x2, box_y2) in raw_rows:
        training_id = class_id_for_onnx_index(class_id)
        if training_id is None:
            continue
        label = label_for_class_id(training_id)
        if label is None or confidence <= confidence_min:
            continue
        mapped = (
            _map_to_original_pixel(box_x1, scale, pad_x, image_width),
            _map_to_original_pixel(box_y1, scale, pad_y, image_height),
            _map_to_original_pixel(box_x2, scale, pad_x, image_width),
            _map_to_original_pixel(box_y2, scale, pad_y, image_height),
        )
        if mapped[2] <= mapped[0] or mapped[3] <= mapped[1]:
            continue
        items.append(
            FoodDetection(
                class_id=training_id,
                label=label,
                confidence=min(confidence, 1.0),
                box=mapped,
            )
        )
    return items


def _map_to_original_pixel(
    coordinate: float, scale: float, pad: float, limit: int
) -> float:
    value = (coordinate - pad) / scale if scale else coordinate
    return float(min(max(value, 0.0), float(limit)))
