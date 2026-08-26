from io import BytesIO
import os

import numpy as np
import pytest
from PIL import Image

from core.config import settings
from helpers import API_V1, auth_headers
from services.food.services.food_classes_service import (
    class_id_for_onnx_index,
    foods_log_line_from_class_ids,
    foods_log_line_from_items,
    label_for_class_id,
)
from services.food.services.food_detector_service import (
    FakeFoodDetector,
    UnavailableFoodDetector,
    _map_to_original_pixel,
    letterbox_chw,
    set_food_detector,
)


def _jpeg(width: int = 32, height: int = 24) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (width, height), (200, 40, 40)).save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture(autouse=True)
def reset_fake_detector():
    set_food_detector(FakeFoodDetector())
    yield
    set_food_detector(FakeFoodDetector())


def test_predict_requires_auth(client):
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", _jpeg(), "image/jpeg")},
    )
    assert response.status_code == 401


def test_predict_rejects_unsupported_type(client):
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("notes.txt", b"hello", "text/plain")},
        headers=auth_headers(client),
    )
    assert response.status_code == 415


def test_predict_rejects_undecodable_image(client):
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", b"not-an-image", "image/jpeg")},
        headers=auth_headers(client),
    )
    assert response.status_code == 400


def test_predict_rejects_oversize(client, monkeypatch):
    monkeypatch.setattr(settings, "food_max_image_bytes", 20)
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", _jpeg(), "image/jpeg")},
        headers=auth_headers(client),
    )
    assert response.status_code == 413


def test_predict_returns_items(client):
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", _jpeg(), "image/jpeg")},
        headers=auth_headers(client),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["image_width"] == 640
    assert body["image_height"] == 480
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["class_id"] == 6
    assert item["label"] == "gulab-jamun"
    assert item["confidence"] == 0.91
    assert item["box"] == {"x1": 80.0, "y1": 60.0, "x2": 280.0, "y2": 260.0}
    assert "kcal" not in item
    assert "total_kcal" not in body


def test_predict_empty_items(client):
    set_food_detector(FakeFoodDetector(items=[]))
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", _jpeg(), "image/jpeg")},
        headers=auth_headers(client),
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_predict_unavailable_returns_503(client):
    set_food_detector(UnavailableFoodDetector())
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", _jpeg(), "image/jpeg")},
        headers=auth_headers(client),
    )
    assert response.status_code == 503


def test_food_health_healthy_with_fake(client):
    response = client.get(f"{API_V1}/food/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["model"] == "loaded"


def test_food_health_unavailable(client):
    set_food_detector(UnavailableFoodDetector())
    response = client.get(f"{API_V1}/food/health")
    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"


def test_aggregate_health_ok_when_food_unavailable(client):
    set_food_detector(UnavailableFoodDetector())
    response = client.get("/health")
    assert response.status_code == 200
    assert "food" not in response.json()["services"]
    food = client.get(f"{API_V1}/food/health")
    assert food.status_code == 503


def test_predict_rejects_too_many_pixels(client, monkeypatch):
    monkeypatch.setattr(settings, "food_max_pixels", 10)
    response = client.post(
        f"{API_V1}/food/predict",
        files={"image": ("meal.jpg", _jpeg(32, 24), "image/jpeg")},
        headers=auth_headers(client),
    )
    assert response.status_code == 400


def test_foods_log_line_from_class_ids_aggregates_labels():
    assert (
        foods_log_line_from_class_ids([5, 7, 7, 27])
        == "green-chutney, idli ×2, coconut-chutney"
    )


def test_foods_log_line_from_items_includes_quantity():
    assert foods_log_line_from_items([(7, 2), (29, 1)]) == "idli ×2, dosa ×1"


def test_nms_class_id_matches_training_id():
    # Do not apply Ultralytics metadata name order: 7 is idli, not onion-pakoda.
    assert class_id_for_onnx_index(7) == 7
    assert label_for_class_id(7) == "idli"
    assert class_id_for_onnx_index(15) == 15
    assert label_for_class_id(15) == "onion-pakoda"
    assert class_id_for_onnx_index(99) is None


def test_map_to_original_pixel_uses_letterbox_geometry():
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    _tensor, scale, pad_x, pad_y = letterbox_chw(image, 800)
    assert _map_to_original_pixel(0.0, scale, pad_x, 200) == pytest.approx(0.0)
    assert _map_to_original_pixel(800.0, scale, pad_x, 200) == pytest.approx(200.0)
    assert _map_to_original_pixel(200.0, scale, pad_y, 100) == pytest.approx(0.0)
    assert _map_to_original_pixel(600.0, scale, pad_y, 100) == pytest.approx(100.0)


def test_relative_food_model_path_joins_backend_root(monkeypatch):
    monkeypatch.setattr(settings, "food_model_path", "ml/models/food/best.onnx")
    model_path = settings.resolved_food_model_path
    assert model_path.is_absolute()
    assert model_path.name == "best.onnx"
    assert model_path.parent.name == "food"
    assert model_path.parts[-4:] == ("ml", "models", "food", "best.onnx")


def test_letterbox_output_shape():
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    tensor, scale, pad_x, pad_y = letterbox_chw(image, 800)
    assert tensor.shape == (1, 3, 800, 800)
    assert scale == pytest.approx(4.0)
    assert pad_x == pytest.approx(0.0)
    assert pad_y == pytest.approx(200.0)


@pytest.mark.skipif(
    not os.environ.get("FOOD_ONNX_SMOKE"),
    reason="set FOOD_ONNX_SMOKE=1 to run ONNX smoke",
)
def test_onnx_smoke_loads_and_runs():
    from services.food.services.food_detector_service import OnnxFoodDetector

    model_path = settings.resolved_food_model_path
    if not model_path.is_file():
        pytest.skip("best.onnx is not present")
    detector = OnnxFoodDetector(model_path)
    result = detector.predict(_jpeg(640, 480))
    assert result.image_width == 640
    assert result.image_height == 480
    assert isinstance(result.items, list)
