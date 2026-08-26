"""Upsert the curated foods catalog from CSV. Run from backend/ against Neon.

Does not load the INDB xlsx. Incomplete rows are stored but are not search hits.

  python scripts/upsert_foods_catalog.py
  python scripts/upsert_foods_catalog.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from infrastructure.database.session import SessionLocal  # noqa: E402
from services.nutrition.services.nutrition_catalog_seed import (  # noqa: E402
    DEFAULT_CSV,
    SeedError,
    load_catalog_rows,
    upsert_catalog,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upsert curated foods catalog from CSV."
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        rows = load_catalog_rows(args.csv)
    except SeedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    complete = sum(1 for row in rows if row.status == "complete")
    incomplete = len(rows) - complete
    print(f"rows={len(rows)} complete={complete} incomplete={incomplete}")
    for row in rows:
        print(
            f"slug={row.slug} status={row.status} class={row.detect_class_id} "
            f"source={row.source_id or '-'}"
        )
    if args.dry_run:
        print("dry-run: no database writes")
        return 0

    db = SessionLocal()
    try:
        count = upsert_catalog(db, rows)
    finally:
        db.close()
    print(f"upserted {count} foods")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
