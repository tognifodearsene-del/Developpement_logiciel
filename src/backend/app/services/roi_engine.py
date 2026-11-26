"""Moteur métier de calcul de coûts, détection de sous-utilisation et calcul de ROI."""

from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AlternativeCatalog, AnalysisReport, Recommendation, SoftwareItem, User


# Seuil en dessous duquel un logiciel est signalé comme sous-utilisé (< 70% de licences actives)
UNDERUTILIZATION_THRESHOLD = 70.0


@dataclass(frozen=True)
class ComputedRecommendation:
    """Résultat intermédiaire avant persistance en base d'une recommandation chiffrée."""

    software_item: SoftwareItem
    alternative: AlternativeCatalog
    current_annual_cost: float
    projected_annual_cost: float
    annual_savings: float
    migration_cost: float
    roi_percent: float | None
    payback_months: float | None
    rationale: str


def compute_item_metrics(
    monthly_cost_total: float, licenses_purchased: int, licenses_used: int
) -> tuple[float, float, bool]:
    """Calcule (coût_annuel, taux_utilisation_%, est_sous_utilisé) pour un logiciel du parc."""
    annual_cost = round(monthly_cost_total * 12.0, 2)
    utilization_rate = round((licenses_used / licenses_purchased) * 100.0, 2) if licenses_purchased else 0.0
    is_underutilized = utilization_rate < UNDERUTILIZATION_THRESHOLD
    return annual_cost, utilization_rate, is_underutilized


def compute_recommendation_metrics(
    item: SoftwareItem, alt: AlternativeCatalog
) -> ComputedRecommendation | None:
    """Évalue les économies, le ROI sur 12 mois et le payback pour un couple logiciel/alternative."""
    current_annual_cost, utilization_rate, is_underutilized = compute_item_metrics(
        item.monthly_cost_total, item.licenses_purchased, item.licenses_used
    )
    # Dimensionnement au plus juste : on ne projette que le nombre de licences réellement utilisées
    projected_annual_cost = round(alt.estimated_monthly_cost_per_user * item.licenses_used * 12.0, 2)
    annual_savings = round(current_annual_cost - projected_annual_cost, 2)
    # On écarte toute alternative qui ne génère pas d'économie annuelle nette positive
    if annual_savings <= 0:
        return None

    migration_cost = round(alt.estimated_migration_cost, 2)
    if migration_cost > 0:
        roi_percent = round(((annual_savings - migration_cost) / migration_cost) * 100.0, 2)
        payback_months = round(migration_cost / (annual_savings / 12.0), 2)
    else:
        # Si le coût de transition est nul, le gain est immédiat (division par zéro évitée)
        roi_percent = None
        payback_months = 0.0

    usage_note = (
        f"Sous-utilisation détectée ({utilization_rate:.0f}% : {item.licenses_used}/{item.licenses_purchased} licences actives). "
        if is_underutilized
        else f"Taux d'utilisation de {utilization_rate:.0f}% ({item.licenses_used}/{item.licenses_purchased} licences actives). "
    )
    rationale = (
        f"{usage_note}Le passage vers {alt.alternative_name} permet une économie estimée de "
        f"{annual_savings:.2f} EUR/an (adéquation fonctionnelle {alt.feature_match_score}%)."
    )

    return ComputedRecommendation(
        software_item=item,
        alternative=alt,
        current_annual_cost=current_annual_cost,
        projected_annual_cost=projected_annual_cost,
        annual_savings=annual_savings,
        migration_cost=migration_cost,
        roi_percent=roi_percent,
        payback_months=payback_months,
        rationale=rationale,
    )


def _match_candidates(item: SoftwareItem, catalog: list[AlternativeCatalog]) -> list[AlternativeCatalog]:
    """Recherche prioritairement le nom exact du logiciel, puis se rabat sur sa catégorie."""
    target_norm = item.name.strip().lower()
    exact = [alt for alt in catalog if alt.target_software.strip().lower() == target_norm]
    if exact:
        return exact

    cat_norm = item.category.strip().lower()
    return [alt for alt in catalog if alt.category.strip().lower() == cat_norm]


def _score_key(rec: ComputedRecommendation) -> tuple[float, int]:
    """Clé de tri : privilégie le gain net sur 1 an, puis le score de couverture fonctionnelle."""
    net_year_one = rec.annual_savings - rec.migration_cost
    return (net_year_one, rec.alternative.feature_match_score)


def generate_analysis_report(db: Session, user: User) -> AnalysisReport:
    """Analyse tout le parc d'un client, classe les recommandations et persiste le rapport."""
    items = list(
        db.scalars(select(SoftwareItem).where(SoftwareItem.user_id == user.id).order_by(SoftwareItem.id))
    )
    catalog = list(db.scalars(select(AlternativeCatalog)))

    total_current_annual_cost = round(sum(item.monthly_cost_total * 12.0 for item in items), 2)

    primary: list[ComputedRecommendation] = []
    secondary: list[ComputedRecommendation] = []

    for item in items:
        candidates = _match_candidates(item, catalog)
        computed = [
            rec for alt in candidates if (rec := compute_recommendation_metrics(item, alt)) is not None
        ]
        if not computed:
            continue
        computed.sort(key=_score_key, reverse=True)
        # On retient la meilleure alternative par logiciel pour les totaux financiers
        primary.append(computed[0])
        secondary.extend(computed[1:])

    primary.sort(key=_score_key, reverse=True)
    selected = list(primary)

    # Si l'inventaire est petit (< 3 logiciels), on complète avec des alternatives secondaires
    # afin de respecter le critère V1 : proposer au moins 3 recommandations exploitables
    if len(selected) < 3 and secondary:
        secondary.sort(key=_score_key, reverse=True)
        needed = 3 - len(selected)
        selected.extend(secondary[:needed])

    # Les KPI agrégés ne comptent qu'une recommandation principale par logiciel (pas de double comptage)
    total_annual_savings = round(sum(rec.annual_savings for rec in primary), 2)
    total_migration_cost = round(sum(rec.migration_cost for rec in primary), 2)

    if total_migration_cost > 0:
        global_roi_percent = round(
            ((total_annual_savings - total_migration_cost) / total_migration_cost) * 100.0, 2
        )
        payback_months = (
            round(total_migration_cost / (total_annual_savings / 12.0), 2)
            if total_annual_savings > 0
            else None
        )
    else:
        global_roi_percent = None
        payback_months = 0.0 if total_annual_savings > 0 else None

    report = AnalysisReport(
        user_id=user.id,
        total_current_annual_cost=total_current_annual_cost,
        total_estimated_annual_savings=total_annual_savings,
        total_migration_cost=total_migration_cost,
        global_roi_percent=global_roi_percent,
        payback_months=payback_months,
    )
    db.add(report)
    db.flush()

    for rank, rec in enumerate(selected, start=1):
        db.add(
            Recommendation(
                report_id=report.id,
                software_item_id=rec.software_item.id,
                alternative_id=rec.alternative.id,
                priority_rank=rank,
                current_annual_cost=rec.current_annual_cost,
                projected_annual_cost=rec.projected_annual_cost,
                annual_savings=rec.annual_savings,
                migration_cost=rec.migration_cost,
                roi_percent=rec.roi_percent,
                payback_months=rec.payback_months,
                rationale=rec.rationale,
            )
        )

    db.commit()
    db.refresh(report)
    return report
