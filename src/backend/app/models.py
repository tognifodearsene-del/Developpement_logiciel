"""SQLAlchemy ORM models matching docs/architecture.md."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """SaaS user account (client or admin)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    company_name: Mapped[str] = mapped_column(String(120), nullable=False, default="PME Demo")
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="client")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    software_items: Mapped[list["SoftwareItem"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    reports: Mapped[list["AnalysisReport"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class SoftwareItem(Base):
    """Software license entry in a user's stack inventory."""

    __tablename__ = "software_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    vendor: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    licenses_purchased: Mapped[int] = mapped_column(Integer, nullable=False)
    licenses_used: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_cost_total: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    owner: Mapped["User"] = relationship(back_populates="software_items")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="software_item", cascade="all, delete-orphan"
    )


class AlternativeCatalog(Base):
    """Reference catalog of lower-cost or open-source software alternatives."""

    __tablename__ = "alternatives_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_software: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    alternative_name: Mapped[str] = mapped_column(String(120), nullable=False)
    vendor_or_license: Mapped[str] = mapped_column(String(120), nullable=False, default="Open Source")
    is_open_source: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    estimated_monthly_cost_per_user: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_migration_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    feature_match_score: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="alternative")


class AnalysisReport(Base):
    """Generated cost & ROI analysis report snapshot."""

    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_current_annual_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_estimated_annual_savings: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_migration_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    global_roi_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    payback_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    owner: Mapped["User"] = relationship(back_populates="reports")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="Recommendation.priority_rank",
    )


class Recommendation(Base):
    """Single software alternative recommendation and ROI calculation inside a report."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_reports.id", ondelete="CASCADE"), nullable=False
    )
    software_item_id: Mapped[int] = mapped_column(
        ForeignKey("software_items.id", ondelete="CASCADE"), nullable=False
    )
    alternative_id: Mapped[int] = mapped_column(
        ForeignKey("alternatives_catalog.id", ondelete="CASCADE"), nullable=False
    )
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    current_annual_cost: Mapped[float] = mapped_column(Float, nullable=False)
    projected_annual_cost: Mapped[float] = mapped_column(Float, nullable=False)
    annual_savings: Mapped[float] = mapped_column(Float, nullable=False)
    migration_cost: Mapped[float] = mapped_column(Float, nullable=False)
    roi_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    payback_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False, default="")

    report: Mapped["AnalysisReport"] = relationship(back_populates="recommendations")
    software_item: Mapped["SoftwareItem"] = relationship(back_populates="recommendations")
    alternative: Mapped["AlternativeCatalog"] = relationship(back_populates="recommendations")
