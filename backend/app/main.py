"""BizTwin FastAPI Application Entrypoint."""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any, List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import init_db
from app.routers import health, analyses, dashboard, locations, uploads

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("biztwin")

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Lifecycle manager: initializes database tables safely on application startup."""
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database tables: %s", e)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "BizTwin API — AI-powered Business Feasibility and Location Intelligence Platform. "
        "Evaluates commercial feasibility, location intelligence, and financial projections for new or expanding businesses."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if isinstance(settings.cors_origins, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Ensure every request has a traceable request ID."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Standardized Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Normalize Pydantic validation errors preserving field-level details."""
    request_id = getattr(request.state, "request_id", None)
    details: List[dict] = []

    for err in exc.errors():
        # Exclude 'body' from loc prefix if present for cleaner field paths
        loc = [str(x) for x in err.get("loc", []) if x != "body"]
        field_path = ".".join(loc) if loc else None
        details.append({
            "field": field_path,
            "message": err.get("msg", "Invalid value"),
        })

    logger.warning("Validation error on %s %s: %s", request.method, request.url.path, details)

    return JSONResponse(
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "One or more fields are invalid.",
                "details": details,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Normalize HTTP exceptions into the standard envelope."""
    request_id = getattr(request.state, "request_id", None)
    code = f"HTTP_{exc.status_code}"
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "BAD_REQUEST"
    elif exc.status_code == status.HTTP_409_CONFLICT:
        code = "CONFLICT"
    elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        code = "INTERNAL_SERVER_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
                "details": None,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler: logs exception internally and returns a safe sanitized response."""
    request_id = getattr(request.state, "request_id", None)
    logger.exception("Unhandled server exception on %s %s [request_id=%s]", request.method, request.url.path, request_id)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please contact support with the request ID.",
                "details": None,
                "request_id": request_id,
            }
        },
    )


# Include Routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(analyses.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(locations.router, prefix=settings.api_prefix)
app.include_router(uploads.router, prefix=settings.api_prefix)
