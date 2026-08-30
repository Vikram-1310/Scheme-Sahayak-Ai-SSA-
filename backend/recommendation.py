import json
from pathlib import Path


SCHEMES_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "schemes.json"
)


def load_schemes():
    with open(SCHEMES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_match_score(profile, scheme):
    score = 0
    reasons = []

    # Category: 25 points
    if profile.get("category") == scheme.get("category"):
        score += 25
        reasons.append("Category matches")

    # Income: 20 points
    income = profile.get("annual_income")

    if income is not None:
        maximum = scheme.get("max_annual_income", 0)

        if income <= maximum:
            score += 20
            reasons.append("Income is within the scheme limit")

    # Age: 15 points
    age = profile.get("age")

    if age is not None:
        if scheme["min_age"] <= age <= scheme["max_age"]:
            score += 15
            reasons.append("Age is eligible")

    # Purpose: 25 points
    purpose = profile.get("purpose")

    if purpose in scheme.get("purpose", []):
        score += 25
        reasons.append("Business purpose matches")

    # Gender: 5 points
    required_gender = scheme.get("gender")

    if required_gender:
        if profile.get("gender") == required_gender:
            score += 5
            reasons.append("Gender criterion matches")
    else:
        score += 5
        reasons.append("No gender restriction")

    return score, reasons


def calculate_financial_bonus(scheme):
    """
    Gives a small ranking bonus based on the scheme's
    financial characteristics.

    This does NOT determine eligibility.
    Eligibility remains a hard requirement.
    """

    bonus = 0

    subsidy = scheme.get("subsidy_percent", 0)
    interest_rate = scheme.get("interest_rate", 100)

    # Higher subsidy = better
    if subsidy >= 30:
        bonus += 5
    elif subsidy >= 25:
        bonus += 4
    elif subsidy >= 20:
        bonus += 3
    elif subsidy >= 15:
        bonus += 2
    elif subsidy > 0:
        bonus += 1

    # Lower interest = better
    if interest_rate <= 6.5:
        bonus += 5
    elif interest_rate <= 7.0:
        bonus += 4
    elif interest_rate <= 7.5:
        bonus += 3
    elif interest_rate <= 8.0:
        bonus += 2
    else:
        bonus += 1

    return bonus


def recommend_schemes(profile, eligibility_results):
    schemes = load_schemes()

    scheme_lookup = {
        scheme["id"]: scheme
        for scheme in schemes
    }

    recommendations = []

    for result in eligibility_results:

        # Never recommend an ineligible scheme
        if not result["eligible"]:
            continue

        scheme = scheme_lookup.get(result["scheme_id"])

        if not scheme:
            continue

        base_score, reasons = calculate_match_score(
            profile,
            scheme
        )

        financial_bonus = calculate_financial_bonus(
            scheme
        )

        final_score = base_score + financial_bonus

        if financial_bonus > 0:
            reasons.append(
                f"Financial suitability bonus: +{financial_bonus}"
            )

        recommendations.append({
            "rank": 0,
            "scheme_id": scheme["id"],
            "scheme_name": scheme["name"],
            "match_score": final_score,
            "base_score": base_score,
            "financial_bonus": financial_bonus,
            "reasons": reasons,
            "loan_max": scheme.get("loan_max"),
            "subsidy_percent": scheme.get("subsidy_percent"),
            "interest_rate": scheme.get("interest_rate"),
            "tenure_years": scheme.get("tenure_years")
        })

    # Highest score first.
    # If scores tie, higher subsidy wins.
    # If still tied, lower interest rate wins.
    recommendations.sort(
        key=lambda item: (
            item["match_score"],
            item["subsidy_percent"],
            -item["interest_rate"]
        ),
        reverse=True
    )

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):
        recommendation["rank"] = index

    return recommendations