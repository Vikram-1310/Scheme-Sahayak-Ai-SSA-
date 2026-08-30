# SIH26092 — clean run guide

## 1. Backend
Open PowerShell in the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

If PowerShell blocks `npm.ps1`, use `npm.cmd` instead of `npm`, or run the commands in Command Prompt.

## 2. Frontend
Open a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the Vite URL shown in the terminal (normally http://localhost:5173).

## 3. Admin/officer accounts
Public registration creates beneficiaries only. To create an officer/admin, first create an admin through a controlled database/provisioning process and then call:

`POST /api/auth/provision`

with an admin bearer token.

## 4. AI data
The unified backend loads `data/Schemes.csv` and exposes the full 4,693-scheme dataset through the same API used by the frontend.

## 5. Database
`data/beneficiaries.db` is intentionally not shipped. It is generated automatically on first backend startup.


## Database and AI (updated)
The backend uses a local SQLite database at `data/scheme_sahayak.db`.
It is created automatically on first backend startup. It stores users, beneficiary
profiles, applications, saved schemes, notifications, chat sessions/messages,
and the partner registry.

The conversational assistant is grounded in the local scheme registry and stores
chat history. For more natural LLM dialogue, optionally install/run Ollama and set:
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=<your-installed-model>
If Ollama is unavailable, the grounded assistant continues to work without an
external AI service.
