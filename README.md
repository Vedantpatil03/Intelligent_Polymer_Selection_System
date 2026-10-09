# Intelligent Polymer Selection and Recommendation System

This project is a full-stack polymer recommendation application that combines a deterministic weighted MCDM engine with a FastAPI backend and a React + Vite frontend. The recommendation logic remains the authoritative decision maker, while the Groq-backed PolyGuide AI layer provides explanation and chat interactions.

## Project architecture

- Frontend: React + Vite
- Backend: FastAPI + Uvicorn
- Database: MongoDB Atlas
- Recommendation engine: deterministic weighted MCDM in Python
- AI explanation: Groq API on the backend only

## Local development environment

### Frontend

Create a local frontend environment file with:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

This variable belongs in the frontend app and is used by Vite at build/runtime. Do not put MongoDB or Groq secrets in the frontend.

### Backend

Create a backend local environment file with:

```bash
MONGODB_URI=
MONGODB_DATABASE=polymer_selection_db
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
AUTH_SECRET_KEY=replace-with-a-long-random-secret
AUTH_SESSION_TTL_HOURS=24
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
FRONTEND_URL=
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

Variable notes:

- `MONGODB_URI`: MongoDB Atlas connection string for the backend only.
- `MONGODB_DATABASE`: database name to use inside MongoDB Atlas.
- `GROQ_API_KEY`: Groq API key used only on the backend.
- `GROQ_MODEL`: model used by the PolyGuide AI chat flow.
- `AUTH_SECRET_KEY`: long random signing secret used for HttpOnly authentication cookies. Keep this only in the backend environment.
- `AUTH_SESSION_TTL_HOURS`: authentication session lifetime.
- `CORS_ORIGINS`: allowed frontend origins for local FastAPI development. Add the deployed Vercel URL in Render as needed.
- `FRONTEND_URL`: optional production frontend URL for CORS on the backend and deployment configuration.
- `COOKIE_SECURE`: set to `true` on HTTPS Render/Vercel deployments; keep `false` for local HTTP development.
- `COOKIE_SAMESITE`: use `lax` locally and `none` when frontend/backend are on different HTTPS sites.

## Deployment notes

### Vercel (frontend)

Set the frontend environment variable in Vercel:

```bash
VITE_API_BASE_URL=https://your-render-backend-url
```

Use the deployed Render backend URL here, not a MongoDB connection string or Groq secret. Keep the app as a standard Vite SPA. If direct route access is needed for /, /recommendation, /custom, and /history, make sure the Vercel SPA fallback is enabled in the deployment settings.

### Render (backend)

Root directory: `backend`

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Environment variables to add in Render:

```bash
MONGODB_URI=
MONGODB_DATABASE=polymer_selection_db
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
AUTH_SECRET_KEY=replace-with-a-long-random-secret
AUTH_SESSION_TTL_HOURS=24
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-vercel-domain
FRONTEND_URL=https://your-vercel-domain
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

Do not commit real credentials to source control. Keep environment secrets only in the deployment platform.

## MongoDB Atlas

The project continues to use MongoDB Atlas as the source of truth for polymer master data, application records, and recommendation history. The backend loads the database from `MONGODB_URI` and `MONGODB_DATABASE` only.

MongoDB Atlas network access must allow Render's outbound IPs and local development access as required. Do not expose the MongoDB URL in the frontend or in any public repository file.

## Security and repository hygiene

The repository ignores common local secret and build artifacts, including `.env` files, `__pycache__`, compiled Python files, `venv`, and `node_modules`.

## Validation checklist

Before deployment, verify:

- Frontend builds successfully with `npm install` and `npm run build`
- Backend imports successfully with Python and loads environment variables from `.env`
- FastAPI app starts via `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- The `/health` endpoint responds with `{"status": "ok"}`
- MongoDB Atlas is reachable from the backend
- Groq is only used by the backend `/chat` route
- The deterministic MCDM recommendation pipeline is unchanged

## Important notes

- The engineering logic (constraints, scoring, rankings, and recommendation calculations) must remain unchanged.
- The Groq/GPT explanation layer is auxiliary and must not replace the deterministic recommendation engine.
- Keep the existing endpoints and MongoDB-backed history behavior intact.
