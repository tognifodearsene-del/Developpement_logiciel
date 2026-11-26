"""Routes CRUD du parc logiciel et d'import CSV (/api/inventory)."""

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import SoftwareItem, User
from app.schemas import (
    CsvImportResponse,
    InventorySummary,
    SoftwareItemCreate,
    SoftwareItemResponse,
    SoftwareItemUpdate,
)
from app.services.csv_parser import parse_inventory_csv
from app.services.roi_engine import compute_item_metrics


router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def _serialize_item(item: SoftwareItem) -> SoftwareItemResponse:
    """Enrichit un SoftwareItem ORM avec ses métriques annuelles et d'utilisation."""
    annual_cost, utilization_rate, is_underutilized = compute_item_metrics(
        item.monthly_cost_total, item.licenses_purchased, item.licenses_used
    )
    return SoftwareItemResponse(
        id=item.id,
        user_id=item.user_id,
        name=item.name,
        category=item.category,
        vendor=item.vendor,
        licenses_purchased=item.licenses_purchased,
        licenses_used=item.licenses_used,
        monthly_cost_total=item.monthly_cost_total,
        annual_cost=annual_cost,
        utilization_rate=utilization_rate,
        is_underutilized=is_underutilized,
        created_at=item.created_at,
    )


def _get_owned_item(db: Session, item_id: int, user_id: int) -> SoftwareItem:
    """Vérifie qu'un logiciel existe et appartient bien à l'utilisateur connecté (isolation multi-tenant)."""
    item = db.scalar(
        select(SoftwareItem).where(SoftwareItem.id == item_id, SoftwareItem.user_id == user_id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Logiciel introuvable")
    return item


@router.get("", response_model=InventorySummary)
def list_inventory(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InventorySummary:
    """Liste le parc logiciel de l'utilisateur avec les indicateurs agrégés du tableau de bord."""
    rows = list(
        db.scalars(
            select(SoftwareItem)
            .where(SoftwareItem.user_id == current_user.id)
            .order_by(SoftwareItem.id.desc())
        )
    )
    serialized = [_serialize_item(row) for row in rows]
    total_monthly = round(sum(item.monthly_cost_total for item in serialized), 2)
    total_annual = round(sum(item.annual_cost for item in serialized), 2)
    avg_util = (
        round(sum(item.utilization_rate for item in serialized) / len(serialized), 2)
        if serialized
        else 0.0
    )
    underutilized_count = sum(1 for item in serialized if item.is_underutilized)
    return InventorySummary(
        items=serialized,
        total_software_count=len(serialized),
        total_monthly_cost=total_monthly,
        total_annual_cost=total_annual,
        average_utilization_rate=avg_util,
        underutilized_count=underutilized_count,
    )


@router.post("", response_model=SoftwareItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: SoftwareItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SoftwareItemResponse:
    """Ajoute manuellement un logiciel dans l'inventaire du client."""
    item = SoftwareItem(
        user_id=current_user.id,
        name=payload.name.strip(),
        category=payload.category.strip(),
        vendor=payload.vendor.strip(),
        licenses_purchased=payload.licenses_purchased,
        licenses_used=payload.licenses_used,
        monthly_cost_total=payload.monthly_cost_total,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize_item(item)


@router.put("/{item_id}", response_model=SoftwareItemResponse)
def update_item(
    item_id: int,
    payload: SoftwareItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SoftwareItemResponse:
    """Met à jour partiellement un logiciel tout en recontrôlant la cohérence des licences."""
    item = _get_owned_item(db, item_id, current_user.id)

    updates = payload.model_dump(exclude_unset=True)
    # Revalidation croisée nécessaire car la mise à jour peut ne modifier qu'un des deux compteurs
    new_purchased = updates.get("licenses_purchased", item.licenses_purchased)
    new_used = updates.get("licenses_used", item.licenses_used)
    if new_used > new_purchased:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="licenses_used ne peut pas dépasser licenses_purchased",
        )

    for field, value in updates.items():
        setattr(item, field, value.strip() if isinstance(value, str) else value)

    db.commit()
    db.refresh(item)
    return _serialize_item(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Supprime un logiciel du parc de l'utilisateur."""
    item = _get_owned_item(db, item_id, current_user.id)
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/import-csv", response_model=CsvImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CsvImportResponse:
    """Importe un fichier CSV : insère les lignes valides et remonte les erreurs ligne par ligne."""
    content = await file.read()
    parsed_items, errors = parse_inventory_csv(content)

    created_models: list[SoftwareItem] = []
    for entry in parsed_items:
        model = SoftwareItem(
            user_id=current_user.id,
            name=entry.name,
            category=entry.category,
            vendor=entry.vendor,
            licenses_purchased=entry.licenses_purchased,
            licenses_used=entry.licenses_used,
            monthly_cost_total=entry.monthly_cost_total,
        )
        db.add(model)
        created_models.append(model)

    if created_models:
        db.commit()
        for model in created_models:
            db.refresh(model)

    return CsvImportResponse(
        imported_count=len(created_models),
        skipped_count=len(errors),
        errors=errors,
        items=[_serialize_item(m) for m in created_models],
    )
