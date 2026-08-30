"""
Lightweight local keyword/synonym system for business-type semantic matching.
No external paid API required — pure Python.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

BUSINESS_SYNONYMS: Dict[str, List[str]] = {
    "tailoring": [
        "tailoring", "tailor", "sewing", "stitching", "garment", "garments",
        "apparel", "textile", "textiles", "handloom", "handicraft",
        "sewing machine", "boutique", "embroidery",
    ],
    "food": [
        "food", "restaurant", "catering", "food processing", "bakery",
        "sweet shop", "snacks", "tiffin", "canteen", "dhaba", "hotel",
        "food stall", "street food",
    ],
    "retail": [
        "retail", "shop", "shopkeeper", "kirana", "general store",
        "grocery", "vending", "petty shop", "trading", "trade", "vyapar",
    ],
    "agriculture": [
        "agriculture", "farming", "farmer", "crop", "cultivation",
        "horticulture", "agri", "agro", "irrigation", "seeds",
    ],
    "dairy": ["dairy", "milk", "cattle", "livestock", "animal husbandry"],
    "poultry": ["poultry", "chicken farming", "egg production", "hatchery"],
    "fisheries": ["fisheries", "fishing", "fishermen", "aquaculture", "fish farming"],
    "transport": [
        "transport", "taxi", "cab", "logistics", "delivery", "trucking",
        "goods carrier",
    ],
    "auto": [
        "auto", "auto rickshaw", "automobile", "vehicle repair",
        "garage", "workshop", "spare parts",
    ],
    "beauty": [
        "beauty", "salon", "parlour", "parlor", "cosmetics", "spa",
        "hairdressing",
    ],
    "carpentry": ["carpentry", "carpenter", "woodwork", "furniture making"],
    "welding": ["welding", "welder", "fabrication", "metal work"],
    "electrical": ["electrical", "electrician", "wiring", "appliance repair"],
    "mobile_repair": ["mobile repair", "phone repair", "mobile service centre"],
    "computer_it": [
        "computer", "it", "software", "information technology",
        "computer training", "computer centre", "web development",
    ],
    "manufacturing": [
        "manufacturing", "manufacture", "factory", "production unit",
        "small scale industry", "msme", "micro enterprise",
    ],
    "handicraft": ["handicraft", "handicrafts", "artisan", "craft", "pottery", "weaving"],
}

# Reverse index: keyword -> canonical business category
_KEYWORD_INDEX: Dict[str, str] = {}
for canonical, keywords in BUSINESS_SYNONYMS.items():
    for kw in keywords:
        _KEYWORD_INDEX[kw] = canonical


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def normalize_business(raw: Optional[str]) -> Optional[str]:
    """Map a free-text business description to a canonical category key."""
    if not raw:
        return None
    text = _clean(str(raw))
    # exact / substring match against known keywords (longest first)
    for kw in sorted(_KEYWORD_INDEX.keys(), key=len, reverse=True):
        if kw in text:
            return _KEYWORD_INDEX[kw]
    return None


def get_related_keywords(canonical_or_raw: Optional[str]) -> Set[str]:
    """Return the full synonym set for a business (for building match text)."""
    if not canonical_or_raw:
        return set()
    canonical = normalize_business(canonical_or_raw) or _clean(canonical_or_raw)
    return set(BUSINESS_SYNONYMS.get(canonical, [canonical_or_raw.strip().lower()]))


def business_matches(user_business: Optional[str], scheme_text: str) -> bool:
    """
    Returns True if the user's business semantically matches text describing
    a scheme (category + name + description + eligibility_text combined).
    """
    if not user_business:
        return False
    scheme_text_l = _clean(scheme_text)
    keywords = get_related_keywords(user_business)
    return any(kw in scheme_text_l for kw in keywords)
