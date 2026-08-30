"""
Basic test suite for the scheme matching system.
Run with: pytest ai/tests/test_scheme_system.py -v
(from project root, with the venv active)
"""

import pytest
from fastapi.testclient import TestClient

from ai.state_normalizer import normalize_state
from ai.caste_normalizer import normalize_caste, user_caste_is_allowed
from ai.business_normalizer import business_matches
from ai.scheme_importer import load_schemes
from ai.scheme_models import Scheme, SchemeEligibility, FinancialDetails, UserProfile
from ai.eligibility_engine import check_eligibility
from ai.scheme_recommender import recommend
from ai.main import app


@pytest.fixture(scope="module")
def schemes():
    return load_schemes()


def test_importer_loads_all_records(schemes):
    assert len(schemes) == 4693


def test_state_normalization_city_to_state():
    assert normalize_state("Vijayawada") == "Andhra Pradesh"
    assert normalize_state("Vijayawada, Andhra Pradesh") == "Andhra Pradesh"
    assert normalize_state("AP") == "Andhra Pradesh"
    assert normalize_state("ap") == "Andhra Pradesh"


def test_caste_normalization():
    assert normalize_caste("Scheduled Caste") == ["SC"]
    assert normalize_caste("SC/ST") == ["SC", "ST"]
    assert normalize_caste("") == []


def _make_scheme(**overrides) -> Scheme:
    base = dict(
        scheme_id="test-1",
        scheme_name="Test Scheme",
        government_level="Central",
        state=None,
        category=["Business & Entrepreneurship"],
        description="Support for tailoring and sewing micro enterprises.",
        benefits=["Loan up to 2 lakh"],
        eligibility=SchemeEligibility(is_central=True),
        financial_details=FinancialDetails(),
    )
    base.update(overrides)
    return Scheme(**base)


def test_sc_matching_no_caste_rule_not_excluded():
    scheme = _make_scheme(eligibility=SchemeEligibility(is_central=True, caste_allowed=[]))
    assert user_caste_is_allowed("SC", scheme.eligibility.caste_allowed) is None


def test_explicit_st_only_scheme_rejected_for_sc():
    scheme = _make_scheme(
        eligibility=SchemeEligibility(is_central=True, caste_allowed=["ST"])
    )
    assert user_caste_is_allowed("SC", scheme.eligibility.caste_allowed) is False


def test_income_within_limit_passes():
    scheme = _make_scheme(
        eligibility=SchemeEligibility(is_central=True, income_limit=500000)
    )
    user = UserProfile(category="SC", annual_income=300000)
    result = check_eligibility(user, scheme)
    assert "Income exceeds" not in " ".join(result.failed_rules)


def test_income_above_limit_fails():
    scheme = _make_scheme(
        eligibility=SchemeEligibility(is_central=True, income_limit=100000)
    )
    user = UserProfile(category="SC", annual_income=300000)
    result = check_eligibility(user, scheme)
    assert result.status == "NOT_ELIGIBLE"


def test_missing_income_produces_insufficient_information():
    scheme = _make_scheme(
        eligibility=SchemeEligibility(is_central=True, income_limit=500000)
    )
    user = UserProfile(category="SC", annual_income=None)
    result = check_eligibility(user, scheme)
    assert result.status == "INSUFFICIENT_INFORMATION"
    assert "annual_income" in result.missing_information


def test_central_scheme_works_for_andhra_pradesh():
    scheme = _make_scheme(eligibility=SchemeEligibility(is_central=True))
    user = UserProfile(category="SC", location="Vijayawada")
    result = check_eligibility(user, scheme)
    assert "State does not match" not in " ".join(result.failed_rules)


def test_business_tailoring_matches_sewing_schemes():
    text = "This scheme supports sewing and tailor micro enterprises."
    assert business_matches("tailoring", text) is True


def test_financial_amount_unknown_does_not_fail():
    scheme = _make_scheme(financial_details=FinancialDetails())
    user = UserProfile(category="SC", loan_required=150000)
    result = check_eligibility(user, scheme)
    assert "outside scheme" not in " ".join(result.failed_rules)
    assert "exceeds" not in " ".join(result.failed_rules)


def test_recommender_returns_results_for_test_profile(schemes):
    user = UserProfile(
        category="SC",
        location="Vijayawada",
        annual_income=300000,
        business="tailoring",
        purpose="STARTING A BUSINESS",
        loan_required=150000,
    )
    recommendations = recommend(user, schemes, top_n=10)
    assert len(recommendations) > 0


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_api_recommend_endpoint(client):
    response = client.post(
        "/schemes/recommend",
        json={
            "category": "SC",
            "location": "Vijayawada",
            "annual_income": 300000,
            "business": "tailoring",
            "purpose": "STARTING A BUSINESS",
            "loan_required": 150000,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0


def test_api_search_endpoint(client):
    response = client.get("/schemes/search", params={"category": "SC", "keyword": "tailoring"})
    assert response.status_code == 200


def test_api_eligibility_endpoint(client, schemes):
    scheme_id = schemes[0].scheme_id
    response = client.post(
        "/schemes/eligibility",
        json={
            "profile": {"category": "SC", "location": "Vijayawada", "annual_income": 300000},
            "scheme_id": scheme_id,
        },
    )
    assert response.status_code == 200
