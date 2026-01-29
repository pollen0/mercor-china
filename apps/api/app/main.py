import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .config import settings
from .database import init_db
from .routers import health, candidates, questions, interviews, employers
from .utils.rate_limit import limiter, rate_limit_exceeded_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("zhimian")


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
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY not set - AI features will be disabled")
    if not settings.r2_account_id:
        logger.warning("R2_ACCOUNT_ID not set - video storage will fail")
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set - emails will be mocked")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and validate config on startup."""
    validate_required_env_vars()
    logger.info("Starting ZhiMian API...")
    init_db()
    logger.info("ZhiMian API started successfully")
    yield
    logger.info("Shutting down ZhiMian API...")


app = FastAPI(
    title="ZhiMian 智面 API",
    description="AI-powered video interview platform for China's job market",
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


@app.get("/")
async def root():
    return {
        "name": "ZhiMian 智面 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "candidates": "/api/candidates",
            "questions": "/api/questions",
            "interviews": "/api/interviews",
            "employers": "/api/employers",
        }
    }
