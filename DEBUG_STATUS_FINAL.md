# Scheme Sahayak AI - final fixes

## Fixed
- `/api/ai/chat` no longer imports the nonexistent `get_my_profile` from `backend.database`.
- Chat history is passed from the authenticated chat session into the assistant, so follow-up context is available.
- Removed the legacy `/api/chat` and `/ai/chat` routes that referenced the missing `ai.ai_engine` implementation.
- Multilingual scheme search now recognizes common Hindi, Tamil, Telugu, Kannada and Malayalam education/business/agriculture/employment/housing/health/women/scholarship/loan terms.
- Frontend language switching now translates the existing literal UI labels across pages through the shared LanguageContext, persists the selected language, and updates document language.
- AI welcome text, placeholder, thinking state and suggestions respond to the selected language.
- SQLite remains the single persistent database and chat sessions/messages are retained.

## Verification
- Python compile check: PASS
- FastAPI TestClient login: PASS
- English greeting: PASS (HTTP 200)
- English education search: PASS (HTTP 200, scheme matches returned)
- Hindi education search: PASS (HTTP 200, scheme matches returned)
- Tamil education search: PASS (HTTP 200, scheme matches returned)
- Chat history endpoint: PASS
- Frontend `npm install`: not completed in this build environment because package download timed out; run it locally before `npm run dev`.
