"""
Pydantic request/response models for the FastAPI endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from ai.scheme_models import Scheme, EligibilityResult, UserProfile


class RecommendRequest(BaseModel):
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
    top_n: int = 10

    def to_profile(self) -> UserProfile:
        return UserProfile(
            category=self.category,
            location=self.location,
            annual_income=self.annual_income,
            age=self.age,
            education=self.education,
            occupation=self.occupation,
            business=self.business,
            purpose=self.purpose,
            project_cost=self.project_cost,
            loan_required=self.loan_required,
            existing_loan=self.existing_loan,
        )


class RecommendationItem(BaseModel):
    scheme_id: str
    scheme_name: str
    score: int
    match_level: str
    eligibility_status: str
    why_recommended: List[str]
    matched_conditions: List[str]
    unknown_conditions: List[str]
    warnings: List[str]
    benefits: List[str]
    documents_required: List[str]
    application_process: Optional[str] = None
    application_url: Optional[str] = None
    official_source: Optional[str] = None
    missing_information: List[str]
    ministry: Optional[str] = None
    department: Optional[str] = None
    state: Optional[str] = None


class RecommendResponse(BaseModel):
    status: str
    profile: Dict[str, Any]
    total_schemes_considered: int
    recommendations: List[RecommendationItem]
    missing_information: List[str]
    follow_up_questions: List[str]


class SearchResponse(BaseModel):
    total: int
    schemes: List[Scheme]


class EligibilityRequest(BaseModel):
    profile: RecommendRequest
    scheme_id: str


class EligibilityResponse(BaseModel):
    status: str
    scheme: Optional[Scheme] = None
    eligibility: Optional[EligibilityResult] = None
    message: Optional[str] = None
