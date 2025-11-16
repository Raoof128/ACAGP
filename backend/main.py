"""
Australian Compliance Automation & Governance Platform (ACAGP)
Main FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize Sentry for error tracking (production)
if settings.sentry_dsn and settings.is_production:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=settings.sentry_traces_sample_rate,
        environment=settings.environment,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database connection pool
    # await init_db()

    # Initialize Prometheus metrics
    if settings.prometheus_enabled:
        logger.info("Prometheus metrics enabled")

    # Load ML models if enabled
    if settings.feature_ml_risk_prediction:
        logger.info("Loading ML risk prediction models")
        # await load_ml_models()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    # await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise-grade Compliance Automation & Governance Platform "
        "for Australian organisations. Automates compliance monitoring "
        "across APRA CPS 234, ASD Essential Eight, OAIC, PCI DSS, and ISO 27001."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add GZip middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Mount Prometheus metrics endpoint
if settings.prometheus_enabled:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "path": str(request.url),
        },
    )


@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.environment,
        "docs": "/docs",
        "api_prefix": settings.api_prefix,
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check endpoint.
    Returns 200 if application is ready to serve requests.
    """
    # TODO: Add database connection check
    # TODO: Add Redis connection check
    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected",
    }


# API Router imports (to be created)
# from api.v1 import compliance, reports, organizations, users, assessments

# Include API routers
# app.include_router(
#     compliance.router,
#     prefix=f"{settings.api_prefix}/compliance",
#     tags=["Compliance"]
# )
# app.include_router(
#     reports.router,
#     prefix=f"{settings.api_prefix}/reports",
#     tags=["Reports"]
# )
# app.include_router(
#     organizations.router,
#     prefix=f"{settings.api_prefix}/organizations",
#     tags=["Organizations"]
# )
# app.include_router(
#     users.router,
#     prefix=f"{settings.api_prefix}/users",
#     tags=["Users"]
# )
# app.include_router(
#     assessments.router,
#     prefix=f"{settings.api_prefix}/assessments",
#     tags=["Assessments"]
# )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
