"""
Rawbank Sentient Fraud Investigation Copilot
AI-Assisted Evidence-Grounded Forensic Investigation Platform
-----------------------------------------------------------------------------
FastAPI application orchestrating natural-language fraud investigation,
entity resolution, deterministic evidence retrieval, 3-tier forensic dossiers,
and citation-grounded LLM reasoning.
Zero ungrounded hallucinations. Zero raw database rows leaked.
"""

import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.config import settings
from backend.app.routers import (
    health_router,
    copilot_router,
    retrieval_router,
    evidence_router,
    entities_router,
    alerts_router,
    transactions_router,
    customers_router,
    devices_router,
    beneficiaries_router,
    search_router
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("rawbank_copilot")

# Initialize FastAPI application
app = FastAPI(
    title="Rawbank Sentient Fraud Investigation Copilot API",
    version=settings.app_version,
    description="""
# Rawbank Sentient Fraud Investigation Copilot ?" Investigation API

Backend API layer powering the **Sentient Fraud Investigation Copilot**.
Built on the **Phase 2 Synthetic Banking Database (2,500 records)**, **Phase 3 Deterministic Rules**,
and **Evidence-Grounded RAG & LLM Reasoning Layer**.

---

### Core Investigative Architecture:
* **The LLM is NOT the database**: Natural language queries resolve to verified entities and exact database evidence BEFORE reaching the reasoning model.
* **Deterministic Pre-Checks**: Authoritative mathematical risk scoring, scenario classification, and baseline metrics execute deterministically.
* **Citation & Evidence Grounding**: Every finding must reference concrete entities `[Source: ID]`. Zero ungrounded hallucination allowed.
* **3-Tier Evidence Dossiers**:
  * **Tier 1: EXACT DATA** (Immutable database records)
  * **Tier 2: CALCULATED** (Deterministic mathematical indicators & scores)
  * **Tier 3: RETRIEVED EVIDENCE** (Graph links, baseline comparisons, auth logs)
* **Zero PII Leakage / Local Demonstration**: Operates 100% locally with synthetic data in compliance with enterprise BFSI guidelines.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"]
)


# -----------------------------------------------------------------------------
# Global Exception Handlers
# -----------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_msg = errors[0].get("msg") if errors else "Invalid request parameters"
    loc = " -> ".join(str(l) for l in errors[0].get("loc", [])) if errors else "request"

    return JSONResponse(
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        content={
            "detail": f"Validation error at '{loc}': {first_msg}",
            "error_code": "VALIDATION_ERROR",
            "errors": exc.errors(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected internal server error occurred while processing the request.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# -----------------------------------------------------------------------------
# Root Information Endpoint
# -----------------------------------------------------------------------------
@app.get("/", tags=["Root"], summary="API Root Metadata")
def root_info():
    return {
        "service": "Rawbank Sentient Fraud Investigation Copilot API",
        "environment": settings.app_env,
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_check": "/api/health",
        "copilot": "/api/copilot/investigate",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# -----------------------------------------------------------------------------
# Mount Sub-Routers
# -----------------------------------------------------------------------------
app.include_router(health_router)
app.include_router(copilot_router)
app.include_router(retrieval_router)
app.include_router(evidence_router)
app.include_router(entities_router)
app.include_router(alerts_router)
app.include_router(transactions_router)
app.include_router(customers_router)
app.include_router(devices_router)
app.include_router(beneficiaries_router)
app.include_router(search_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
