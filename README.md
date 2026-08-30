# Scheme Sahayak AI

A competition-ready prototype for AI-assisted government scheme discovery, eligibility checking, scheme-level financial planning, and application tracking.

## Highlights

- 4,693-scheme searchable registry loaded from `data/Schemes.csv`
- Profile-driven eligibility checks
- AI-ranked scheme recommendations with reasons
- Individual scheme detail pages
- **Financial calculator embedded inside each scheme**
- Application submission and status tracking
- Multilingual foundation: English, Hindi, Tamil, Telugu, Kannada, Malayalam
- Embedded **Scheme Sahayak AI** assistant with optional local Ollama support and an offline fallback
- JWT authentication and role-aware application workflow
- Responsive presentation-focused React interface

## Run on Windows

### Backend

```powershell
cd "Scheme Sahayak AI"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend — new terminal

```powershell
cd "Scheme Sahayak AI\frontend"
npm.cmd install
npm.cmd run dev
```

Open the Vite URL shown in the terminal.

## Optional local AI

Copy `.env.example` to `.env` and configure `OLLAMA_URL` and `OLLAMA_MODEL` if Ollama is available locally. The application remains usable without Ollama using the built-in scheme-aware assistant.

## Important product note

The application registry contains 317 planned/registered capabilities, but a registry entry is not proof that an external integration is live. External services such as SMS/email delivery or third-party document verification require their respective provider credentials and integration.
