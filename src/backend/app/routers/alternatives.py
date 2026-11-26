"""Benchmark alternatives catalog routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import AlternativeCatalog, User
from app.schemas import AlternativeCreate, AlternativeResponse


router = APIRouter(prefix="/api/alternatives", tags=["alternatives"])


@router.get("", response_model=list[AlternativeResponse])
def list_alternatives(
    category: str | None = Query(default=None),
    target_software: str | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AlternativeResponse]:
    """List available software alternatives with optional filtering."""
    stmt = select(AlternativeCatalog).order_by(AlternativeCatalog.target_software)
    if category:
        stmt = stmt.where(AlternativeCatalog.category.ilike(f"%{category.strip()}%"))
    if target_software:
        stmt = stmt.where(AlternativeCatalog.target_software.ilike(f"%{target_software.strip()}%"))

    rows = list(db.scalars(stmt))
    return [AlternativeResponse.model_validate(row) for row in rows]


@router.post("", response_model=AlternativeResponse, status_code=status.HTTP_201_CREATED)
def create_alternative(
    payload: AlternativeCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AlternativeResponse:
    """Add an alternative to the benchmark catalog (admin only)."""
    alt = AlternativeCatalog(**payload.model_dump())
    db.add(alt)
    db.commit()
    db.refresh(alt)
    return AlternativeResponse.model_validate(alt)
