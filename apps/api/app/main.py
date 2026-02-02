import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .config import settings
from .database import init_db
from .routers import health, candidates, questions, interviews, employers, auth, admin, courses, activities, public
from .utils.rate_limit import limiter, rate_limit_exceeded_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("pathway")


def validate_required_env_vars():
    """Validate that required environment variables are set."""
    missing = []

    # Always required
    if not settings.database_url:
        missing.append("DATABASE_URL")

    # Required in production (not debug mode)
    if not settings.debug:
        if not settings.jwt_secret:
            missing.append("JWT_SECRET")
        if not settings.api_secret_key:
            missing.append("API_SECRET_KEY")

    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Warn about optional but recommended vars
    if not settings.anthropic_api_key and not settings.deepseek_api_key:
        logger.warning("Neither ANTHROPIC_API_KEY nor DEEPSEEK_API_KEY set - AI features will be disabled")
    if not settings.r2_account_id:
        logger.warning("R2_ACCOUNT_ID not set - video storage will fail")
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set - emails will be mocked")
    if not settings.admin_password:
        logger.warning("ADMIN_PASSWORD not set - admin endpoints will be inaccessible")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and validate config on startup."""
    validate_required_env_vars()
    logger.info("Starting Pathway API...")
    init_db()
    logger.info("Pathway API started successfully")
    yield
    logger.info("Shutting down Pathway API...")


app = FastAPI(
    title="Pathway API",
    description="AI-powered interview platform helping college students land their first job",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
app.include_router(health.router)

# Candidates
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])

# Interview questions
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])

# Interview sessions
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])

# Employers
app.include_router(employers.router, prefix="/api/employers", tags=["employers"])

# Authentication (verification)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Admin panel
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Courses & Transcripts
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])

# Activities, Clubs & Awards
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])

# Public endpoints (no auth required)
app.include_router(public.router, prefix="/api/public", tags=["public"])


@app.get("/")
async def root():
    return {
        "name": "Pathway API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "candidates": "/api/candidates",
            "questions": "/api/questions",
            "interviews": "/api/interviews",
            "employers": "/api/employers",
            "courses": "/api/courses",
            "activities": "/api/activities",
        }
    }
