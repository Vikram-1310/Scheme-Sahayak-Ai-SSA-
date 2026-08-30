"""
Purpose normalization and matching (e.g. "STARTING A BUSINESS" vs a scheme's
"Business & Entrepreneurship" category).
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

PURPOSE_SYNONYMS: Dict[str, List[str]] = {
    "starting_business": [
        "starting a business", "start a business", "new business",
        "self employment", "self-employment", "entrepreneurship",
        "entrepreneur", "enterprise", "micro enterprise", "startup",
        "start-up", "income generation", "business & entrepreneurship",
        "business and entrepreneurship", "livelihood",
    ],
    "business_expansion": [
        "business expansion", "expand business", "scale up",
        "working capital", "modernisation", "modernization",
    ],
    "education": [
        "education", "scholarship", "tuition", "school fees",
        "college fees", "student", "higher education", "skill training",
        "vocational training", "skill development",
    ],
    "housing": [
        "housing", "house construction", "home loan", "shelter",
        "pucca house", "awas",
    ],
    "agriculture": [
        "agriculture", "farming", "crop loan", "irrigation", "kisan",
    ],
    "employment": [
        "employment", "job", "wage employment", "rojgar", "swarojgar",
    ],
}

_KEYWORD_INDEX: Dict[str, str] = {}
for canonical, keywords in PURPOSE_SYNONYMS.items():
    for kw in keywords:
        _KEYWORD_INDEX[kw] = canonical


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def normalize_purpose(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    text = _clean(str(raw))
    for kw in sorted(_KEYWORD_INDEX.keys(), key=len, reverse=True):
        if kw in text:
            return _KEYWORD_INDEX[kw]
    return None


def get_related_keywords(canonical_or_raw: Optional[str]) -> Set[str]:
    if not canonical_or_raw:
        return set()
    canonical = normalize_purpose(canonical_or_raw) or _clean(canonical_or_raw)
    return set(PURPOSE_SYNONYMS.get(canonical, [canonical_or_raw.strip().lower()]))


def purpose_matches(user_purpose: Optional[str], scheme_text: str) -> bool:
    if not user_purpose:
        return False
    scheme_text_l = _clean(scheme_text)
    keywords = get_related_keywords(user_purpose)
    return any(kw in scheme_text_l for kw in keywords)
