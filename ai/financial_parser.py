"""
Parse financial amounts (income limits, loan/benefit amounts) from
structured fields and, cautiously, from free text.

Anything extracted from free text is marked with source="extracted_estimate"
and must never be presented to the user as a certain/explicit limit.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

_NUMBER_RE = re.compile(
    r"(?:rs\.?|inr|₹)?\s*"
    r"([\d,]+(?:\.\d+)?)\s*"
    r"(lakh|lakhs|lac|lacs|crore|crores|cr)?",
    re.IGNORECASE,
)

_MULTIPLIERS = {
    "lakh": 100_000, "lakhs": 100_000, "lac": 100_000, "lacs": 100_000,
    "crore": 10_000_000, "crores": 10_000_000, "cr": 10_000_000,
}


def parse_amount_to_int(raw) -> Optional[int]:
    """Parse a single explicit numeric field (e.g. eligibility_income_max)."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        try:
            if raw != raw:  # NaN check
                return None
        except Exception:
            pass
        return int(raw)
    text = str(raw).strip()
    if not text or text.lower() in ("nan", "none", "n/a", "-"):
        return None
    match = _NUMBER_RE.search(text)
    if not match:
        return None
    number_str, unit = match.group(1), match.group(2)
    try:
        number = float(number_str.replace(",", ""))
    except ValueError:
        return None
    if unit:
        number *= _MULTIPLIERS.get(unit.lower(), 1)
    return int(number)


def extract_amounts_from_text(text: Optional[str]) -> list:
    """
    Best-effort extraction of rupee amounts mentioned in free text
    (benefits/description/eligibility_text). These are ESTIMATES ONLY.
    """
    if not text:
        return []
    results = []
    for match in _NUMBER_RE.finditer(str(text)):
        number_str, unit = match.group(1), match.group(2)
        if not unit and "," not in number_str and len(number_str) <= 2:
            # Skip tiny bare numbers with no unit/context (too noisy,
            # e.g. "2 documents", "3 years")
            continue
        try:
            number = float(number_str.replace(",", ""))
        except ValueError:
            continue
        if unit:
            number *= _MULTIPLIERS.get(unit.lower(), 1)
        if number >= 1000:  # ignore trivial numbers
            results.append(int(number))
    return results


def evaluate_amount_against_range(
    requested: Optional[int],
    minimum: Optional[int],
    maximum: Optional[int],
) -> Tuple[Optional[bool], str]:
    """
    Returns (result, reason):
        result True  -> explicitly within range
        result False -> explicitly outside range (hard exclusion candidate)
        result None  -> unknown (no usable range/requested info)
    """
    if requested is None:
        return None, "Requested amount not provided by user."
    if minimum is None and maximum is None:
        return None, "Scheme does not specify a financial limit."
    if minimum is not None and maximum is not None:
        if minimum <= requested <= maximum:
            return True, f"Requested amount within scheme range ({minimum}-{maximum})."
        return False, f"Requested amount outside scheme range ({minimum}-{maximum})."
    if maximum is not None:
        if requested <= maximum:
            return True, f"Requested amount within scheme maximum ({maximum})."
        return False, f"Requested amount exceeds scheme maximum ({maximum})."
    if minimum is not None:
        if requested >= minimum:
            return True, f"Requested amount meets scheme minimum ({minimum})."
        return False, f"Requested amount below scheme minimum ({minimum})."
    return None, "Insufficient financial data."
