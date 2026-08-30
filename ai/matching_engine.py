"""
Match-scoring engine: computes a relevance score and level for a
(user, scheme) pair, used to rank recommendations.

match_level semantics:
    EXCLUDED -> explicit hard contradiction (e.g. caste or state mismatch);
                never recommended regardless of score
    HIGH / MEDIUM / LOW -> relative ranking based on accumulated score
"""

from __future__ import annotations

from typing import List

from ai.scheme_models import UserProfile, Scheme, SchemeMatch
from ai.caste_normalizer import user_caste_is_allowed
from ai.state_normalizer import normalize_state
from ai.business_normalizer import business_matches
from ai.purpose_normalizer import purpose_matches

HIGH_THRESHOLD = 60
MEDIUM_THRESHOLD = 30


def _scheme_text(scheme: Scheme) -> str:
    return " ".join(
        filter(
            None,
            [
                scheme.scheme_name,
                scheme.description,
                " ".join(scheme.category),
                " ".join(scheme.benefits),
                scheme.eligibility_text_raw,
            ],
        )
    )


def _excluded(scheme: Scheme, unmatched: List[str]) -> SchemeMatch:
    return SchemeMatch(
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        score=0,
        match_level="EXCLUDED",
        matched_conditions=[],
        unmatched_conditions=unmatched,
        warnings=[],
    )


def match_score(user: UserProfile, scheme: Scheme) -> SchemeMatch:
    elig = scheme.eligibility

    matched: List[str] = []
    unmatched: List[str] = []
    warnings: List[str] = []
    score = 0

    # Hard exclusion: explicit caste contradiction
    caste_ok = user_caste_is_allowed(user.category, elig.caste_allowed)
    if caste_ok is False:
        return _excluded(
            scheme, ["Category does not match scheme's allowed categories."]
        )
    if caste_ok is True:
        score += 25
        matched.append("Category matches scheme's allowed categories.")

    # Hard exclusion: explicit state contradiction
    if elig.is_central:
        score += 15
        matched.append("Central scheme — available nationwide.")
    else:
        allowed_states = elig.states_allowed or (
            [scheme.state] if scheme.state else []
        )
        if allowed_states:
            if user.location:
                user_state = normalize_state(user.location) or user.location
                if user_state not in allowed_states:
                    return _excluded(
                        scheme,
                        ["State does not match scheme's applicable states."],
                    )
                score += 15
                matched.append("State matches scheme's applicable states.")
            else:
                unmatched.append(
                    "Location not provided; scheme is state-restricted."
                )

    # Income
    if elig.income_limit is not None:
        if user.annual_income is not None:
            if user.annual_income <= elig.income_limit:
                score += 20
                matched.append("Income within scheme's limit.")
            else:
                unmatched.append("Income exceeds scheme's limit.")
        else:
            unmatched.append(
                "Income limit specified but user's income is unknown."
            )
    else:
        score += 10
        matched.append("No specific income limit for this scheme.")

    # Age
    if elig.age_min is not None or elig.age_max is not None:
        if user.age is not None:
            within_min = elig.age_min is None or user.age >= elig.age_min
            within_max = elig.age_max is None or user.age <= elig.age_max
            if within_min and within_max:
                score += 10
                matched.append("Age within scheme's allowed range.")
            else:
                unmatched.append("Age outside scheme's allowed range.")
        else:
            unmatched.append(
                "Age requirement specified but user's age is unknown."
            )

    # Business / purpose semantic match against scheme text
    text = _scheme_text(scheme)
    if business_matches(user.business, text):
        score += 15
        matched.append("Business type matches scheme's focus area.")
    if purpose_matches(user.purpose, text):
        score += 15
        matched.append("Purpose matches scheme's intent.")

    if elig.disability_related:
        warnings.append(
            "This scheme is specifically intended for persons with disabilities."
        )

    if score >= HIGH_THRESHOLD:
        level = "HIGH"
    elif score >= MEDIUM_THRESHOLD:
        level = "MEDIUM"
    else:
        level = "LOW"

    return SchemeMatch(
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        score=score,
        match_level=level,
        matched_conditions=matched,
        unmatched_conditions=unmatched,
        warnings=warnings,
    )
