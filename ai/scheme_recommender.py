"""
Orchestrates matching_engine + eligibility_engine over the full dataset,
ranks results, and builds explainable recommendation objects.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ai.scheme_models import Scheme, UserProfile
from ai.matching_engine import match_score
from ai.eligibility_engine import check_eligibility


def _build_recommendation(user: UserProfile, scheme: Scheme) -> Dict[str, Any]:
    match = match_score(user, scheme)
    eligibility = check_eligibility(user, scheme)

    return {
        "scheme_id": scheme.scheme_id,
        "scheme_name": scheme.scheme_name,
        "score": match.score,
        "match_level": match.match_level,
        "eligibility_status": eligibility.status,
        "why_recommended": match.matched_conditions,
        "matched_conditions": match.matched_conditions,
        "unknown_conditions": match.unmatched_conditions,
        "warnings": list(dict.fromkeys(match.warnings + eligibility.warnings)),
        "benefits": scheme.benefits,
        "documents_required": scheme.documents_required,
        "application_process": scheme.application_process,
        "application_url": scheme.application_url,
        "official_source": scheme.official_source,
        "missing_information": eligibility.missing_information,
        "ministry": scheme.ministry,
        "department": scheme.department,
        "state": scheme.state,
    }


def recommend(
    user: UserProfile,
    schemes: List[Scheme],
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """
    Filters out hard-excluded schemes (explicit contradictions),
    scores the rest, and returns the top N ranked recommendations.
    NOT_ELIGIBLE items (from eligibility engine) are also excluded from
    the final ranked list, since they represent explicit disqualification;
    everything else (ELIGIBLE / INSUFFICIENT_INFORMATION) is eligible to
    be recommended, ranked by match score.
    """
    candidates = []
    for scheme in schemes:
        rec = _build_recommendation(user, scheme)
        if rec["match_level"] == "EXCLUDED":
            continue
        if rec["eligibility_status"] == "NOT_ELIGIBLE":
            continue
        candidates.append(rec)

    candidates.sort(key=lambda r: r["score"], reverse=True)
    return candidates[:top_n]


def get_missing_information_for_top_candidates(
    user: UserProfile,
    schemes: List[Scheme],
    sample_size: int = 30,
) -> List[str]:
    """
    Look at a broad sample of otherwise-plausible schemes and figure out
    which fields are most commonly missing, so the AI/chat layer can ask
    only relevant follow-up questions (not everything up front).
    """
    from collections import Counter

    counter: Counter = Counter()
    checked = 0
    for scheme in schemes:
        if checked >= sample_size:
            break
        match = match_score(user, scheme)
        if match.match_level == "EXCLUDED":
            continue
        eligibility = check_eligibility(user, scheme)
        for field in eligibility.missing_information:
            counter[field] += 1
        checked += 1

    # Only surface fields that came up meaningfully often
    threshold = max(1, checked // 4)
    return [field for field, count in counter.most_common() if count >= threshold]
