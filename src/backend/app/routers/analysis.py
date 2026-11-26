"""Routes de lancement d'analyse financière et de consultation des rapports ROI (/api/analysis)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import AnalysisReport, Recommendation, SoftwareItem, User
from app.schemas import AnalysisReportDetail, AnalysisReportSummary, RecommendationResponse
from app.services.roi_engine import generate_analysis_report


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _serialize_report_summary(report: AnalysisReport) -> AnalysisReportSummary:
    """Convertit un rapport ORM en résumé financier pour la liste d'historique."""
    return AnalysisReportSummary(
        id=report.id,
        total_current_annual_cost=report.total_current_annual_cost,
        total_estimated_annual_savings=report.total_estimated_annual_savings,
        total_migration_cost=report.total_migration_cost,
        global_roi_percent=report.global_roi_percent,
        payback_months=report.payback_months,
        recommendation_count=len(report.recommendations),
        created_at=report.created_at,
    )


def _serialize_report_detail(report: AnalysisReport) -> AnalysisReportDetail:
    """Assemble la vue détaillée d'un rapport et de ses recommandations ordonnées."""
    recs = [
        RecommendationResponse(
            id=rec.id,
            priority_rank=rec.priority_rank,
            software_item_id=rec.software_item_id,
            software_name=rec.software_item.name,
            category=rec.software_item.category,
            alternative_id=rec.alternative_id,
            alternative_name=rec.alternative.alternative_name,
            is_open_source=rec.alternative.is_open_source,
            feature_match_score=rec.alternative.feature_match_score,
            current_annual_cost=rec.current_annual_cost,
            projected_annual_cost=rec.projected_annual_cost,
            annual_savings=rec.annual_savings,
            migration_cost=rec.migration_cost,
            roi_percent=rec.roi_percent,
            payback_months=rec.payback_months,
            rationale=rec.rationale,
        )
        for rec in report.recommendations
    ]
    return AnalysisReportDetail(
        id=report.id,
        total_current_annual_cost=report.total_current_annual_cost,
        total_estimated_annual_savings=report.total_estimated_annual_savings,
        total_migration_cost=report.total_migration_cost,
        global_roi_percent=report.global_roi_percent,
        payback_months=report.payback_months,
        recommendation_count=len(recs),
        created_at=report.created_at,
        recommendations=recs,
    )


@router.post("/run", response_model=AnalysisReportDetail, status_code=status.HTTP_201_CREATED)
def run_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisReportDetail:
    """Lance le moteur ROI sur le parc courant et enregistre un nouveau rapport d'analyse."""
    item_count = db.scalar(
        select(func.count(SoftwareItem.id)).where(SoftwareItem.user_id == current_user.id)
    ) or 0
    if item_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ajoutez ou importez au moins un logiciel avant de lancer l'analyse",
        )

    report = generate_analysis_report(db, current_user)
    # Précharge les relations (logiciel & alternative) en 2 requêtes pour éviter les requêtes N+1
    loaded = db.scalar(
        select(AnalysisReport)
        .options(
            selectinload(AnalysisReport.recommendations).selectinload(Recommendation.software_item),
            selectinload(AnalysisReport.recommendations).selectinload(Recommendation.alternative),
        )
        .where(AnalysisReport.id == report.id)
    )
    return _serialize_report_detail(loaded)


@router.get("/reports", response_model=list[AnalysisReportSummary])
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisReportSummary]:
    """Retourne l'historique des rapports générés par l'utilisateur (du plus récent au plus ancien)."""
    reports = list(
        db.scalars(
            select(AnalysisReport)
            .options(selectinload(AnalysisReport.recommendations))
            .where(AnalysisReport.user_id == current_user.id)
            .order_by(AnalysisReport.id.desc())
        )
    )
    return [_serialize_report_summary(r) for r in reports]


@router.get("/reports/{report_id}", response_model=AnalysisReportDetail)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisReportDetail:
    """Récupère le détail complet d'un rapport appartenant à l'utilisateur connecté."""
    report = db.scalar(
        select(AnalysisReport)
        .options(
            selectinload(AnalysisReport.recommendations).selectinload(Recommendation.software_item),
            selectinload(AnalysisReport.recommendations).selectinload(Recommendation.alternative),
        )
        .where(AnalysisReport.id == report_id, AnalysisReport.user_id == current_user.id)
    )
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rapport introuvable")
    return _serialize_report_detail(report)
