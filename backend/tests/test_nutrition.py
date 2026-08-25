from decimal import Decimal

from infrastructure.database.models.food import Food
from helpers import API_V1, auth_headers
from services.nutrition.services.nutrition_catalog_seed import (
    DEFAULT_CSV,
    load_catalog_rows,
    servings_for_row,
    upsert_catalog,
)
from services.nutrition.services.nutrition_macros_service import snapshot_for_grams


def _seed_catalog(db_session):
    db = db_session()
    try:
        upsert_catalog(db, load_catalog_rows(DEFAULT_CSV))
    finally:
        db.close()


def test_committed_catalog_has_detect_gaps_and_roti():
    rows = load_catalog_rows(DEFAULT_CSV)
    by_slug = {row.slug: row for row in rows}
    assert by_slug["idli"].detect_class_id == 7
    assert by_slug["idli"].status == "complete"
    assert by_slug["idli"].source_id == "ASC144"
    assert by_slug["ghevar"].status == "incomplete"
    assert by_slug["jalebi"].status == "incomplete"
    assert by_slug["bhature"].status == "incomplete"
    assert servings_for_row(by_slug["ghevar"]) == []
    assert by_slug["roti"].detect_class_id is None
    assert by_slug["roti"].status == "complete"
    assert "chapati" in by_slug["roti"].aliases
    assert 80 <= len(rows) <= 120


def test_search_requires_auth(client):
    response = client.get(f"{API_V1}/nutrition/search", params={"q": "idli"})
    assert response.status_code == 401


def test_search_idli_and_aloo_gobhi(client, db_session):
    _seed_catalog(db_session)
    headers = auth_headers(client)
    idli = client.get(
        f"{API_V1}/nutrition/search", params={"q": "idli"}, headers=headers
    )
    assert idli.status_code == 200
    hit = next(item for item in idli.json()["items"] if item["slug"] == "idli")
    assert hit["detect_class_id"] == 7
    assert hit["source_id"] == "ASC144"
    units = {row["unit"] for row in hit["servings"]}
    assert "g" in units
    assert "piece" in units
    assert any(row["is_default"] for row in hit["servings"])

    gobhi = client.get(
        f"{API_V1}/nutrition/search", params={"q": "aloo gobhi"}, headers=headers
    )
    assert gobhi.status_code == 200
    slugs = [item["slug"] for item in gobhi.json()["items"]]
    assert "aloo-gobi" in slugs


def test_search_roti_and_chapati(client, db_session):
    _seed_catalog(db_session)
    headers = auth_headers(client)
    for query in ("roti", "chapati"):
        response = client.get(
            f"{API_V1}/nutrition/search", params={"q": query}, headers=headers
        )
        assert response.status_code == 200
        slugs = [item["slug"] for item in response.json()["items"]]
        assert "roti" in slugs
        assert slugs[0] == "roti" or "roti" in slugs
        roti = next(item for item in response.json()["items"] if item["slug"] == "roti")
        assert roti["detect_class_id"] is None


def test_search_hides_incomplete_detect_classes(client, db_session):
    _seed_catalog(db_session)
    headers = auth_headers(client)
    for query in ("ghevar", "jalebi", "bhature"):
        response = client.get(
            f"{API_V1}/nutrition/search", params={"q": query}, headers=headers
        )
        assert response.status_code == 200
        assert response.json()["items"] == []


def test_get_food_requires_auth(client):
    response = client.get(f"{API_V1}/nutrition/00000000-0000-4000-8000-000000000099")
    assert response.status_code == 401


def test_get_food_by_id(client, db_session):
    _seed_catalog(db_session)
    db = db_session()
    try:
        roti_id = str(db.query(Food).filter(Food.slug == "roti").one().id)
        ghevar_id = str(db.query(Food).filter(Food.slug == "ghevar").one().id)
    finally:
        db.close()
    headers = auth_headers(client)
    roti = client.get(f"{API_V1}/nutrition/{roti_id}", headers=headers)
    assert roti.status_code == 200
    assert roti.json()["slug"] == "roti"
    assert roti.json()["servings"]
    hidden = client.get(f"{API_V1}/nutrition/{ghevar_id}", headers=headers)
    assert hidden.status_code == 404
    missing = client.get(
        f"{API_V1}/nutrition/00000000-0000-4000-8000-000000000099",
        headers=headers,
    )
    assert missing.status_code == 404


def test_snapshot_for_grams_matches_per_100g(db_session):
    _seed_catalog(db_session)
    db = db_session()
    try:
        food = db.query(Food).filter(Food.slug == "idli").one()
        snap = snapshot_for_grams(food, Decimal("100"))
        assert snap.calories == food.calories_per_100g
        half = snapshot_for_grams(food, Decimal("50"))
        assert float(half.calories) == round(float(food.calories_per_100g) / 2, 2)
    finally:
        db.close()
