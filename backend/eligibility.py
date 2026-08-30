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


def check_eligibility(profile):
    schemes = load_schemes()
    results = []

    for scheme in schemes:
        reasons = []
        eligible = True

        # Category
        if profile.get("category") != scheme.get("category"):
            eligible = False
            reasons.append("Category does not match")

        # Annual income
        income = profile.get("annual_income")

        if income is not None:
            if income > scheme["max_annual_income"]:
                eligible = False
                reasons.append(
                    "Annual income exceeds the scheme limit"
                )

        # Age
        age = profile.get("age")

        if age is not None:
            if age < scheme["min_age"]:
                eligible = False
                reasons.append(
                    "Age is below the minimum"
                )

            elif age > scheme["max_age"]:
                eligible = False
                reasons.append(
                    "Age exceeds the maximum"
                )

        # Purpose
        purpose = profile.get("purpose")

        if purpose:
            allowed_purposes = scheme.get("purpose", [])

            if purpose not in allowed_purposes:
                eligible = False
                reasons.append(
                    "Business purpose does not match"
                )

        # Gender-specific requirement
        required_gender = scheme.get("gender")

        if required_gender:
            if profile.get("gender") != required_gender:
                eligible = False
                reasons.append(
                    "Gender criterion not satisfied"
                )

        results.append({
            "scheme_id": scheme["id"],
            "scheme_name": scheme["name"],
            "eligible": eligible,
            "reasons": reasons
        })

    return results