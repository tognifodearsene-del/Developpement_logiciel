"""Tests unitaires du moteur d'utilisation des licences et de calcul de ROI."""

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import AlternativeCatalog, SoftwareItem, User
from app.services.roi_engine import (
    compute_item_metrics,
    compute_recommendation_metrics,
    generate_analysis_report,
)


def test_compute_item_metrics_underutilized_vs_healthy() -> None:
    """Vérifie le seuil de sous-utilisation (< 70%) et le calcul du coût annuel."""
    annual, util, underutilized = compute_item_metrics(300.0, 30, 14)
    assert annual == 3600.0
    assert util == 46.67
    assert underutilized is True

    annual_ok, util_ok, underutilized_ok = compute_item_metrics(500.0, 20, 18)
    assert annual_ok == 6000.0
    assert util_ok == 90.0
    assert underutilized_ok is False


def test_compute_recommendation_metrics_with_and_without_migration_cost() -> None:
    """Vérifie le calcul ROI/payback avec coût de migration positif et nul."""
    item = SoftwareItem(
        user_id=1,
        name="Power BI Pro",
        category="BI & Analytics",
        vendor="Microsoft",
        licenses_purchased=30,
        licenses_used=14,
        monthly_cost_total=300.0,
    )
    alt = AlternativeCatalog(
        target_software="Power BI Pro",
        category="BI & Analytics",
        alternative_name="Apache Superset",
        is_open_source=True,
        estimated_monthly_cost_per_user=2.0,
        estimated_migration_cost=900.0,
        feature_match_score=88,
    )

    rec = compute_recommendation_metrics(item, alt)
    assert rec is not None
    assert rec.current_annual_cost == 3600.0
    assert rec.projected_annual_cost == 336.0
    assert rec.annual_savings == 3264.0
    assert rec.roi_percent == 262.67
    assert rec.payback_months == 3.31

    # Cas limite : migration gratuite -> roi_percent doit être None (gain immédiat sans division par 0)
    alt_zero_migration = AlternativeCatalog(
        target_software="Power BI Pro",
        category="BI & Analytics",
        alternative_name="FreeTool",
        is_open_source=True,
        estimated_monthly_cost_per_user=0.0,
        estimated_migration_cost=0.0,
        feature_match_score=75,
    )
    rec_zero = compute_recommendation_metrics(item, alt_zero_migration)
    assert rec_zero is not None
    assert rec_zero.roi_percent is None
    assert rec_zero.payback_months == 0.0


def test_generate_analysis_report_produces_at_least_three_recommendations(db_session: Session) -> None:
    """Vérifie qu'un petit parc (2 logiciels) produit bien au moins 3 recommandations classées."""
    user = User(
        email="cto@pme.fr",
        password_hash=hash_password("secret123"),
        full_name="Arsene",
        company_name="PME Test",
    )
    db_session.add(user)
    db_session.flush()

    db_session.add_all(
        [
            SoftwareItem(
                user_id=user.id,
                name="Power BI Pro",
                category="BI & Analytics",
                vendor="Microsoft",
                licenses_purchased=30,
                licenses_used=14,
                monthly_cost_total=300.0,
            ),
            SoftwareItem(
                user_id=user.id,
                name="Jira Software",
                category="Gestion de projet",
                vendor="Atlassian",
                licenses_purchased=40,
                licenses_used=22,
                monthly_cost_total=320.0,
            ),
        ]
    )
    db_session.commit()

    report = generate_analysis_report(db_session, user)

    assert report.total_current_annual_cost == 7440.0
    assert report.total_estimated_annual_savings > 0
    assert report.global_roi_percent is not None
    assert len(report.recommendations) >= 3
    assert [r.priority_rank for r in report.recommendations] == [1, 2, 3]
