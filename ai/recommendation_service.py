"""
High-level service layer used by both the FastAPI endpoints and (optionally)
the AI chat engine. Wraps the scheme source + recommender + missing-info
detection into one convenient call.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ai.scheme_models import UserProfile
from ai.scheme_source import get_scheme_source
from ai.scheme_recommender import recommend, get_missing_information_for_top_candidates

REQUIRED_FIELDS_PRIORITY = ["location", "annual_income", "business", "loan_required"]


def build_missing_field_questions(user: UserProfile, missing_fields: List[str]) -> List[str]:
    prompts = {
        "location": "Which state or city are you located in?",
        "annual_income": "What is your annual family income?",
        "business": "What type of business are you running or planning?",
        "loan_required": "How much loan amount do you require?",
        "age": "What is your age?",
        "occupation": "What is your current occupation?",
        "category": "What is your caste category (SC/ST/OBC/General)?",
    }
    ordered = [f for f in REQUIRED_FIELDS_PRIORITY if f in missing_fields]
    ordered += [f for f in missing_fields if f not in ordered]
    return [prompts.get(f, f"Please provide: {f}") for f in ordered]


def get_recommendations(user: UserProfile, top_n: int = 10) -> Dict[str, Any]:
    source = get_scheme_source()
    all_schemes = source.all()

    recommendations = recommend(user, all_schemes, top_n=top_n)

    missing_fields = get_missing_information_for_top_candidates(user, all_schemes)
    missing_questions = build_missing_field_questions(user, missing_fields)

    return {
        "status": "success",
        "profile": user.model_dump(),
        "total_schemes_considered": len(all_schemes),
        "recommendations": recommendations,
        "missing_information": missing_fields,
        "follow_up_questions": missing_questions,
    }


def search_schemes(
    category: Optional[str] = None,
    state: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    source = get_scheme_source()
    results = source.all()

    if category:
        cat_ids = {s.scheme_id for s in source.by_category(category)}
        results = [s for s in results if s.scheme_id in cat_ids]

    if state:
        state_ids = {s.scheme_id for s in source.by_state(state)}
        results = [s for s in results if s.scheme_id in state_ids]

    if keyword:
        kw_ids = {s.scheme_id for s in source.search(keyword)}
        results = [s for s in results if s.scheme_id in kw_ids]

    return {"total": len(results), "schemes": results}


def check_single_scheme_eligibility(user: UserProfile, scheme_id: str) -> Dict[str, Any]:
    from ai.eligibility_engine import check_eligibility

    source = get_scheme_source()
    scheme = source.get(scheme_id)
    if scheme is None:
        return {"status": "error", "message": f"Scheme '{scheme_id}' not found."}

    eligibility = check_eligibility(user, scheme)
    return {
        "status": "success",
        "scheme": scheme,
        "eligibility": eligibility,
    }
