"""
State normalization for Indian states/UTs, including city -> state inference.

Design goals:
- Accept messy input: "AP", "ap", "Andhra Pradesh", "Vijayawada, Andhra Pradesh"
- Infer state from a known city name if no state is directly recognized
- Treat "Central" / "India" / "" / "All India" as a central-scheme marker,
  not a specific state
"""

from __future__ import annotations

import json
import re
from typing import Optional, List


def _parse_string_list(raw) -> List[str]:
    """
    Parse a field that may be stored as a JSON-style array string
    (e.g. '["Puducherry"]', '["All"]', '[]') into a plain list of strings.
    Falls back to comma-splitting if it isn't valid JSON.
    """
    if raw is None:
        return []
    text = str(raw).strip()
    if not text or text.lower() in ("nan", "none", "n/a", "-", "[]"):
        return []
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (json.JSONDecodeError, TypeError):
            inner = text[1:-1]
            parts = re.split(r",", inner)
            cleaned = [p.strip().strip('"').strip("'") for p in parts]
            return [p for p in cleaned if p]
    return [text]

# Canonical state/UT names
CANONICAL_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal",
    # UTs
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]

# Common abbreviations / alternate spellings -> canonical
STATE_ALIASES = {
    "ap": "Andhra Pradesh",
    "andhra": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",
    "ar": "Arunachal Pradesh",
    "arunachal": "Arunachal Pradesh",
    "as": "Assam",
    "br": "Bihar",
    "cg": "Chhattisgarh",
    "chattisgarh": "Chhattisgarh",
    "chhattisgarh": "Chhattisgarh",
    "ga": "Goa",
    "gj": "Gujarat",
    "hr": "Haryana",
    "hp": "Himachal Pradesh",
    "jh": "Jharkhand",
    "jharkand": "Jharkhand",
    "ka": "Karnataka",
    "kar": "Karnataka",
    "kl": "Kerala",
    "mp": "Madhya Pradesh",
    "mh": "Maharashtra",
    "maharastra": "Maharashtra",
    "mn": "Manipur",
    "ml": "Meghalaya",
    "mz": "Mizoram",
    "nl": "Nagaland",
    "or": "Odisha",
    "odisa": "Odisha",
    "orissa": "Odisha",
    "pb": "Punjab",
    "rj": "Rajasthan",
    "sk": "Sikkim",
    "tn": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "ts": "Telangana",
    "tg": "Telangana",
    "telengana": "Telangana",
    "tr": "Tripura",
    "up": "Uttar Pradesh",
    "uttarpradesh": "Uttar Pradesh",
    "uk": "Uttarakhand",
    "ua": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "wb": "West Bengal",
    "westbengal": "West Bengal",
    # UTs
    "an": "Andaman and Nicobar Islands",
    "andaman and nicobar": "Andaman and Nicobar Islands",
    "ch": "Chandigarh",
    "dnhdd": "Dadra and Nagar Haveli and Daman and Diu",
    "dn": "Dadra and Nagar Haveli and Daman and Diu",
    "dd": "Dadra and Nagar Haveli and Daman and Diu",
    "dl": "Delhi",
    "delhi ncr": "Delhi",
    "new delhi": "Delhi",
    "jk": "Jammu and Kashmir",
    "j&k": "Jammu and Kashmir",
    "jammu and kashmir": "Jammu and Kashmir",
    "la": "Ladakh",
    "ld": "Lakshadweep",
    "py": "Puducherry",
    "pondicherry": "Puducherry",
}

# Markers that mean "not a specific state" (central / nationwide scheme)
CENTRAL_MARKERS = {
    "", "central", "centre", "center", "national", "all india", "india",
    "pan india", "all-india", "govt of india", "government of india", "nan",
    "none",
}

# Minimal but useful city -> state mapping (extend as needed)
CITY_TO_STATE = {
    "vijayawada": "Andhra Pradesh",
    "visakhapatnam": "Andhra Pradesh",
    "vizag": "Andhra Pradesh",
    "guntur": "Andhra Pradesh",
    "tirupati": "Andhra Pradesh",
    "nellore": "Andhra Pradesh",
    "kurnool": "Andhra Pradesh",
    "rajahmundry": "Andhra Pradesh",
    "kadapa": "Andhra Pradesh",
    "hyderabad": "Telangana",
    "warangal": "Telangana",
    "nizamabad": "Telangana",
    "chennai": "Tamil Nadu",
    "coimbatore": "Tamil Nadu",
    "madurai": "Tamil Nadu",
    "trichy": "Tamil Nadu",
    "bangalore": "Karnataka",
    "bengaluru": "Karnataka",
    "mysore": "Karnataka",
    "mysuru": "Karnataka",
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "nagpur": "Maharashtra",
    "nashik": "Maharashtra",
    "kolkata": "West Bengal",
    "howrah": "West Bengal",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "jaipur": "Rajasthan",
    "jodhpur": "Rajasthan",
    "udaipur": "Rajasthan",
    "lucknow": "Uttar Pradesh",
    "kanpur": "Uttar Pradesh",
    "varanasi": "Uttar Pradesh",
    "agra": "Uttar Pradesh",
    "noida": "Uttar Pradesh",
    "ghaziabad": "Uttar Pradesh",
    "patna": "Bihar",
    "gaya": "Bihar",
    "bhopal": "Madhya Pradesh",
    "indore": "Madhya Pradesh",
    "gwalior": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh",
    "ahmedabad": "Gujarat",
    "surat": "Gujarat",
    "vadodara": "Gujarat",
    "rajkot": "Gujarat",
    "chandigarh": "Chandigarh",
    "kochi": "Kerala",
    "cochin": "Kerala",
    "thiruvananthapuram": "Kerala",
    "trivandrum": "Kerala",
    "kozhikode": "Kerala",
    "bhubaneswar": "Odisha",
    "cuttack": "Odisha",
    "ranchi": "Jharkhand",
    "jamshedpur": "Jharkhand",
    "raipur": "Chhattisgarh",
    "guwahati": "Assam",
    "shimla": "Himachal Pradesh",
    "dehradun": "Uttarakhand",
    "panaji": "Goa",
    "amritsar": "Punjab",
    "ludhiana": "Punjab",
    "srinagar": "Jammu and Kashmir",
    "jammu": "Jammu and Kashmir",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "gurgaon": "Haryana",
    "gurugram": "Haryana",
    "faridabad": "Haryana",
}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def normalize_state(raw: Optional[str]) -> Optional[str]:
    """
    Normalize a raw state/location string to a canonical state name.
    Returns None if it clearly indicates a central/nationwide scheme
    or the input is empty/unrecognizable.
    """
    if raw is None:
        return None
    text = _clean(str(raw))
    if text in CENTRAL_MARKERS:
        return None

    # Direct canonical match
    for state in CANONICAL_STATES:
        if text == state.lower():
            return state

    # Alias match
    if text in STATE_ALIASES:
        return STATE_ALIASES[text]

    # "City, State" or "City - State" patterns
    parts = re.split(r"[,\-/]", text)
    parts = [p.strip() for p in parts if p.strip()]
    for part in reversed(parts):  # state usually comes last
        if part in STATE_ALIASES:
            return STATE_ALIASES[part]
        for state in CANONICAL_STATES:
            if part == state.lower():
                return state

    # City lookup (handles "Vijayawada", "Vijayawada, Andhra Pradesh" already
    # covered above, but also bare city names)
    for part in parts or [text]:
        if part in CITY_TO_STATE:
            return CITY_TO_STATE[part]

    # Fuzzy contains-city check as last resort
    for city, state in CITY_TO_STATE.items():
        if city in text:
            return state

    return None


def normalize_states_list(raw: Optional[str]) -> List[str]:
    """
    Handles CSV cells stored as JSON-array strings (e.g. '["Puducherry"]',
    '["All"]') as well as plain comma-separated text. Returns a
    de-duplicated list of canonical states found; empty list means
    "no specific state restriction" (i.e. central/unrestricted) — this
    includes the case where the value is explicitly "All"/"All India".
    """
    if not raw:
        return []
    items = _parse_string_list(raw)
    result = []
    for item in items:
        if item.strip().lower() in ("all", "all india", "pan india"):
            continue  # "All" means unrestricted, not a specific state
        state = normalize_state(item)
        if state and state not in result:
            result.append(state)
    return result


def infer_state_from_location(location: Optional[str]) -> Optional[str]:
    """Convenience wrapper used for user-supplied free-text location."""
    return normalize_state(location)
