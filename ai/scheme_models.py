"""
Pydantic models for schemes, user profiles, matches, and eligibility.
Backward compatible with the existing model shapes; new optional fields
were added with safe defaults so nothing that already depends on this
module breaks.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SchemeEligibility(BaseModel):
    income_limit: Optional[int] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None

    categories: List[str] = Field(default_factory=list)
    occupations: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)

    other_conditions: List[str] = Field(default_factory=list)

    # --- new fields (safe defaults; existing code unaffected) ---
    caste_allowed: List[str] = Field(default_factory=list)  # [] = unrestricted/unknown
    states_allowed: List[str] = Field(default_factory=list)  # [] = central/unrestricted
    is_central: bool = False
    gender: Optional[str] = None
    disability_related: bool = False
    bpl_required: Optional[bool] = None
    income_limit_source: Optional[str] = None  # "explicit" | "extracted_estimate" | None


class FinancialDetails(BaseModel):
    minimum_amount: Optional[int] = None
    maximum_amount: Optional[int] = None

    interest_rate: Optional[str] = None
    subsidy: Optional[str] = None
    repayment_period: Optional[str] = None

    # --- new fields ---
    amount_source: Optional[str] = None  # "explicit" | "extracted_estimate" | None


class Scheme(BaseModel):
    scheme_id: str
    scheme_name: str

    government_level: str
    state: Optional[str] = None

    ministry: Optional[str] = None
    department: Optional[str] = None

    category: List[str] = Field(default_factory=list)
    scheme_type: Optional[str] = None

    description: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)

    eligibility: SchemeEligibility = Field(default_factory=SchemeEligibility)
    financial_details: FinancialDetails = Field(default_factory=FinancialDetails)

    documents_required: List[str] = Field(default_factory=list)

    application_process: Optional[str] = None
    application_url: Optional[str] = None

    official_source: Optional[str] = None
    last_verified: Optional[str] = None

    # --- new field: raw eligibility text kept for fallback matching ---
    eligibility_text_raw: Optional[str] = None


class UserProfile(BaseModel):
    category: Optional[str] = None
    location: Optional[str] = None

    annual_income: Optional[int] = None
    age: Optional[int] = None

    education: Optional[str] = None
    occupation: Optional[str] = None
    business: Optional[str] = None

    purpose: Optional[str] = None

    project_cost: Optional[int] = None
    loan_required: Optional[int] = None

    existing_loan: Optional[bool] = None


class SchemeMatch(BaseModel):
    scheme_id: str
    scheme_name: str

    score: int
    match_level: str  # HIGH | MEDIUM | LOW | EXCLUDED

    matched_conditions: List[str] = Field(default_factory=list)
    unmatched_conditions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SchemeSearchRequest(BaseModel):
    category: Optional[str] = None
    state: Optional[str] = None
    keyword: Optional[str] = None


class SchemeSearchResponse(BaseModel):
    total: int
    schemes: List[Scheme]


class EligibilityResult(BaseModel):
    scheme_id: str
    status: str  # ELIGIBLE | NOT_ELIGIBLE | INSUFFICIENT_INFORMATION

    matched_rules: List[str] = Field(default_factory=list)
    failed_rules: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
