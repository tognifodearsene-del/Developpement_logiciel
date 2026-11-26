"""Initialisation idempotente du catalogue d'alternatives depuis le fichier JSON de référence."""

import json
from pathlib import Path
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AlternativeCatalog


def seed_alternatives(db: Session, seed_path: Path) -> int:
    """Peuple la table alternatives_catalog si elle est encore vide (idempotent)."""
    existing_count = db.scalar(select(func.count(AlternativeCatalog.id))) or 0
    if existing_count > 0 or not seed_path.exists():
        return 0

    raw_items = json.loads(seed_path.read_text(encoding="utf-8"))
    created = 0
    for entry in raw_items:
        db.add(
            AlternativeCatalog(
                target_software=entry["target_software"],
                category=entry["category"],
                alternative_name=entry["alternative_name"],
                vendor_or_license=entry.get("vendor_or_license", "Open Source"),
                is_open_source=bool(entry.get("is_open_source", True)),
                estimated_monthly_cost_per_user=float(entry.get("estimated_monthly_cost_per_user", 0.0)),
                estimated_migration_cost=float(entry.get("estimated_migration_cost", 0.0)),
                feature_match_score=int(entry.get("feature_match_score", 80)),
                description=entry.get("description", ""),
            )
        )
        created += 1

    db.commit()
    return created
