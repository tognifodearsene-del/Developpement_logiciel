"""Routes d'export des rapports au format CSV ou PDF (/api/reports)."""

from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import AnalysisReport, Recommendation, User
from app.services.report_exporter import export_report_csv, export_report_pdf


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{report_id}/export")
def export_report(
    report_id: int,
    format: Literal["csv", "pdf"] = Query(default="csv"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Télécharge un rapport d'analyse au format CSV ou PDF en pièce jointe HTTP."""
    report = db.scalar(
        select(AnalysisReport)
        .options(
            selectinload(AnalysisReport.owner),
            selectinload(AnalysisReport.recommendations).selectinload(Recommendation.software_item),
            selectinload(AnalysisReport.recommendations).selectinload(Recommendation.alternative),
        )
        .where(AnalysisReport.id == report_id, AnalysisReport.user_id == current_user.id)
    )
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rapport introuvable")

    if format == "pdf":
        payload = export_report_pdf(report)
        return Response(
            content=payload,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="optistack-rapport-{report_id}.pdf"'},
        )

    payload = export_report_csv(report)
    return Response(
        content=payload,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="optistack-rapport-{report_id}.csv"'},
    )
