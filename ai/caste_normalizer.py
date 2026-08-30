"""
Caste/category normalization.

Priority order when normalizing a scheme's caste eligibility:
1. Explicit structured field (eligibility_caste column)
2. eligibility_text (only clear, explicit mentions, not substring noise)

We deliberately do NOT treat "SC" as present just because the substring
"sc" appears somewhere in a long text (e.g. "scheme", "discretion", etc).
"""

from __future__ import annotations

import json
import re
from typing import List, Optional


def _parse_string_list(raw: Optional[str]) -> List[str]:
    """
    Parse a field that may be stored as a JSON-style array string
    (e.g. '["SC","ST"]', '["All"]', '[]') into a plain list of strings.
    Falls back to comma-splitting if it isn't valid JSON.
    Returns [] for empty/unparseable input.
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
            # Fall back to stripping brackets/quotes and splitting on commas
            inner = text[1:-1]
            parts = re.split(r",", inner)
            cleaned = [p.strip().strip('"').strip("'") for p in parts]
            return [p for p in cleaned if p]
    # Not bracketed — treat as a plain delimited string
    parts = re.split(r"[,/;&+]| and ", text)
    return [p.strip() for p in parts if p.strip()]

CASTE_MAP = {
    "sc": "SC",
    "s.c": "SC",
    "s.c.": "SC",
    "scheduled caste": "SC",
    "scheduled castes": "SC",
    "st": "ST",
    "s.t": "ST",
    "scheduled tribe": "ST",
    "scheduled tribes": "ST",
    "obc": "OBC",
    "o.b.c": "OBC",
    "other backward class": "OBC",
    "other backward classes": "OBC",
    "ews": "EWS",
    "economically weaker section": "EWS",
    "economically weaker sections": "EWS",
    "general": "GENERAL",
    "gen": "GENERAL",
    "unreserved": "GENERAL",
    "all": "ALL",
    "all categories": "ALL",
    "any": "ALL",
    "open": "ALL",
    "minority": "MINORITY",
    "minorities": "MINORITY",
}

# Word-boundary regex per token, so "sc" only matches as a standalone token
# (e.g. "SC", "SC/ST"), never inside "scheme" or "discretion".
_TOKEN_RE = re.compile(r"[a-z]+(?:\.[a-z]+)*")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def normalize_caste_field(raw: Optional[str]) -> List[str]:
    """
    Normalize an explicit eligibility_caste field (may contain
    "SC", "SC/ST", "SC, ST, OBC", "Scheduled Caste", "All", etc.)
    into a list of canonical codes, e.g. ["SC", "ST"].

    Empty list means "not specified" (unknown, not "General only").
    """
    if not raw:
        return []

    items = _parse_string_list(raw)
    if not items:
        return []

    found: List[str] = []
    for item in items:
        lowered = item.strip().lower().strip(".")
        if not lowered:
            continue
        # Direct exact match against known tokens/phrases
        if lowered in CASTE_MAP:
            code = CASTE_MAP[lowered]
            if code not in found:
                found.append(code)
            continue
        # Phrase contained within a longer item (rare, but safe)
        for phrase in sorted(CASTE_MAP.keys(), key=len, reverse=True):
            if phrase in lowered:
                code = CASTE_MAP[phrase]
                if code not in found:
                    found.append(code)
                break

    if "ALL" in found:
        return ["ALL"]

    return found


def normalize_caste_text_fallback(eligibility_text: Optional[str]) -> List[str]:
    """
    Weaker fallback: look for explicit, standalone caste tokens in free text.
    Only used when the structured field is empty. Requires standalone tokens
    (via tokenizer) so "sc" won't match inside other words.
    """
    if not eligibility_text:
        return []
    tokens = set(_tokenize(str(eligibility_text)))
    found = []
    for token in ("sc", "st", "obc", "ews", "general"):
        if token in tokens:
            code = CASTE_MAP[token]
            if code not in found:
                found.append(code)
    return found


def normalize_caste(
    eligibility_caste_field: Optional[str],
    eligibility_text: Optional[str] = None,
) -> List[str]:
    """
    Full normalization pipeline: explicit field first, then text fallback.
    Returns [] if truly unspecified (meaning: unrestricted/unknown).
    """
    explicit = normalize_caste_field(eligibility_caste_field)
    if explicit:
        return explicit
    return normalize_caste_text_fallback(eligibility_text)


def user_caste_is_allowed(user_caste: Optional[str], scheme_castes: List[str]) -> Optional[bool]:
    """
    Returns:
        True  -> explicitly allowed
        False -> explicitly excluded (hard exclusion)
        None  -> unknown / not specified (treat as compatible, not a failure)
    """
    if not scheme_castes or "ALL" in scheme_castes:
        return None  # no restriction -> unknown/unrestricted, not a failure
    if not user_caste:
        return None  # we don't know the user's caste; can't exclude
    user_code = CASTE_MAP.get(user_caste.strip().lower(), user_caste.strip().upper())
    if user_code in scheme_castes:
        return True
    # Explicit contradiction: scheme restricted to other specific caste(s)
    return False
