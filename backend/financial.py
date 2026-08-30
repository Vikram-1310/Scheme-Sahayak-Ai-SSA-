import math


def calculate_emi(principal, annual_interest_rate, tenure_years):
    if principal <= 0:
        return 0

    months = tenure_years * 12
    monthly_rate = annual_interest_rate / 12 / 100

    if monthly_rate == 0:
        return principal / months

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** months
        / ((1 + monthly_rate) ** months - 1)
    )

    return round(emi, 2)


def calculate_finance(
    requested_amount,
    scheme
):
    loan_max = scheme.get("loan_max", 0)

    loan_amount = min(
        requested_amount,
        loan_max
    )

    subsidy_percent = scheme.get(
        "subsidy_percent",
        0
    )

    subsidy_amount = (
        loan_amount * subsidy_percent / 100
    )

    financed_amount = (
        loan_amount - subsidy_amount
    )

    interest_rate = scheme.get(
        "interest_rate",
        0
    )

    tenure_years = scheme.get(
        "tenure_years",
        1
    )

    emi = calculate_emi(
        financed_amount,
        interest_rate,
        tenure_years
    )

    total_repayment = round(
        emi * tenure_years * 12,
        2
    )

    total_interest = round(
        total_repayment - financed_amount,
        2
    )

    return {
        "requested_amount": requested_amount,
        "approved_loan_amount": loan_amount,
        "subsidy_percent": subsidy_percent,
        "subsidy_amount": round(subsidy_amount, 2),
        "financed_amount": round(financed_amount, 2),
        "interest_rate": interest_rate,
        "tenure_years": tenure_years,
        "monthly_emi": emi,
        "total_interest": total_interest,
        "total_repayment": total_repayment
    }