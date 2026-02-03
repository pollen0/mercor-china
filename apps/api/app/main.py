import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .config import settings
from .database import init_db
from .routers import health, candidates, questions, interviews, employers, auth, admin, courses, activities, public, calendar, employer_calendar, team_members, scheduling_links, organizations
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

    # Initialize reminder scheduler
    try:
        from .services.reminder_scheduler import init_scheduler, shutdown_scheduler
        init_scheduler()
        logger.info("Reminder scheduler initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize reminder scheduler: {e}")

    logger.info("Pathway API started successfully")
    yield
    logger.info("Shutting down Pathway API...")

    # Shutdown scheduler
    try:
        from .services.reminder_scheduler import shutdown_scheduler
        shutdown_scheduler()
    except Exception as e:
        logger.warning(f"Failed to shutdown scheduler: {e}")


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

# Add security headers middleware
from .middleware.security import SecurityHeadersMiddleware
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=not settings.debug,  # Only enable HSTS in production
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

# Calendar integration (Google Calendar) - Candidates
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])

# Calendar integration (Google Calendar) - Employers
app.include_router(employer_calendar.router, prefix="/api/employers/calendar", tags=["employer-calendar"])

# Admin panel
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Courses & Transcripts
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])

# Activities, Clubs & Awards
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])

# Public endpoints (no auth required)
app.include_router(public.router, prefix="/api/public", tags=["public"])

# Team member management
app.include_router(team_members.router, prefix="/api/employers/team-members", tags=["team-members"])

# Scheduling links
app.include_router(scheduling_links.router, prefix="/api/employers/scheduling-links", tags=["scheduling-links"])

# Organizations (team collaboration)
app.include_router(organizations.router, tags=["organizations"])


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
            "calendar": "/api/calendar",
            "team_members": "/api/employers/team-members",
            "scheduling_links": "/api/employers/scheduling-links",
        }
    }


# Public scheduling endpoint (no auth required)
@app.get("/api/schedule/{slug}")
async def public_schedule_redirect(slug: str):
    """Redirect to the public scheduling endpoint."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/api/employers/scheduling-links/public/{slug}")
