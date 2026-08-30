from pathlib import Path
import json
import os
import secrets

from fastapi import FastAPI, HTTPException, Depends, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from uuid import uuid4

from backend.database import (
    initialize_database,
    create_chat_session,
    get_chat_session,
    save_chat_message,
    get_chat_messages,
    save_scheme,
    unsave_scheme,
    get_saved_schemes,
    get_nearby_partners,
)

from backend.profile import (
    initialize_profile_system,
    create_profile,
    get_profile,
    get_my_profile,
    update_profile,
)

from backend.application import (
    initialize_application_table,
    create_application,
    get_application,
    update_application_status,
    get_beneficiary_applications,
    application_owned_by_user,
)

from backend.auth import (
    initialize_auth_table,
    create_user,
    get_user,
    verify_password,
    create_access_token,
    decode_access_token,
    get_connection,
)

from ai.scheme_source import get_scheme_source

from ai.recommendation_service import (
    get_recommendations as ai_recommendations,
    search_schemes as ai_search,
    check_single_scheme_eligibility,
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Scheme Sahayak AI - Government Scheme Assistant",
    version="3.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUTHENTICATION
# ============================================================

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    return payload


def require_roles(*roles):
    def dep(user=Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )

        return user

    return dep


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()
initialize_auth_table()
initialize_profile_system()
initialize_application_table()


# ============================================================
# FILES
# ============================================================

FEATURES_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "features.json"
)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class BeneficiaryProfile(BaseModel):
    category: str = Field(min_length=1)
    annual_income: float = Field(ge=0)
    age: int = Field(ge=0, le=120)
    purpose: str = Field(min_length=1)

    gender: str | None = None
    state: str | None = None
    district: str | None = None
    occupation: str | None = None
    business_type: str | None = None
    business_stage: str | None = None


class RecommendationRequest(BeneficiaryProfile):
    requested_amount: float = Field(gt=0)


class ApplicationRequest(BaseModel):
    beneficiary_id: int = Field(gt=0)
    scheme_id: str = Field(min_length=1)
    notes: str | None = None


class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: str | None = None


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    role: str = "beneficiary"


class LoginRequest(BaseModel):
    username: str
    password: str


# ============================================================
# ADMIN SETUP MODEL
# ============================================================

class AdminCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    setup_key: str = Field(min_length=1)


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "project": "Scheme Sahayak AI",
        "status": "running",
        "platform": "AI Government Scheme Assistant",
        "scheme_count": len(get_scheme_source().all()),
        "registered_features": 317,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "scheme_count": len(get_scheme_source().all()),
    }


# ============================================================
# AUTH - REGISTER
# ============================================================

@app.post("/api/auth/register")
def register_user(request: RegisterRequest):

    # Public registration can ONLY create beneficiary accounts.
    if request.role != "beneficiary":
        raise HTTPException(
            status_code=403,
            detail="Public registration can only create beneficiary accounts",
        )

    user = create_user(
        request.username.strip(),
        request.password,
        "beneficiary",
    )

    if user is None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    return {
        "message": "User registered successfully",
        "user": user,
    }


# ============================================================
# AUTH - LOGIN
# ============================================================

@app.post("/api/auth/login")
def login_user(request: LoginRequest):

    user = get_user(request.username.strip())

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not verify_password(
        request.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    token = create_access_token(
        user["id"],
        user["username"],
        user["role"],
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        },
    }


# ============================================================
# AUTH - PROVISION USER
# ============================================================

@app.post("/api/auth/provision")
def provision_user(
    request: RegisterRequest,
    user=Depends(require_roles("admin")),
):

    if request.role not in {
        "beneficiary",
        "officer",
        "admin",
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid role",
        )

    created = create_user(
        request.username.strip(),
        request.password,
        request.role,
    )

    if created is None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    return {
        "message": "User provisioned",
        "user": created,
    }


# ============================================================
# ADMIN - ONE TIME SETUP
# ============================================================

@app.post("/api/admin/setup")
def setup_admin(request: AdminCreateRequest):

    setup_key = os.getenv("ADMIN_SETUP_KEY")

    if not setup_key:
        raise HTTPException(
            status_code=503,
            detail="Admin setup is disabled because ADMIN_SETUP_KEY is not configured",
        )

    if not secrets.compare_digest(
        request.setup_key,
        setup_key,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid setup key",
        )

    connection = get_connection()

    try:
        existing_admin = connection.execute(
            "SELECT id FROM users WHERE role='admin' LIMIT 1"
        ).fetchone()

    finally:
        connection.close()

    if existing_admin:
        raise HTTPException(
            status_code=409,
            detail="An admin account already exists",
        )

    admin = create_user(
        request.username.strip(),
        request.password,
        "admin",
    )

    if admin is None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    return {
        "message": "Admin account created successfully",
        "user": admin,
    }


# ============================================================
# ADMIN - VIEW USERS
# ============================================================

@app.get("/api/admin/users")
def get_all_users(
    user=Depends(require_roles("admin")),
):

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                username,
                role,
                created_at
            FROM users
            ORDER BY id
            """
        ).fetchall()

    finally:
        connection.close()

    return {
        "total_users": len(rows),
        "users": [dict(row) for row in rows],
    }


# ============================================================
# PROFILE - CURRENT USER
# ============================================================

@app.get("/api/profiles/me")
def my_profile(
    user=Depends(get_current_user),
):

    return {
        "profile": get_my_profile(
            int(user["sub"])
        )
    }


# ============================================================
# PROFILE - CREATE
# ============================================================

@app.post("/api/profiles")
def create_beneficiary_profile(
    profile: BeneficiaryProfile,
    user=Depends(get_current_user),
):

    saved = create_profile(
        profile.model_dump(),
        int(user["sub"]),
    )

    return {
        "message": "Beneficiary profile created",
        "profile": saved,
    }


# ============================================================
# PROFILE OWNERSHIP
# ============================================================

def owned_profile(profile_id, user):

    profile = get_profile(profile_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Beneficiary profile not found",
        )

    if (
        profile.get("user_id") != int(user["sub"])
        and user.get("role") not in {"admin", "officer"}
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this profile",
        )

    return profile


# ============================================================
# PROFILE - GET
# ============================================================

@app.get("/api/profiles/{profile_id}")
def get_beneficiary_profile(
    profile_id: int,
    user=Depends(get_current_user),
):

    return {
        "profile": owned_profile(
            profile_id,
            user,
        )
    }


# ============================================================
# PROFILE - UPDATE
# ============================================================

@app.put("/api/profiles/{profile_id}")
def update_beneficiary_profile(
    profile_id: int,
    profile: BeneficiaryProfile,
    user=Depends(get_current_user),
):

    if user.get("role") not in {
        "admin",
        "officer",
    }:
        owned_profile(
            profile_id,
            user,
        )

    updated = update_profile(
        profile_id,
        profile.model_dump(),
        int(user["sub"]),
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Beneficiary profile not found",
        )

    return {
        "message": "Beneficiary profile updated",
        "profile": updated,
    }


# ============================================================
# FEATURES
# ============================================================

@app.get("/api/features")
def get_features(
    user=Depends(get_current_user),
):

    with open(
        FEATURES_FILE,
        encoding="utf-8",
    ) as file:

        return json.load(file)


@app.get("/api/features/{feature_id}")
def get_feature(
    feature_id: str,
    user=Depends(get_current_user),
):

    with open(
        FEATURES_FILE,
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    for feature in data["features"]:

        if feature["id"].lower() == feature_id.lower():
            return feature

    raise HTTPException(
        status_code=404,
        detail=f"Feature {feature_id} not found",
    )


# ============================================================
# ELIGIBILITY
# ============================================================

@app.post("/api/eligibility/check")
def eligibility_check(
    profile: BeneficiaryProfile,
    user=Depends(get_current_user),
):

    from ai.scheme_models import UserProfile
    from ai.eligibility_engine import check_eligibility

    user_profile = UserProfile(
        category=profile.category,
        annual_income=int(profile.annual_income),
        age=profile.age,
        purpose=profile.purpose,
        location=None,
    )

    source = get_scheme_source()

    results = []

    for scheme in source.all():

        result = check_eligibility(
            user_profile,
            scheme,
        ).model_dump()

        result["eligible"] = (
            result["status"] == "ELIGIBLE"
        )

        results.append(result)

    return {
        "results": results
    }


# ============================================================
# RECOMMENDATIONS
# ============================================================

@app.post("/api/recommendations")
def recommendations(
    request: RecommendationRequest,
    user=Depends(get_current_user),
):

    return ai_recommendations(
        request.model_dump()
    )


# ============================================================
# SCHEME SEARCH
# ============================================================

@app.get("/api/schemes/search")
def schemes_search(
    category: str | None = None,
    state: str | None = None,
    keyword: str | None = None,
):

    return ai_search(
        category=category,
        state=state,
        keyword=keyword,
    )


# ============================================================
# NEARBY PARTNERS
# ============================================================

@app.get("/api/partners/nearby")
def nearby_partners(
    scheme_id: str,
    latitude: float,
    longitude: float,
    radius_km: float = 50,
):

    if not get_scheme_source().get(scheme_id):

        raise HTTPException(
            status_code=404,
            detail="Scheme not found",
        )

    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid coordinates",
        )

    radius_km = min(
        max(radius_km, 1),
        100,
    )

    return {
        "scheme_id": scheme_id,
        "radius_km": radius_km,
        "partners": get_nearby_partners(
            scheme_id,
            latitude,
            longitude,
            radius_km=radius_km,
        ),
    }


# ============================================================
# SCHEME DETAILS
# ============================================================

@app.get("/api/schemes/{scheme_id}")
def scheme_detail(
    scheme_id: str,
):

    scheme = get_scheme_source().get(
        scheme_id
    )

    if not scheme:

        raise HTTPException(
            status_code=404,
            detail="Scheme not found",
        )

    return scheme


# ============================================================
# AI CHAT
# ============================================================

@app.post("/api/ai/chat")
def ai_chat(
    payload: dict,
    user=Depends(get_current_user),
):

    session_id = payload.get(
        "session_id"
    )

    message = payload.get(
        "message",
        "",
    )

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message is required",
        )

    if not session_id:

        session_id = str(uuid4())

        create_chat_session(
            session_id,
            int(user["sub"]),
        )

    save_chat_message(
        session_id,
        "user",
        message,
    )

    # Import AI assistant dynamically
    from backend.ai_assistant import generate_ai_response

    response = generate_ai_response(
        message
    )

    save_chat_message(
        session_id,
        "assistant",
        response,
    )

    return {
        "session_id": session_id,
        "response": response,
    }


# ============================================================
# AI CHAT HISTORY
# ============================================================

@app.get("/api/ai/history/{session_id}")
def ai_history(
    session_id: str,
    user=Depends(get_current_user),
):

    session = get_chat_session(
        session_id
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Chat session not found",
        )

    if session.get("user_id") != int(
        user["sub"]
    ):

        raise HTTPException(
            status_code=403,
            detail="You do not have access to this chat",
        )

    return {
        "session_id": session_id,
        "messages": get_chat_messages(
            session_id
        ),
    }


# ============================================================
# SAVED SCHEMES
# ============================================================

@app.get("/api/saved")
def get_saved(
    user=Depends(get_current_user),
):

    return {
        "schemes": get_saved_schemes(
            int(user["sub"])
        )
    }


@app.post("/api/saved/{scheme_id}")
def save(
    scheme_id: str,
    user=Depends(get_current_user),
):

    if not get_scheme_source().get(
        scheme_id
    ):

        raise HTTPException(
            status_code=404,
            detail="Scheme not found",
        )

    save_scheme(
        int(user["sub"]),
        scheme_id,
    )

    return {
        "message": "Scheme saved successfully"
    }


@app.delete("/api/saved/{scheme_id}")
def unsave(
    scheme_id: str,
    user=Depends(get_current_user),
):

    unsave_scheme(
        int(user["sub"]),
        scheme_id,
    )

    return {
        "message": "Scheme removed from saved schemes"
    }


# ============================================================
# DATABASE STATUS
# ============================================================

@app.get("/api/database/status")
def database_status(
    user=Depends(require_roles("admin", "officer")),
):

    connection = get_connection()

    try:

        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        ).fetchall()

        users_count = connection.execute(
            "SELECT COUNT(*) AS count FROM users"
        ).fetchone()["count"]

    finally:

        connection.close()

    return {
        "database": "connected",
        "tables": [
            row["name"]
            for row in tables
        ],
        "users_count": users_count,
    }


# ============================================================
# APPLICATIONS - CREATE
# ============================================================

@app.post("/api/applications")
def submit_application(
    request: ApplicationRequest,
    user=Depends(get_current_user),
):

    profile = get_profile(
        request.beneficiary_id
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Beneficiary profile not found",
        )

    if (
        profile.get("user_id")
        != int(user["sub"])
        and user.get("role")
        not in {"admin", "officer"}
    ):

        raise HTTPException(
            status_code=403,
            detail="You do not have access to this profile",
        )

    if not get_scheme_source().get(
        request.scheme_id
    ):

        raise HTTPException(
            status_code=404,
            detail="Scheme not found",
        )

    application = create_application(
        request.beneficiary_id,
        request.scheme_id,
        request.notes,
    )

    return {
        "message": "Application submitted successfully",
        "application": application,
    }


# ============================================================
# APPLICATION - GET
# ============================================================

@app.get("/api/applications/{application_id}")
def get_application_detail(
    application_id: int,
    user=Depends(get_current_user),
):

    application = get_application(
        application_id
    )

    if not application:

        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    if not application_owned_by_user(
        application_id,
        int(user["sub"]),
    ) and user.get("role") not in {
        "admin",
        "officer",
    }:

        raise HTTPException(
            status_code=403,
            detail="You do not have access to this application",
        )

    return {
        "application": application
    }


# ============================================================
# APPLICATION - UPDATE STATUS
# ============================================================

@app.put("/api/applications/{application_id}/status")
def change_application_status(
    application_id: int,
    request: ApplicationStatusUpdate,
    user=Depends(require_roles("admin", "officer")),
):

    updated = update_application_status(
        application_id,
        request.status,
        request.notes,
    )

    if updated is None:

        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return {
        "message": "Application status updated",
        "application": updated,
    }


# ============================================================
# PROFILE APPLICATIONS
# ============================================================

@app.get("/api/profiles/{profile_id}/applications")
def profile_applications(
    profile_id: int,
    user=Depends(get_current_user),
):

    profile = owned_profile(
        profile_id,
        user,
    )

    applications = get_beneficiary_applications(
        profile_id
    )

    return {
        "profile_id": profile_id,
        "applications": applications,
    }