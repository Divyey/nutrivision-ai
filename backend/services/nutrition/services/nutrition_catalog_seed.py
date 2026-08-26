"""Parse foods_catalog.csv and upsert foods, aliases, and servings.

Nutrition service owns this catalog. Do not invent INDB values. Incomplete
rows (no per-100g) are stored with status=incomplete and no servings. Search
hides them.

  python scripts/upsert_foods_catalog.py
"""

from __future__ import annotations

import csv
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy.orm import Session

from infrastructure.database.models.food import Food, FoodAlias, FoodServing

DEFAULT_CSV = Path(__file__).resolve().parents[3] / "data" / "foods_catalog.csv"

FOOD_ID_NS = uuid.UUID("a6c00600-0000-4000-8000-000000000006")
ALIAS_ID_NS = uuid.UUID("a6c00601-0000-4000-8000-000000000006")
SERVING_ID_NS = uuid.UUID("a6c00602-0000-4000-8000-000000000006")

STATUS_COMPLETE = "complete"
STATUS_INCOMPLETE = "incomplete"
NUMERIC_FIELDS = (
    "calories_per_100g",
    "protein_per_100g",
    "carb_per_100g",
    "fat_per_100g",
    "default_serving_grams",
)
REQUIRED_COLUMNS = (
    "slug",
    "name",
    "detect_class_id",
    "status",
    *NUMERIC_FIELDS,
    "density_g_per_ml",
    "source_dataset",
    "source_id",
    "source_note",
    "aliases",
    "indb_serving_unit",
)

INDB_UNIT_MAP = {
    "chapati": "piece",
    "roti": "piece",
    "parantha": "piece",
    "naan": "piece",
    "thepla": "piece",
    "dosa": "piece",
    "idli": "piece",
    "omelette": "piece",
    "egg": "piece",
    "piece": "piece",
    "dhokla": "piece",
    "appam": "piece",
    "puttu": "piece",
    "bowl": "bowl",
    "small bowl": "bowl",
    "curry bowl": "bowl",
    "soup bowl": "bowl",
    "plate": "serving",
    "small plate": "serving",
    "tall glass": "ml",
    "glass": "ml",
    "cup": "ml",
}


class SeedError(Exception):
    """CSV is malformed or a row is only partly filled."""


@dataclass(frozen=True)
class CatalogRow:
    slug: str
    name: str
    detect_class_id: int | None
    status: str
    calories_per_100g: Decimal | None
    protein_per_100g: Decimal | None
    carb_per_100g: Decimal | None
    fat_per_100g: Decimal | None
    density_g_per_ml: Decimal | None
    source_dataset: str
    source_id: str
    source_note: str
    aliases: tuple[str, ...]
    indb_serving_unit: str
    default_serving_grams: Decimal | None


def food_uuid(slug: str) -> uuid.UUID:
    return uuid.uuid5(FOOD_ID_NS, slug)


def _cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def _parse_decimal(raw: str, field: str, slug: str) -> Decimal:
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise SeedError(f"{slug}: invalid {field} {raw!r}") from exc
    if value <= 0:
        raise SeedError(f"{slug}: {field} must be > 0")
    return value


def normalize_alias(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").replace("/", " ").split())


def _aliases(raw: str, slug: str, name: str) -> tuple[str, ...]:
    ordered = [normalize_alias(slug), normalize_alias(name)]
    ordered.extend(normalize_alias(part) for part in raw.split(","))
    return tuple(dict.fromkeys(alias for alias in ordered if alias))


def load_catalog_rows(path: Path) -> list[CatalogRow]:
    if not path.is_file():
        raise SeedError(f"CSV not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SeedError("CSV has no header.")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise SeedError(f"CSV missing columns: {', '.join(missing)}")

        rows: list[CatalogRow] = []
        seen_slugs: set[str] = set()
        seen_class_ids: set[int] = set()
        for row in reader:
            slug = _cell(row, "slug")
            if not slug:
                raise SeedError("Empty slug.")
            if slug in seen_slugs:
                raise SeedError(f"Duplicate slug {slug}")
            seen_slugs.add(slug)
            status = _cell(row, "status")
            if status not in {STATUS_COMPLETE, STATUS_INCOMPLETE}:
                raise SeedError(f"{slug}: status must be complete or incomplete")
            raw_class = _cell(row, "detect_class_id")
            detect_class_id = int(raw_class) if raw_class else None
            if detect_class_id is not None:
                if detect_class_id in seen_class_ids:
                    raise SeedError(f"Duplicate detect_class_id {detect_class_id}")
                seen_class_ids.add(detect_class_id)

            empty = [field for field in NUMERIC_FIELDS if not _cell(row, field)]
            if status == STATUS_INCOMPLETE:
                if len(empty) != len(NUMERIC_FIELDS):
                    raise SeedError(
                        f"{slug}: incomplete rows must leave all numeric columns empty"
                    )
                calories = protein = carb = fat = serving = None
            else:
                if empty:
                    raise SeedError(
                        f"{slug}: complete rows need all numeric columns "
                        f"({', '.join(empty)} empty)"
                    )
                calories = _parse_decimal(
                    _cell(row, "calories_per_100g"), "calories_per_100g", slug
                )
                protein = _parse_decimal(
                    _cell(row, "protein_per_100g"), "protein_per_100g", slug
                )
                carb = _parse_decimal(
                    _cell(row, "carb_per_100g"), "carb_per_100g", slug
                )
                fat = _parse_decimal(_cell(row, "fat_per_100g"), "fat_per_100g", slug)
                serving = _parse_decimal(
                    _cell(row, "default_serving_grams"),
                    "default_serving_grams",
                    slug,
                )

            density_raw = _cell(row, "density_g_per_ml")
            density = (
                _parse_decimal(density_raw, "density_g_per_ml", slug)
                if density_raw
                else None
            )
            rows.append(
                CatalogRow(
                    slug=slug,
                    name=_cell(row, "name") or slug,
                    detect_class_id=detect_class_id,
                    status=status,
                    calories_per_100g=calories,
                    protein_per_100g=protein,
                    carb_per_100g=carb,
                    fat_per_100g=fat,
                    density_g_per_ml=density,
                    source_dataset=_cell(row, "source_dataset"),
                    source_id=_cell(row, "source_id"),
                    source_note=_cell(row, "source_note"),
                    aliases=_aliases(_cell(row, "aliases"), slug, _cell(row, "name")),
                    indb_serving_unit=_cell(row, "indb_serving_unit").lower(),
                    default_serving_grams=serving,
                )
            )
    return rows


def servings_for_row(
    row: CatalogRow,
) -> list[tuple[str, Decimal, Decimal | None, bool]]:
    """Return (unit, grams, milliliters, is_default)."""
    if row.status != STATUS_COMPLETE or row.default_serving_grams is None:
        return []
    default = row.default_serving_grams
    mapped = INDB_UNIT_MAP.get(row.indb_serving_unit)
    if row.density_g_per_ml is not None:
        mapped = "ml"
    default_unit = mapped or "serving"
    rows: list[tuple[str, Decimal, Decimal | None, bool]] = [
        ("g", Decimal("1"), None, False),
        ("small", (default * Decimal("0.5")).quantize(Decimal("0.01")), None, False),
        ("medium", default, None, default_unit == "medium"),
        ("large", (default * Decimal("1.5")).quantize(Decimal("0.01")), None, False),
        ("serving", default, None, default_unit == "serving"),
    ]
    if default_unit == "piece":
        rows.append(("piece", default, None, True))
    elif default_unit == "bowl":
        rows.append(("bowl", default, None, True))
        rows.append(("katori", default, None, False))
    elif default_unit == "ml":
        milliliters = default
        if row.density_g_per_ml is not None:
            milliliters = (default / row.density_g_per_ml).quantize(Decimal("0.01"))
        rows.append(("ml", default, milliliters, True))
        rows.append(("cup", default, milliliters, False))
    by_unit: dict[str, tuple[str, Decimal, Decimal | None, bool]] = {}
    for item in rows:
        by_unit.setdefault(item[0], item)
    unique = list(by_unit.values())
    if not any(item[3] for item in unique):
        unique = [
            (unit, grams, milliliters, unit == "serving")
            for unit, grams, milliliters, _is_default in unique
        ]
    return unique


def upsert_catalog(db: Session, rows: list[CatalogRow]) -> int:
    for row in rows:
        food_id = food_uuid(row.slug)
        existing = db.get(Food, food_id)
        if existing is None:
            existing = db.query(Food).filter(Food.slug == row.slug).one_or_none()
        if existing is None:
            existing = Food(id=food_id, slug=row.slug)
            db.add(existing)
        existing.slug = row.slug
        existing.name = row.name
        existing.detect_class_id = row.detect_class_id
        existing.calories_per_100g = row.calories_per_100g
        existing.protein_per_100g = row.protein_per_100g
        existing.carb_per_100g = row.carb_per_100g
        existing.fat_per_100g = row.fat_per_100g
        existing.density_g_per_ml = row.density_g_per_ml
        existing.source_dataset = row.source_dataset or None
        existing.source_id = row.source_id or None
        existing.source_note = row.source_note or None
        existing.status = row.status
        db.flush()
        db.query(FoodAlias).filter(FoodAlias.food_id == existing.id).delete()
        db.query(FoodServing).filter(FoodServing.food_id == existing.id).delete()
        for alias in row.aliases:
            db.add(
                FoodAlias(
                    id=uuid.uuid5(ALIAS_ID_NS, f"{row.slug}:{alias}"),
                    food_id=existing.id,
                    alias=alias,
                )
            )
        for unit, grams, milliliters, is_default in servings_for_row(row):
            db.add(
                FoodServing(
                    id=uuid.uuid5(SERVING_ID_NS, f"{row.slug}:{unit}"),
                    food_id=existing.id,
                    unit=unit,
                    grams=grams,
                    milliliters=milliliters,
                    is_default=is_default,
                )
            )
    db.commit()
    return len(rows)
