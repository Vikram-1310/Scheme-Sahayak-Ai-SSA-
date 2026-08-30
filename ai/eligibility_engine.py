"""
Eligibility rule engine: determines whether a user profile satisfies a
scheme's eligibility conditions.

Status semantics:
    ELIGIBLE                 -> no failed rules, no missing information
    NOT_ELIGIBLE              -> at least one explicit, hard rule failure
    INSUFFICIENT_INFORMATION -> no failures, but required info is missing

Unknown/unspecified scheme conditions are never treated as failures -
only explicit contradictions count against the user.
"""

from __future__ import annotations

from typing import List

from ai.scheme_models import UserProfile, Scheme, EligibilityResult
from ai.caste_normalizer import user_caste_is_allowed
from ai.state_normalizer import normalize_state
from ai.financial_parser import evaluate_amount_against_range


def check_eligibility(user: UserProfile, scheme: Scheme) -> EligibilityResult:
    elig = scheme.eligibility

    matched_rules: List[str] = []
    failed_rules: List[str] = []
    missing_information: List[str] = []
    warnings: List[str] = []

    # ------------------------------------------------------------------
    # Category / caste
    # ------------------------------------------------------------------
    caste_ok = user_caste_is_allowed(user.category, elig.caste_allowed)
    if caste_ok is True:
        matched_rules.append("Category matches scheme's allowed categories.")
    elif caste_ok is False:
        failed_rules.append("Category does not match scheme's allowed categories.")
    elif elig.caste_allowed and not user.category:
        missing_information.append("category")

    # ------------------------------------------------------------------
    # Annual income
    # ------------------------------------------------------------------
    if elig.income_limit is not None:
        if user.annual_income is None:
            missing_information.append("annual_income")
        elif user.annual_income > elig.income_limit:
            failed_rules.append(
                f"Income exceeds scheme's limit of {elig.income_limit}."
            )
        else:
            matched_rules.append("Income within scheme's limit.")

    # ------------------------------------------------------------------
    # Age
    # ------------------------------------------------------------------
    if elig.age_min is not None or elig.age_max is not None:
        if user.age is None:
            missing_information.append("age")
        elif elig.age_min is not None and user.age < elig.age_min:
            failed_rules.append(f"Age below scheme's minimum of {elig.age_min}.")
        elif elig.age_max is not None and user.age > elig.age_max:
            failed_rules.append(f"Age above scheme's maximum of {elig.age_max}.")
        else:
            matched_rules.append("Age within scheme's allowed range.")

    # ------------------------------------------------------------------
    # State / location
    # ------------------------------------------------------------------
    if elig.is_central:
        matched_rules.append("Central scheme — no state restriction.")
    else:
        allowed_states = elig.states_allowed or (
            [scheme.state] if scheme.state else []
        )
        if allowed_states:
            if not user.location:
                missing_information.append("location")
            else:
                user_state = normalize_state(user.location) or user.location
                if user_state not in allowed_states:
                    failed_rules.append(
                        "State does not match scheme's applicable states."
                    )
                else:
                    matched_rules.append(
                        "State matches scheme's applicable states."
                    )

    # ------------------------------------------------------------------
    # Financial range (requested/loan amount vs scheme min/max)
    # ------------------------------------------------------------------
    fin = scheme.financial_details
    result, reason = evaluate_amount_against_range(
        user.loan_required, fin.minimum_amount, fin.maximum_amount
    )
    if result is True:
        matched_rules.append(reason)
    elif result is False:
        failed_rules.append(reason)
    # result is None -> insufficient/unknown financial data; not a failure

    # ------------------------------------------------------------------
    # Disability (informational only — not enforced as a hard rule since
    # we don't collect a disability flag on the user profile)
    # ------------------------------------------------------------------
    if elig.disability_related:
        warnings.append(
            "This scheme is specifically intended for persons with disabilities."
        )

    if elig.bpl_required:
        warnings.append(
            "This scheme requires Below Poverty Line (BPL) status."
        )

    # ------------------------------------------------------------------
    # Final status
    # ------------------------------------------------------------------
    if failed_rules:
        status = "NOT_ELIGIBLE"
    elif missing_information:
        status = "INSUFFICIENT_INFORMATION"
    else:
        status = "ELIGIBLE"

    return EligibilityResult(
        scheme_id=scheme.scheme_id,
        status=status,
        matched_rules=matched_rules,
        failed_rules=failed_rules,
        missing_information=missing_information,
        warnings=warnings,
    )
