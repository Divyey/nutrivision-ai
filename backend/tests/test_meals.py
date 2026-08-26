from decimal import Decimal

from helpers import API_V1, VALID_USER, auth_headers, register
from infrastructure.database.models.dish_nutrition import DishNutrition
from services.food.services.food_nutrition_service import snapshot_for_quantity

DAY = "2026-08-23"
ENTRIES = f"{API_V1}/meals/entries"
DIARY = f"{API_V1}/meals/diary"
WATER = f"{API_V1}/meals/water"
# Obvious pytest fakes — not real IFCT/INDB values.
FAKE_CALORIES_PER_100G = Decimal("1")
FAKE_PROTEIN_PER_100G = Decimal("2")
FAKE_CARB_PER_100G = Decimal("3")
FAKE_FAT_PER_100G = Decimal("4")
FAKE_SERVING_GRAMS = Decimal("100")
CLASS_IDLI = 7


def _seed_fake_nutrition(db_session, class_id: int = CLASS_IDLI) -> None:
    db = db_session()
    try:
        db.add(
            DishNutrition(
                class_id=class_id,
                calories_per_100g=FAKE_CALORIES_PER_100G,
                protein_per_100g=FAKE_PROTEIN_PER_100G,
                carb_per_100g=FAKE_CARB_PER_100G,
                fat_per_100g=FAKE_FAT_PER_100G,
                default_serving_grams=FAKE_SERVING_GRAMS,
            )
        )
        db.commit()
    finally:
        db.close()


def _log_payload(quantity: float = 2, slot: str = "lunch", class_id: int = CLASS_IDLI):
    return {
        "logged_on": DAY,
        "slot": slot,
        "items": [{"class_id": class_id, "quantity": quantity}],
    }


def test_snapshot_quantity_is_default_servings(db_session):
    _seed_fake_nutrition(db_session)
    db = db_session()
    try:
        row = db.get(DishNutrition, CLASS_IDLI)
        one = snapshot_for_quantity(row, Decimal("1"))
        two = snapshot_for_quantity(row, Decimal("2"))
    finally:
        db.close()
    assert float(one.calories) == 1.0
    assert float(one.protein) == 2.0
    assert float(one.carb) == 3.0
    assert float(one.fat) == 4.0
    assert float(two.calories) == 2.0


def test_log_requires_auth(client):
    response = client.post(ENTRIES, json=_log_payload())
    assert response.status_code == 401


def test_diary_requires_auth(client):
    response = client.get(DIARY, params={"date": DAY})
    assert response.status_code == 401


def test_log_without_nutrition_row_returns_400(client):
    headers = auth_headers(client)
    response = client.post(ENTRIES, json=_log_payload(), headers=headers)
    assert response.status_code == 400
    assert "Nutrition" in response.json()["detail"]


def test_log_unknown_class_returns_422(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    response = client.post(
        ENTRIES,
        json=_log_payload(class_id=99),
        headers=headers,
    )
    assert response.status_code == 422


def test_log_invalid_slot_returns_422(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    response = client.post(
        ENTRIES,
        json=_log_payload(slot="brunch"),
        headers=headers,
    )
    assert response.status_code == 422


def test_log_and_diary_sums(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    created = client.post(ENTRIES, json=_log_payload(quantity=2), headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert len(body) == 1
    assert body[0]["label"] == "idli"
    assert body[0]["quantity"] == 2
    assert body[0]["calories"] == 2.0
    assert body[0]["protein"] == 4.0
    assert body[0]["carb"] == 6.0
    assert body[0]["fat"] == 8.0
    assert body[0]["slot"] == "lunch"
    assert body[0]["source"] == "scan"

    diary = client.get(DIARY, params={"date": DAY}, headers=headers)
    assert diary.status_code == 200
    day = diary.json()
    assert day["date"] == DAY
    assert len(day["slots"]["lunch"]) == 1
    assert day["slots"]["breakfast"] == []
    assert day["totals"]["calories"] == 2.0
    assert day["totals"]["protein"] == 4.0
    assert day["water"]["milliliters"] == 0


def test_diary_reads_snapshot_without_live_nutrition_lookup(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    logged = client.post(ENTRIES, json=_log_payload(quantity=2), headers=headers)
    assert logged.status_code == 201
    db = db_session()
    try:
        row = db.get(DishNutrition, CLASS_IDLI)
        db.delete(row)
        db.commit()
    finally:
        db.close()
    diary = client.get(DIARY, params={"date": DAY}, headers=headers)
    assert diary.status_code == 200
    assert diary.json()["totals"]["calories"] == 2.0
    entry_id = logged.json()[0]["id"]
    quantity_patch = client.patch(
        f"{ENTRIES}/{entry_id}", json={"quantity": 3}, headers=headers
    )
    assert quantity_patch.status_code == 400


def test_users_cannot_read_each_others_entries(client, db_session):
    _seed_fake_nutrition(db_session)
    ada = auth_headers(client)
    created = client.post(ENTRIES, json=_log_payload(), headers=ada).json()[0]
    register(client, email="other@example.com")
    other_token = client.post(
        f"{API_V1}/auth/login",
        json={"email": "other@example.com", "password": VALID_USER["password"]},
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {other_token}"}
    diary = client.get(DIARY, params={"date": DAY}, headers=other)
    assert diary.json()["slots"]["lunch"] == []
    patch = client.patch(
        f"{ENTRIES}/{created['id']}",
        json={"quantity": 1},
        headers=other,
    )
    assert patch.status_code == 404


def test_patch_quantity_resnapshots_patch_slot_does_not(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    entry_id = client.post(
        ENTRIES, json=_log_payload(quantity=1), headers=headers
    ).json()[0]["id"]
    quantity_patch = client.patch(
        f"{ENTRIES}/{entry_id}", json={"quantity": 3}, headers=headers
    )
    assert quantity_patch.status_code == 200
    assert quantity_patch.json()["calories"] == 3.0
    assert quantity_patch.json()["protein"] == 6.0
    slot = client.patch(
        f"{ENTRIES}/{entry_id}", json={"slot": "dinner"}, headers=headers
    )
    assert slot.status_code == 200
    assert slot.json()["slot"] == "dinner"
    assert slot.json()["calories"] == 3.0


def test_delete_meal_entry(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    entry_id = client.post(ENTRIES, json=_log_payload(), headers=headers).json()[0][
        "id"
    ]
    deleted = client.delete(f"{ENTRIES}/{entry_id}", headers=headers)
    assert deleted.status_code == 204
    diary = client.get(DIARY, params={"date": DAY}, headers=headers)
    assert diary.json()["slots"]["lunch"] == []


def test_water_add_and_remove(client):
    headers = auth_headers(client)
    created = client.post(
        WATER,
        json={"logged_on": DAY, "milliliters": 250},
        headers=headers,
    )
    assert created.status_code == 201
    water_id = created.json()["id"]
    diary = client.get(DIARY, params={"date": DAY}, headers=headers)
    assert diary.json()["water"]["milliliters"] == 250
    assert len(diary.json()["water"]["entries"]) == 1
    deleted = client.delete(f"{WATER}/{water_id}", headers=headers)
    assert deleted.status_code == 204
    diary = client.get(DIARY, params={"date": DAY}, headers=headers)
    assert diary.json()["water"]["milliliters"] == 0


def test_users_cannot_delete_each_others_water(client):
    ada = auth_headers(client)
    water_id = client.post(
        WATER,
        json={"logged_on": DAY, "milliliters": 250},
        headers=ada,
    ).json()["id"]
    register(client, email="other@example.com")
    other_token = client.post(
        f"{API_V1}/auth/login",
        json={"email": "other@example.com", "password": VALID_USER["password"]},
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {other_token}"}
    deleted = client.delete(f"{WATER}/{water_id}", headers=other)
    assert deleted.status_code == 404


def test_empty_items_rejected(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    response = client.post(
        ENTRIES,
        json={"logged_on": DAY, "slot": "lunch", "items": []},
        headers=headers,
    )
    assert response.status_code == 422


def test_typed_log_requires_food_or_class(client):
    headers = auth_headers(client)
    response = client.post(
        ENTRIES,
        json={"logged_on": DAY, "slot": "lunch", "items": [{"quantity": 1}]},
        headers=headers,
    )
    assert response.status_code == 422


def test_typed_log_roti_and_patch(client, db_session):
    from infrastructure.database.models.food import Food
    from services.nutrition.services.nutrition_catalog_seed import (
        DEFAULT_CSV,
        load_catalog_rows,
        upsert_catalog,
    )

    db = db_session()
    try:
        upsert_catalog(db, load_catalog_rows(DEFAULT_CSV))
        roti = db.query(Food).filter(Food.slug == "roti").one()
        roti_id = str(roti.id)
        default_unit = next(row.unit for row in roti.servings if row.is_default)
    finally:
        db.close()

    headers = auth_headers(client)
    created = client.post(
        ENTRIES,
        json={
            "logged_on": DAY,
            "slot": "breakfast",
            "items": [
                {"food_id": roti_id, "unit": default_unit, "quantity": 2},
            ],
        },
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()[0]
    assert body["source"] == "typed"
    assert body["class_id"] is None
    assert body["food_id"] == roti_id
    assert body["unit"] == default_unit
    assert body["calories"] > 0

    patched = client.patch(
        f"{ENTRIES}/{body['id']}", json={"quantity": 1}, headers=headers
    )
    assert patched.status_code == 200
    assert patched.json()["quantity"] == 1
    assert patched.json()["calories"] < body["calories"]

    grams = client.post(
        ENTRIES,
        json={
            "logged_on": DAY,
            "slot": "lunch",
            "items": [{"food_id": roti_id, "unit": "g", "quantity": 150}],
        },
        headers=headers,
    )
    assert grams.status_code == 201
    assert grams.json()[0]["quantity"] == 150

    large = client.patch(
        f"{ENTRIES}/{body['id']}", json={"unit": "large"}, headers=headers
    )
    assert large.status_code == 200
    assert large.json()["unit"] == "large"
    assert large.json()["calories"] > patched.json()["calories"]

    idli = db_session()
    try:
        idli_id = str(idli.query(Food).filter(Food.slug == "idli").one().id)
    finally:
        idli.close()
    swapped = client.patch(
        f"{ENTRIES}/{body['id']}",
        json={"food_id": idli_id, "unit": "piece", "quantity": 1},
        headers=headers,
    )
    assert swapped.status_code == 200
    assert swapped.json()["food_id"] == idli_id
    assert swapped.json()["unit"] == "piece"
    assert swapped.json()["label"] == "idli"
    assert swapped.json()["source"] == "typed"

    missing_unit = client.patch(
        f"{ENTRIES}/{body['id']}", json={"food_id": idli_id}, headers=headers
    )
    assert missing_unit.status_code == 422


def test_patch_scan_unit_requires_catalog_food(client, db_session):
    _seed_fake_nutrition(db_session)
    headers = auth_headers(client)
    entry_id = client.post(
        ENTRIES, json=_log_payload(quantity=1), headers=headers
    ).json()[0]["id"]
    response = client.patch(
        f"{ENTRIES}/{entry_id}", json={"unit": "piece"}, headers=headers
    )
    assert response.status_code == 400
    assert "catalog" in response.json()["detail"].lower()


def test_patch_scan_to_typed_catalog(client, db_session):
    from infrastructure.database.models.food import Food
    from services.nutrition.services.nutrition_catalog_seed import (
        DEFAULT_CSV,
        load_catalog_rows,
        upsert_catalog,
    )

    _seed_fake_nutrition(db_session)
    db = db_session()
    try:
        upsert_catalog(db, load_catalog_rows(DEFAULT_CSV))
        idli_id = str(db.query(Food).filter(Food.slug == "idli").one().id)
    finally:
        db.close()

    headers = auth_headers(client)
    entry_id = client.post(
        ENTRIES, json=_log_payload(quantity=1), headers=headers
    ).json()[0]["id"]
    response = client.patch(
        f"{ENTRIES}/{entry_id}",
        json={"food_id": idli_id, "unit": "piece", "quantity": 1},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "typed"
    assert body["food_id"] == idli_id
    assert body["unit"] == "piece"
    assert body["label"] == "idli"


def test_typed_log_incomplete_food_returns_400(client, db_session):
    from infrastructure.database.models.food import Food
    from services.nutrition.services.nutrition_catalog_seed import (
        DEFAULT_CSV,
        load_catalog_rows,
        upsert_catalog,
    )

    db = db_session()
    try:
        upsert_catalog(db, load_catalog_rows(DEFAULT_CSV))
        ghevar_id = str(db.query(Food).filter(Food.slug == "ghevar").one().id)
    finally:
        db.close()

    headers = auth_headers(client)
    response = client.post(
        ENTRIES,
        json={
            "logged_on": DAY,
            "slot": "snacks",
            "items": [{"food_id": ghevar_id, "unit": "serving", "quantity": 1}],
        },
        headers=headers,
    )
    assert response.status_code == 400
