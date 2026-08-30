"""
Shared pytest fixtures for the backend test suite.

backend/test_api.py assumes:
  - a user "testbeneficiary" / "Test@12345" already exists and can log in
  - a beneficiary profile with id=1 already exists

This fixture resets the SQLite database file to a clean state and seeds
both before the test session starts.
"""

from pathlib import Path

import pytest


DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "beneficiaries.db"
)


@pytest.fixture(scope="session", autouse=True)
def seed_test_data():
    # Start from a clean database so re-running the suite doesn't hit
    # "username already exists" errors.
    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    from backend.auth import initialize_auth_table, create_user
    from backend.database import initialize_database, create_beneficiary
    from backend.application import initialize_application_table

    initialize_auth_table()
    initialize_database()
    initialize_application_table()

    create_user(
        username="testbeneficiary",
        password="Test@12345",
        role="beneficiary",
    )

    # First beneficiary created on a fresh table gets id=1 (AUTOINCREMENT).
    create_beneficiary(
        category="SC",
        annual_income=250000,
        age=30,
        purpose="STARTING A BUSINESS",
        gender=None,
    )

    yield
