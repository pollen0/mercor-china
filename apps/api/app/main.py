import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .config import settings
from .database import init_db
from .routers import health, candidates, questions, interviews, employers, auth, admin, courses, activities, public, calendar, employer_calendar, team_members, scheduling_links, organizations, vibe_code, referrals
from .utils.rate_limit import limiter, rate_limit_exceeded_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("pathway")

# Silence noisy third-party loggers
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("s3transfer").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)


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


def _filter_model_keys(model_class, data: dict) -> dict:
    """Filter dict to only keys that are columns on the model."""
    from sqlalchemy import inspect
    valid_keys = {c.key for c in inspect(model_class).column_attrs}
    return {k: v for k, v in data.items() if k in valid_keys}


def auto_seed_data():
    """Auto-seed universities, courses, and clubs on startup if tables are empty."""
    from .database import SessionLocal
    from .models.course import University, Course
    from .models.activity import Club
    from .data.seed_courses import get_all_universities, get_all_courses
    from .data.seed_clubs import get_all_clubs

    db = SessionLocal()
    try:
        # Seed universities — batch check existing IDs
        existing_uni_ids = {r[0] for r in db.query(University.id).all()}
        universities = get_all_universities()
        added = 0
        for uni_data in universities:
            if uni_data["id"] not in existing_uni_ids:
                db.add(University(**uni_data))
                added += 1
        if added:
            db.commit()
            logger.info(f"Auto-seeded {added} new universities (total: {len(existing_uni_ids) + added})")

        # Seed courses — batch check existing IDs, filter unknown keys
        existing_course_ids = {r[0] for r in db.query(Course.id).all()}
        courses = get_all_courses()
        added = 0
        for course_data in courses:
            if course_data["id"] not in existing_course_ids:
                db.add(Course(**_filter_model_keys(Course, course_data)))
                added += 1
        if added:
            db.commit()
            logger.info(f"Auto-seeded {added} new courses (total: {len(existing_course_ids) + added})")

        # Seed clubs — batch check existing IDs, filter unknown keys
        existing_club_ids = {r[0] for r in db.query(Club.id).all()}
        clubs_data = get_all_clubs()
        added = 0
        for club_data in clubs_data:
            if club_data["id"] not in existing_club_ids:
                db.add(Club(**_filter_model_keys(Club, club_data)))
                added += 1
        if added:
            db.commit()
            logger.info(f"Auto-seeded {added} new clubs (total: {len(existing_club_ids) + added})")

    except Exception as e:
        db.rollback()
        logger.warning(f"Auto-seed failed (non-fatal): {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and validate config on startup."""
    validate_required_env_vars()
    logger.info("Starting Pathway API...")
    init_db()

    # Auto-seed universities, courses, and clubs
    try:
        auto_seed_data()
    except Exception as e:
        logger.warning(f"Auto-seed failed (non-fatal): {e}")

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

# Vibe Code Sessions (AI coding session analysis)
app.include_router(vibe_code.router, prefix="/api/vibe-code", tags=["vibe-code"])

# Referral system
app.include_router(referrals.router, prefix="/api/referrals", tags=["referrals"])


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
            "vibe_code": "/api/vibe-code",
            "referrals": "/api/referrals",
        }
    }


# Public scheduling endpoint (no auth required)
@app.get("/api/schedule/{slug}")
async def public_schedule_redirect(slug: str):
    """Redirect to the public scheduling endpoint."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/api/employers/scheduling-links/public/{slug}")
