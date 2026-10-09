import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router, auth_router


def get_cors_origins():
    configured = os.getenv("CORS_ORIGINS")
    origins = []

    if configured:
        origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    else:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://polyguideai.vercel.app",
        ]

    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        frontend_url = frontend_url.strip()
        if frontend_url and frontend_url not in origins:
            origins.append(frontend_url)

    return origins


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Intelligent Polymer Material Selection API",

    description=(
        "API for intelligent polymer material "
        "selection and recommendation using "
        "weighted Multi-Criteria Decision Making (MCDM)."
    ),

    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=get_cors_origins(),

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# REGISTER ROUTES
# ============================================================

app.include_router(router)
app.include_router(auth_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message":
            "Intelligent Polymer Material Selection API",

        "status":
            "running",

        "docs":
            "/docs",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok"}