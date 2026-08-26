from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from infrastructure.database.models.food import Food, FoodServing
from infrastructure.database.models.meal_entry import MealEntry
from infrastructure.database.models.user import User
from infrastructure.database.models.water_entry import WaterEntry
from services.food.services.food_classes_service import label_for_class_id
from services.food.services.food_nutrition_service import (
    get_dish_nutrition,
    snapshot_for_quantity,
)
from services.meals.schema.meals_schema import (
    DiaryResponse,
    LogMealsRequest,
    LogWaterRequest,
    MacroTotals,
    MealEntryResponse,
    MealSlot,
    PatchMealEntryRequest,
    WaterDayResponse,
    WaterEntryResponse,
)
from services.nutrition.services.nutrition_macros_service import (
    MacroSnapshot,
    NutritionError,
    snapshot_for_grams,
)

MEAL_SOURCE_SCAN = "scan"
MEAL_SOURCE_TYPED = "typed"
SLOTS = tuple(MealSlot)


class MealsError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class _MacroFields(Protocol):
    calories: Decimal
    protein: Decimal
    carb: Decimal
    fat: Decimal


def _as_float(value: object) -> float:
    return float(value)


def _to_entry_response(entry: MealEntry) -> MealEntryResponse:
    return MealEntryResponse(
        id=entry.id,
        logged_on=entry.logged_on,
        slot=MealSlot(entry.slot),
        source=entry.source,
        class_id=entry.class_id,
        food_id=entry.food_id,
        unit=entry.unit,
        label=entry.label,
        quantity=_as_float(entry.quantity),
        calories=_as_float(entry.calories),
        protein=_as_float(entry.protein),
        carb=_as_float(entry.carb),
        fat=_as_float(entry.fat),
    )


def _to_water_response(entry: WaterEntry) -> WaterEntryResponse:
    return WaterEntryResponse(
        id=entry.id,
        logged_on=entry.logged_on,
        milliliters=entry.milliliters,
    )


def _snapshot_or_raise(db: Session, class_id: int, quantity: Decimal):
    label = label_for_class_id(class_id)
    if label is None:
        raise MealsError(400, "Unknown food class.")
    row = get_dish_nutrition(db, class_id)
    if row is None:
        raise MealsError(400, "Nutrition data is not available for this food class.")
    return label, snapshot_for_quantity(row, quantity)


def _serving_for_unit(food: Food, unit: str) -> FoodServing:
    for serving in food.servings:
        if serving.unit == unit:
            return serving
    raise MealsError(400, "Unknown serving unit for this food.")


def _typed_snapshot(
    db: Session, food_id: UUID, unit: str, quantity: Decimal
) -> tuple[Food, MacroSnapshot]:
    food = (
        db.query(Food)
        .options(selectinload(Food.servings))
        .filter(Food.id == food_id)
        .one_or_none()
    )
    if food is None:
        raise MealsError(400, "Unknown food.")
    serving = _serving_for_unit(food, unit)
    grams = quantity * serving.grams
    try:
        return food, snapshot_for_grams(food, grams)
    except NutritionError as exc:
        raise MealsError(exc.status_code, exc.detail) from exc


def log_meals(
    db: Session, user: User, payload: LogMealsRequest
) -> list[MealEntryResponse]:
    created: list[MealEntry] = []
    for meal_item in payload.items:
        quantity = Decimal(str(meal_item.quantity))
        if meal_item.food_id is not None:
            if meal_item.unit is None:
                raise MealsError(400, "unit is required when logging a catalog food.")
            food, snapshot = _typed_snapshot(
                db, meal_item.food_id, meal_item.unit, quantity
            )
            entry = MealEntry(
                user_id=user.id,
                logged_on=payload.logged_on,
                slot=payload.slot.value,
                source=MEAL_SOURCE_TYPED,
                class_id=food.detect_class_id,
                food_id=food.id,
                unit=meal_item.unit,
                label=food.name,
                quantity=quantity,
                calories=snapshot.calories,
                protein=snapshot.protein,
                carb=snapshot.carb,
                fat=snapshot.fat,
            )
        else:
            if meal_item.class_id is None:
                raise MealsError(400, "Provide either class_id or food_id.")
            label, snapshot = _snapshot_or_raise(db, meal_item.class_id, quantity)
            entry = MealEntry(
                user_id=user.id,
                logged_on=payload.logged_on,
                slot=payload.slot.value,
                source=MEAL_SOURCE_SCAN,
                class_id=meal_item.class_id,
                food_id=None,
                unit=None,
                label=label,
                quantity=quantity,
                calories=snapshot.calories,
                protein=snapshot.protein,
                carb=snapshot.carb,
                fat=snapshot.fat,
            )
        db.add(entry)
        created.append(entry)
    db.commit()
    for entry in created:
        db.refresh(entry)
    return [_to_entry_response(entry) for entry in created]


def _owned_meal(db: Session, user: User, entry_id: UUID) -> MealEntry:
    entry = (
        db.query(MealEntry)
        .filter(MealEntry.id == entry_id, MealEntry.user_id == user.id)
        .one_or_none()
    )
    if entry is None:
        raise MealsError(404, "Meal entry not found.")
    return entry


def _owned_water(db: Session, user: User, entry_id: UUID) -> WaterEntry:
    entry = (
        db.query(WaterEntry)
        .filter(WaterEntry.id == entry_id, WaterEntry.user_id == user.id)
        .one_or_none()
    )
    if entry is None:
        raise MealsError(404, "Water entry not found.")
    return entry


def _apply_macros(entry: MealEntry, quantity: Decimal, snapshot: _MacroFields) -> None:
    entry.quantity = quantity
    entry.calories = snapshot.calories
    entry.protein = snapshot.protein
    entry.carb = snapshot.carb
    entry.fat = snapshot.fat


def patch_meal_entry(
    db: Session, user: User, entry_id: UUID, payload: PatchMealEntryRequest
) -> MealEntryResponse:
    entry = _owned_meal(db, user, entry_id)
    if payload.slot is not None:
        entry.slot = payload.slot.value
    food_changed = payload.food_id is not None or payload.unit is not None
    if payload.quantity is not None or food_changed:
        quantity = Decimal(
            str(payload.quantity if payload.quantity is not None else entry.quantity)
        )
        food_id = payload.food_id if payload.food_id is not None else entry.food_id
        unit = payload.unit if payload.unit is not None else entry.unit
        if food_id is not None:
            if unit is None:
                raise MealsError(400, "This entry has no serving unit.")
            food, snapshot = _typed_snapshot(db, food_id, unit, quantity)
            entry.source = MEAL_SOURCE_TYPED
            entry.food_id = food.id
            entry.unit = unit
            entry.label = food.name
            entry.class_id = food.detect_class_id
            _apply_macros(entry, quantity, snapshot)
        else:
            if payload.unit is not None:
                raise MealsError(400, "unit is only valid with a catalog food.")
            if entry.class_id is None:
                raise MealsError(400, "Nutrition data is not available for this food.")
            _label, snapshot = _snapshot_or_raise(db, entry.class_id, quantity)
            _apply_macros(entry, quantity, snapshot)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_entry_response(entry)


def delete_meal_entry(db: Session, user: User, entry_id: UUID) -> None:
    entry = _owned_meal(db, user, entry_id)
    db.delete(entry)
    db.commit()


def log_water(db: Session, user: User, payload: LogWaterRequest) -> WaterEntryResponse:
    entry = WaterEntry(
        user_id=user.id,
        logged_on=payload.logged_on,
        milliliters=payload.milliliters,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_water_response(entry)


def delete_water_entry(db: Session, user: User, entry_id: UUID) -> None:
    entry = _owned_water(db, user, entry_id)
    db.delete(entry)
    db.commit()


def get_diary(db: Session, user: User, logged_on: date) -> DiaryResponse:
    meals = (
        db.query(MealEntry)
        .filter(MealEntry.user_id == user.id, MealEntry.logged_on == logged_on)
        .order_by(MealEntry.created_at.asc())
        .all()
    )
    waters = (
        db.query(WaterEntry)
        .filter(WaterEntry.user_id == user.id, WaterEntry.logged_on == logged_on)
        .order_by(WaterEntry.created_at.asc())
        .all()
    )
    slots: dict[MealSlot, list[MealEntryResponse]] = {slot: [] for slot in SLOTS}
    totals = {"calories": 0.0, "protein": 0.0, "carb": 0.0, "fat": 0.0}
    for meal in meals:
        response = _to_entry_response(meal)
        slots[response.slot].append(response)
        totals["calories"] += response.calories
        totals["protein"] += response.protein
        totals["carb"] += response.carb
        totals["fat"] += response.fat
    water_ml = sum(entry.milliliters for entry in waters)
    return DiaryResponse(
        date=logged_on,
        slots=slots,
        water=WaterDayResponse(
            milliliters=water_ml,
            entries=[_to_water_response(entry) for entry in waters],
        ),
        totals=MacroTotals(
            calories=round(totals["calories"], 2),
            protein=round(totals["protein"], 2),
            carb=round(totals["carb"], 2),
            fat=round(totals["fat"], 2),
        ),
    )
