# Scheme Sahayak AI — Frontend

React (Vite) frontend for the SC Beneficiary scheme-matching platform.
Talks to the FastAPI backend in `Scheme Sahayak AI/backend/`.

## Folder structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js            # dev server on :5173, proxies /api → :8000
├── .env.example
└── src/
    ├── main.jsx
    ├── App.jsx                # routes
    ├── api/
    │   └── client.js          # every backend call lives here
    ├── context/
    │   └── AuthContext.jsx    # login/register/logout, token storage
    ├── components/
    │   ├── Navbar.jsx
    │   ├── ProtectedRoute.jsx
    │   ├── StatusSeal.jsx
    │   └── EmptyState.jsx
    ├── pages/
    │   ├── Login.jsx
    │   ├── Register.jsx
    │   ├── Profile.jsx         # create/update beneficiary profile
    │   ├── Eligibility.jsx     # POST /api/eligibility/check
    │   ├── Recommendations.jsx # POST /api/recommendations + apply
    │   └── Applications.jsx    # GET /api/profiles/{id}/applications
    └── styles/
        └── theme.css           # design tokens + component styles
```

## Setup

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`. Make sure the backend is running first:

```bash
cd ../backend  # or wherever backend/main.py lives
uvicorn backend.main:app --reload
```

The dev server proxies any request to `/api/*` straight to
`http://127.0.0.1:8000`, so nothing needs a hardcoded backend URL locally.

## How the pages map to backend endpoints

| Page              | Endpoint(s)                                                        |
|-------------------|----------------------------------------------------------------------|
| Login / Register  | `POST /api/auth/login`, `POST /api/auth/register`                   |
| Profile           | `POST /api/profiles`, `GET /api/profiles/{id}`, `PUT /api/profiles/{id}` |
| Eligibility       | `POST /api/eligibility/check`                                        |
| Recommendations   | `POST /api/recommendations`, `POST /api/applications`                |
| Applications      | `GET /api/profiles/{id}/applications`                                |

All authenticated calls attach `Authorization: Bearer <token>` automatically
(see `api/client.js`) — the token comes from `/api/auth/login` and is kept in
`localStorage` alongside the created beneficiary `profile_id`.

## Known gap

The backend's `/api/features` endpoint (the 317-item feature registry) has
no corresponding page yet, since — per the backend README — the actual
`data/features.json` content hasn't been confirmed as real JSON (a SQLite
db was found under that filename at one point). Add a `Features.jsx` page
once that data file is sorted out on the backend side.


## Added features
- Multi-language selector: English, Tamil, Hindi, Telugu, Kannada and Malayalam.
- Finance Calculator at `/finance-calculator` for EMI, total interest and total repayment estimates.
