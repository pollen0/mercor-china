"""
Rate limiting utilities using slowapi.

Provides configurable rate limits for different endpoint types:
- Auth endpoints: Stricter limits to prevent brute force
- AI/Scoring endpoints: Moderate limits due to resource usage
- General endpoints: More relaxed limits
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


def get_client_ip(request: Request) -> str:
    """
    Get client IP, accounting for proxies.

    Checks X-Forwarded-For header first (for reverse proxies),
    then falls back to direct connection IP.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(key_func=get_client_ip)


# Rate limit presets
class RateLimits:
    """Predefined rate limit strings for different endpoint types."""

    # Auth endpoints - strict to prevent brute force
    AUTH_LOGIN = "5/minute"  # 5 login attempts per minute
    AUTH_REGISTER = "3/minute"  # 3 registration attempts per minute
    AUTH_WECHAT = "10/minute"  # 10 WeChat auth attempts per minute

    # AI/Resource-intensive endpoints
    AI_SCORING = "10/minute"  # Scoring requests
    AI_TRANSCRIPTION = "10/minute"  # Transcription requests
    AI_RESUME_PARSE = "5/minute"  # Resume parsing (expensive)

    # Interview endpoints
    INTERVIEW_START = "10/minute"  # Start interview
    INTERVIEW_SUBMIT = "30/minute"  # Submit responses

    # General CRUD operations
    CRUD_READ = "60/minute"  # Read operations
    CRUD_WRITE = "30/minute"  # Write operations

    # Bulk operations
    BULK_EXPORT = "5/minute"  # CSV exports
    BULK_ACTION = "10/minute"  # Bulk status updates

    # Default fallback
    DEFAULT = "100/minute"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.

    Returns a user-friendly JSON response in Chinese.
    """
    # Extract retry-after from the exception
    retry_after = getattr(exc, "retry_after", 60)

    return JSONResponse(
        status_code=429,
        content={
            "detail": "请求过于频繁，请稍后再试",
            "detail_en": "Too many requests, please try again later",
            "retry_after": retry_after,
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(exc.limit) if hasattr(exc, "limit") else "unknown",
        }
    )


def setup_rate_limiting(app):
    """
    Configure rate limiting for a FastAPI app.

    Call this in main.py after creating the app:
        setup_rate_limiting(app)
    """
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
