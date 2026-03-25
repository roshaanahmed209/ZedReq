# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZedRec is a LinkedIn-clone platform with AI-powered features: social feed, job portal with AI matching, LMS, AI video interviews (Tavus), real-time messaging, and a separate admin backoffice.

## Running the Project

### Start both backends (development)
```bash
python run_backends.py
```
Launches main API on `:5000` and backoffice on `:5001`. Controlled by `START_BACKENDS=both|main|backoffice` in root `.env`.

### Start services individually
```bash
# Main API
cd backend && python -m uvicorn main:app --reload --port 5000

# Backoffice API
cd backoffice/backend && python -m uvicorn main:app --reload --port 5001

# Frontend
cd frontend && npm run dev   # Vite dev server on :5173

# Frontend production build
cd frontend && npm run build
```

### Render deployment
`START_BACKENDS` env var selects which service to run (`main` or `backoffice`).

## Architecture

### Three-tier structure
```
frontend/          → React 18 + Vite (user-facing UI)
backend/           → FastAPI (main app, port 5000)
backoffice/        → FastAPI admin panel + React dashboard (port 5001)
run_backends.py    → Unified launcher for both APIs
```

### Backend layer pattern (both `backend/` and `backoffice/backend/`)
```
routers/     → HTTP route handlers, thin — delegate to services
services/    → Business logic, external integrations
models/      → SQLAlchemy ORM models
schemas/     → Pydantic request/response validation
middleware/  → JWT auth, error handling, security headers, request size limit
dependencies/→ FastAPI dependency injection (auth, DB session)
config/      → settings.py (Pydantic from .env), database.py (psycopg3 raw), database_orm.py (SQLAlchemy async)
```

### Database setup
Two DB connection modes coexist:
- `database.py` — raw psycopg3 connection pool (used in performance-critical services)
- `database_orm.py` — SQLAlchemy async ORM (used where ORM models are preferred)

### Key external integrations
| Service | Usage |
|---------|-------|
| Tavus AI | AI video interview avatars (`tavus_service.py`) |
| OpenAI + LangChain | GPT coaching, resume analysis, RAG pipelines |
| Qdrant | Vector embeddings for job/user semantic matching |
| Firebase | Google Auth, push notifications |
| Redis | Caching recommendations and session data |
| Cloudinary/R2 | Image and video storage |
| Resend | Transactional email |

### Frontend structure
```
src/pages/       → Route-level components (Feed, Jobs, LMS, AIInterviews, Messages, etc.)
src/components/  → Reusable UI components
src/contexts/    → AuthContext (JWT state), ThemeContext
src/utils/       → Helpers (analytics, AI chat formatting)
```

Authentication state lives in `AuthContext.jsx` and propagates via `ProtectedRoute.jsx`.

## Environment Setup

Copy `.env.example` to `.env` at root and `backoffice/.env.example` to `backoffice/.env`. Key variables:

- `START_BACKENDS` — which service(s) to start
- `ZEDREQ_PORT` / `BACKOFFICE_PORT` — service ports
- `DB_HOST/PORT/NAME/USER/PASSWORD` — PostgreSQL credentials
- `JWT_SECRET_KEY` — JWT signing secret
- `CORS_ORIGINS` — comma-separated allowed frontend URLs
- `OPENAI_API_KEY`, `TAVUS_API_KEY`, `QDRANT_URL` — AI service credentials
- `FIREBASE_PROJECT_ID` — Firebase config

## No Tests Currently

There is no test framework configuration (`pytest.ini`, `conftest.py`, `tests/` directory) in this codebase.
