"""
Employer Google Calendar integration endpoints.
Allows employers to connect their Google Calendar for scheduling interviews.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import Employer
from ..services.calendar import calendar_service
from ..utils.auth import verify_token
from ..utils.csrf import generate_csrf_token, validate_csrf_token

logger = logging.getLogger("pathway.employer_calendar")
router = APIRouter()


# Request/Response schemas
class GoogleOAuthUrlResponse(BaseModel):
    url: str
    state: str


class GoogleOAuthCallbackRequest(BaseModel):
    code: str
    state: str


class GoogleOAuthCallbackResponse(BaseModel):
    success: bool
    message: str


class EmployerCalendarStatusResponse(BaseModel):
    connected: bool
    connected_at: Optional[str] = None


class DisconnectResponse(BaseModel):
    success: bool
    message: str


# Helper to get current employer
async def get_current_employer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Employer:
    """Get the current authenticated employer."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer_id = payload.get("sub")
    if not employer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token content",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return employer


@router.get("/google/url", response_model=GoogleOAuthUrlResponse)
async def get_google_oauth_url(
    employer: Employer = Depends(get_current_employer),
):
    """
    Get Google OAuth URL for calendar authorization.
    Returns URL and state token (stored server-side for CSRF protection).
    """
    if not calendar_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar integration is not configured"
        )

    # Generate CSRF state token with employer user binding
    state = generate_csrf_token(
        oauth_type="google_employer_calendar",
        user_id=employer.id,
        prefix="emp_"
    )
    url = calendar_service.get_oauth_url(state, is_employer=True)

    return GoogleOAuthUrlResponse(url=url, state=state)


@router.post("/google/callback", response_model=GoogleOAuthCallbackResponse)
async def google_oauth_callback(
    data: GoogleOAuthCallbackRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Handle Google OAuth callback and store tokens.
    Validates the CSRF state token server-side.
    """
    # Validate CSRF state token
    if not data.state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state token. Please restart the OAuth flow."
        )

    if not validate_csrf_token(
        data.state,
        expected_type="google_employer_calendar",
        user_id=employer.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token. Please restart the OAuth flow."
        )

    try:
        # Exchange code for tokens (use employer redirect URI)
        tokens = await calendar_service.exchange_code(data.code, is_employer=True)

        # Store encrypted tokens
        employer.google_calendar_token = tokens["access_token"]
        employer.google_calendar_refresh_token = tokens["refresh_token"]
        employer.google_calendar_connected_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Google Calendar connected for employer: {employer.id}")

        return GoogleOAuthCallbackResponse(
            success=True,
            message="Google Calendar connected successfully"
        )

    except ValueError as e:
        logger.error(f"Google OAuth callback failed for employer {employer.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/google/status", response_model=EmployerCalendarStatusResponse)
async def get_calendar_status(
    employer: Employer = Depends(get_current_employer),
):
    """Check if Google Calendar is connected for the employer."""
    connected = bool(employer.google_calendar_token)

    return EmployerCalendarStatusResponse(
        connected=connected,
        connected_at=employer.google_calendar_connected_at.isoformat() if employer.google_calendar_connected_at else None
    )


@router.delete("/google/disconnect", response_model=DisconnectResponse)
async def disconnect_google_calendar(
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """Disconnect Google Calendar integration for the employer."""
    employer.google_calendar_token = None
    employer.google_calendar_refresh_token = None
    employer.google_calendar_connected_at = None
    db.commit()

    logger.info(f"Google Calendar disconnected for employer: {employer.id}")

    return DisconnectResponse(
        success=True,
        message="Google Calendar disconnected successfully"
    )
