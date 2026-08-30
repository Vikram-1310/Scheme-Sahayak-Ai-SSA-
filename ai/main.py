"""
FastAPI application entry point.

Run from project root with:
.\\ai\\.venv\\Scripts\\python.exe -m uvicorn ai.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from ai.auth import router as auth_router
from ai.api_models import (
    RecommendRequest,
    RecommendResponse,
    SearchResponse,
    EligibilityRequest,
    EligibilityResponse,
)
from ai.recommendation_service import (
    get_recommendations,
    search_schemes,
    check_single_scheme_eligibility,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="Scheme Sahayak AI - AI-Driven Scheme Matching")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Scheme Sahayak AI matching API is running."}


# ----------------------------------------------------------------------
# AI chat endpoint — preserved, delegating to your existing ai_engine.py.
# NOTE: this calls it defensively since the actual ai_engine.py contents
# were not provided. If your real function name/signature differs, update
# _run_ai_engine below to call it exactly.
# ----------------------------------------------------------------------
def _run_ai_engine(message: str):
    try:
        from ai import ai_engine  # noqa: WPS433 (local import by design)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"ai_engine import failed: {exc}")

    for fn_name in ("process_message", "handle_chat", "chat", "process_chat", "run"):
        fn = getattr(ai_engine, fn_name, None)
        if callable(fn):
            return fn(message)

    raise HTTPException(
        status_code=500,
        detail=(
            "Could not find a callable entry point in ai_engine.py "
            "(tried process_message/handle_chat/chat/process_chat/run). "
            "Please expose one of these, or update _run_ai_engine to match "
            "your actual function name."
        ),
    )


@app.post("/ai/chat")
def ai_chat(payload: dict):
    message = payload.get("message") or payload.get("text")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' in request body.")
    return _run_ai_engine(message)


# ----------------------------------------------------------------------
# Scheme recommendation / search / eligibility endpoints
# ----------------------------------------------------------------------

@app.post("/schemes/recommend", response_model=RecommendResponse)
def recommend_schemes(request: RecommendRequest):
    profile = request.to_profile()
    result = get_recommendations(profile, top_n=request.top_n)
    return result


@app.get("/schemes/search", response_model=SearchResponse)
def search_schemes_endpoint(
    category: str | None = Query(default=None),
    state: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
):
    result = search_schemes(category=category, state=state, keyword=keyword)
    return result


@app.post("/schemes/eligibility", response_model=EligibilityResponse)
def eligibility_endpoint(request: EligibilityRequest):
    profile = request.profile.to_profile()
    result = check_single_scheme_eligibility(profile, request.scheme_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result
