"""Pydantic schemas for request validation and API responses."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Auth & Users ---


class UserRegister(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    company_name: str = Field(default="PME Demo", min_length=1, max_length=120)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    company_name: str
    role: Literal["client", "admin"]
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Inventory ---


class SoftwareItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    vendor: str = Field(default="", max_length=120)
    licenses_purchased: int = Field(ge=1)
    licenses_used: int = Field(ge=0)
    monthly_cost_total: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_license_usage(self) -> "SoftwareItemBase":
        if self.licenses_used > self.licenses_purchased:
            raise ValueError("licenses_used cannot exceed licenses_purchased")
        return self


class SoftwareItemCreate(SoftwareItemBase):
    pass


class SoftwareItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    vendor: str | None = Field(default=None, max_length=120)
    licenses_purchased: int | None = Field(default=None, ge=1)
    licenses_used: int | None = Field(default=None, ge=0)
    monthly_cost_total: float | None = Field(default=None, ge=0.0)


class SoftwareItemResponse(SoftwareItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    annual_cost: float
    utilization_rate: float
    is_underutilized: bool
    created_at: datetime


class InventorySummary(BaseModel):
    items: list[SoftwareItemResponse]
    total_software_count: int
    total_monthly_cost: float
    total_annual_cost: float
    average_utilization_rate: float
    underutilized_count: int


class CsvImportError(BaseModel):
    line: int
    message: str


class CsvImportResponse(BaseModel):
    imported_count: int
    skipped_count: int
    errors: list[CsvImportError]
    items: list[SoftwareItemResponse]


# --- Alternatives ---


class AlternativeCreate(BaseModel):
    target_software: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    alternative_name: str = Field(min_length=1, max_length=120)
    vendor_or_license: str = Field(default="Open Source", max_length=120)
    is_open_source: bool = True
    estimated_monthly_cost_per_user: float = Field(default=0.0, ge=0.0)
    estimated_migration_cost: float = Field(default=0.0, ge=0.0)
    feature_match_score: int = Field(default=80, ge=0, le=100)
    description: str = ""


class AlternativeResponse(AlternativeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Analysis & Reports ---


class RecommendationResponse(BaseModel):
    id: int
    priority_rank: int
    software_item_id: int
    software_name: str
    category: str
    alternative_id: int
    alternative_name: str
    is_open_source: bool
    feature_match_score: int
    current_annual_cost: float
    projected_annual_cost: float
    annual_savings: float
    migration_cost: float
    roi_percent: float | None
    payback_months: float | None
    rationale: str


class AnalysisReportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_current_annual_cost: float
    total_estimated_annual_savings: float
    total_migration_cost: float
    global_roi_percent: float | None
    payback_months: float | None
    recommendation_count: int
    created_at: datetime


class AnalysisReportDetail(AnalysisReportSummary):
    recommendations: list[RecommendationResponse]
