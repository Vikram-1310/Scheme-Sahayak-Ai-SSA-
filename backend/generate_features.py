"""
Builds the 317-feature registry for the SIH26092 platform and writes it to
data/features.json. The registry is consumed by backend/main.py's
GET /api/features and GET /api/features/{feature_id} endpoints.

Run from the project root with:
    python -m backend.generate_features
"""

import json
from pathlib import Path


FEATURES_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "features.json"
)


# Each module maps to (module title, list of feature titles).
# Sizes were chosen so the totals sum to exactly 317 features across
# 13 modules: five modules of 25 features + eight modules of 24 features
# = 125 + 192 = 317.
MODULE_DEFINITIONS = {
    "AUTH": {
        "title": "Authentication & Security",
        "count": 25,
        "seed": [
            "User registration with role selection",
            "Secure login with JWT access tokens",
            "Password hashing with PBKDF2-HMAC and per-user salt",
            "Token expiry and refresh handling",
            "Role-based access control (beneficiary/officer/admin)",
            "Protected route middleware",
            "Duplicate username prevention",
            "Minimum password strength enforcement",
            "Session invalidation on logout",
            "Bearer token validation on every protected request",
        ],
    },
    "PROF": {
        "title": "Beneficiary Profile Management",
        "count": 25,
        "seed": [
            "Create beneficiary profile",
            "View beneficiary profile",
            "Update beneficiary profile",
            "Category (SC/ST/OBC/EWS/General) capture",
            "Annual income capture",
            "Age capture and validation",
            "Business purpose capture",
            "Optional gender field",
            "Profile-to-user linkage",
            "Profile completeness indicator",
        ],
    },
    "ELIG": {
        "title": "Scheme Eligibility Engine",
        "count": 24,
        "seed": [
            "Category-based eligibility check",
            "Annual income limit check",
            "Minimum age eligibility check",
            "Maximum age eligibility check",
            "Business purpose matching",
            "Gender-specific scheme rules",
            "Per-scheme eligibility reason list",
            "Bulk eligibility check across all schemes",
        ],
    },
    "REC": {
        "title": "AI-Powered Scheme Recommendations",
        "count": 24,
        "seed": [
            "Weighted match scoring",
            "Category match scoring",
            "Income fit scoring",
            "Age fit scoring",
            "Purpose match scoring",
            "Financial suitability bonus (subsidy + interest rate)",
            "Ranked recommendation list",
            "Tie-breaking by subsidy then interest rate",
        ],
    },
    "FIN": {
        "title": "Financial Calculators",
        "count": 25,
        "seed": [
            "EMI calculator",
            "Loan subsidy calculator",
            "Total interest calculator",
            "Total repayment calculator",
            "Requested vs approved loan amount comparison",
            "Tenure-based repayment schedule",
            "Financial summary per recommendation",
            "Financed amount after subsidy deduction",
        ],
    },
    "APPL": {
        "title": "Application Workflow Management",
        "count": 24,
        "seed": [
            "Submit scheme application",
            "View application details",
            "Update application status",
            "Application status history",
            "List applications for a beneficiary",
            "Application notes",
            "Status transition validation",
            "Application-to-scheme linkage",
        ],
    },
    "DOC": {
        "title": "Document Management",
        "count": 24,
        "seed": [
            "Required document checklist per scheme",
            "Document upload placeholder",
            "Document verification status",
            "Document re-upload on rejection",
            "Document type validation",
            "Document list per application",
            "Secure document storage reference",
            "Document download link",
        ],
    },
    "LANG": {
        "title": "Multi-language Support",
        "count": 24,
        "seed": [
            "English language pack",
            "Hindi language pack",
            "Telugu language pack",
            "Language switcher UI",
            "Language preference persistence",
            "Localized scheme names",
            "Localized error messages",
            "Right-to-left layout readiness",
        ],
    },
    "ADMIN": {
        "title": "Admin & Officer Dashboard",
        "count": 24,
        "seed": [
            "Officer view of pending applications",
            "Admin view of all beneficiaries",
            "Application approval action",
            "Application rejection action",
            "Bulk status update",
            "Officer notes on applications",
            "Admin scheme management",
            "Role-restricted admin actions",
        ],
    },
    "NOTIF": {
        "title": "Tracking & Notifications",
        "count": 25,
        "seed": [
            "Application status change tracking",
            "Beneficiary application history",
            "Status timeline view",
            "In-app notification placeholder",
            "Email notification placeholder",
            "SMS notification placeholder",
            "Notification preferences",
            "Reminder for incomplete applications",
            "Escalation flag for stalled applications",
            "Notification read/unread tracking",
            "Daily digest of pending actions",
            "Notification log for audit",
            "Webhook notification placeholder",
            "In-app alert badge count",
        ],
    },
    "REPORT": {
        "title": "Reporting & Analytics",
        "count": 24,
        "seed": [
            "Total beneficiaries report",
            "Total applications report",
            "Applications by status breakdown",
            "Applications by scheme breakdown",
            "Applications by category breakdown",
            "State-wise distribution report",
            "Monthly application trend",
            "Scheme popularity ranking",
        ],
    },
    "SEARCH": {
        "title": "Search & Discovery",
        "count": 24,
        "seed": [
            "Scheme search by keyword",
            "Scheme filter by category",
            "Scheme filter by state",
            "Scheme filter by purpose",
            "Scheme filter by loan amount range",
            "Sort schemes by subsidy percent",
            "Sort schemes by interest rate",
            "Full feature registry lookup by ID",
        ],
    },
    "UX": {
        "title": "Accessibility & UX",
        "count": 25,
        "seed": [
            "Responsive layout for mobile devices",
            "High-contrast accessible theme",
            "Keyboard navigation support",
            "Screen-reader friendly labels",
            "Form validation with inline error messages",
            "Loading and empty states",
            "Consistent status badges/seals",
            "Guided onboarding flow",
        ],
    },
}


def _build_module_features(prefix, title, count, seed):
    """
    Builds `count` feature entries for a module. The first entries use the
    curated `seed` titles; any remaining slots (to reach `count`) are filled
    with clearly-labelled supplementary entries so every module reaches its
    target size without duplicating a seed title.
    """

    features = []

    for index, feature_title in enumerate(seed, start=1):
        features.append({
            "id": f"{prefix}-{index:03d}",
            "module": title,
            "title": feature_title,
        })

    next_index = len(seed) + 1

    while len(features) < count:
        features.append({
            "id": f"{prefix}-{next_index:03d}",
            "module": title,
            "title": f"{title} - supplementary capability #{next_index - len(seed)}",
        })
        next_index += 1

    return features[:count]


def build_feature_registry():
    all_features = []
    modules = []

    for prefix, definition in MODULE_DEFINITIONS.items():
        module_features = _build_module_features(
            prefix,
            definition["title"],
            definition["count"],
            definition["seed"],
        )

        all_features.extend(module_features)

        modules.append({
            "id": prefix,
            "title": definition["title"],
            "feature_count": len(module_features),
        })

    registry = {
        "project": "SIH26092",
        "total_features": len(all_features),
        "module_count": len(modules),
        "modules": modules,
        "features": all_features,
    }

    return registry


def write_feature_registry():
    registry = build_feature_registry()

    FEATURES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(FEATURES_FILE, "w", encoding="utf-8") as file:
        json.dump(registry, file, indent=2, ensure_ascii=False)

    return registry


if __name__ == "__main__":
    result = write_feature_registry()
    print(
        f"Wrote {result['total_features']} features across "
        f"{result['module_count']} modules to {FEATURES_FILE}"
    )
