"""
CSV -> Scheme object importer with normalization.
Preserves the existing contract: loads data/Schemes.csv and reports
"Loaded N schemes with 0 errors" style output.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ai.scheme_models import Scheme, SchemeEligibility, FinancialDetails
from ai.state_normalizer import normalize_state, normalize_states_list
from ai.caste_normalizer import normalize_caste
from ai.financial_parser import parse_amount_to_int, extract_amounts_from_text

logger = logging.getLogger("scheme_importer")

DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "Schemes.csv"


def _clean_str(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, float) and value != value:  # NaN
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "n/a", "-"):
        return None
    return text


def _split_list_field(value) -> List[str]:
    text = _clean_str(value)
    if not text:
        return []
    parts = [p.strip() for p in text.split(",") if p.strip()]
    return parts


def _parse_int(value) -> Optional[int]:
    text = _clean_str(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except (ValueError, TypeError):
        return None


def _parse_bool(value) -> Optional[bool]:
    text = _clean_str(value)
    if text is None:
        return None
    t = text.strip().lower()
    if t in ("yes", "true", "1", "y"):
        return True
    if t in ("no", "false", "0", "n"):
        return False
    return None


def _row_to_scheme(row: pd.Series, index: int) -> Scheme:
    slug = _clean_str(row.get("slug")) or f"scheme-{index}"
    name = _clean_str(row.get("name")) or "Unnamed Scheme"
    description = _clean_str(row.get("description"))
    ministry = _clean_str(row.get("ministry"))
    department = _clean_str(row.get("department"))

    raw_state = _clean_str(row.get("state"))
    normalized_state = normalize_state(raw_state)  # None => central
    government_level = "Central" if normalized_state is None else "State"

    category_list = _split_list_field(row.get("category"))
    benefits_list = _split_list_field(row.get("benefits"))
    documents_list = _split_list_field(row.get("documents_required"))

    eligibility_text = _clean_str(row.get("eligibility_text"))
    application_process = _clean_str(row.get("application_process"))
    apply_url = _clean_str(row.get("apply_url"))
    official_url = _clean_str(row.get("official_url"))

    age_min = _parse_int(row.get("eligibility_age_min"))
    age_max = _parse_int(row.get("eligibility_age_max"))
    gender = _clean_str(row.get("eligibility_gender"))
    caste_raw = row.get("eligibility_caste")
    caste_list = normalize_caste(caste_raw, eligibility_text)

    income_max_raw = row.get("eligibility_income_max")
    income_max_explicit = parse_amount_to_int(income_max_raw)
    income_source = "explicit" if income_max_explicit is not None else None
    if income_max_explicit is None:
        # cautious fallback extraction from free text
        candidates = extract_amounts_from_text(eligibility_text)
        if candidates:
            income_max_explicit = min(candidates)  # conservative guess
            income_source = "extracted_estimate"

    eligibility_residence = _clean_str(row.get("eligibility_residence"))
    eligibility_state_raw = row.get("eligibility_state")
    states_allowed = normalize_states_list(eligibility_state_raw)
    disability = _parse_bool(row.get("eligibility_disability"))
    bpl = _parse_bool(row.get("eligibility_bpl"))

    is_central = government_level == "Central" and not states_allowed

    # Try to extract loan/benefit min-max amounts from benefits/description
    combined_financial_text = " ".join(
        t for t in [benefits_list and " ".join(benefits_list), description, eligibility_text]
        if t
    )
    extracted_amounts = extract_amounts_from_text(combined_financial_text)
    min_amount = min(extracted_amounts) if extracted_amounts else None
    max_amount = max(extracted_amounts) if extracted_amounts else None
    amount_source = "extracted_estimate" if extracted_amounts else None

    eligibility = SchemeEligibility(
        income_limit=income_max_explicit,
        age_min=age_min,
        age_max=age_max,
        categories=category_list,
        occupations=[],
        locations=[normalized_state] if normalized_state else [],
        other_conditions=[eligibility_residence] if eligibility_residence else [],
        caste_allowed=caste_list,
        states_allowed=states_allowed or ([normalized_state] if normalized_state else []),
        is_central=is_central,
        gender=gender,
        disability_related=bool(disability),
        bpl_required=bpl,
        income_limit_source=income_source,
    )

    financial_details = FinancialDetails(
        minimum_amount=min_amount,
        maximum_amount=max_amount,
        amount_source=amount_source,
    )

    return Scheme(
        scheme_id=slug,
        scheme_name=name,
        government_level=government_level,
        state=normalized_state,
        ministry=ministry,
        department=department,
        category=category_list,
        scheme_type=_clean_str(row.get("beneficiary_type")),
        description=description,
        benefits=benefits_list,
        eligibility=eligibility,
        financial_details=financial_details,
        documents_required=documents_list,
        application_process=application_process,
        application_url=apply_url,
        official_source=official_url,
        last_verified=_clean_str(row.get("scraped_at")),
        eligibility_text_raw=eligibility_text,
    )


def load_schemes(csv_path: Optional[Path] = None) -> List[Scheme]:
    path = csv_path or DEFAULT_CSV_PATH
    df = pd.read_csv(path)
    schemes: List[Scheme] = []
    errors = 0
    for idx, row in df.iterrows():
        try:
            schemes.append(_row_to_scheme(row, idx))
        except Exception as exc:  # noqa: BLE001
            errors += 1
            logger.warning("Failed to import row %s: %s", idx, exc)

    logger.info("CSV rows found: %s", len(df))
    logger.info("Loaded %s schemes with %s errors.", len(schemes), errors)
    return schemes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = load_schemes()
    print(f"Loaded {len(result)} schemes.")
