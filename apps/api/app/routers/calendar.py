"""
Google Calendar integration endpoints.
Allows candidates and employers to connect their Google Calendar for scheduling.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..models import Candidate
from ..services.calendar import calendar_service
from ..utils.crypto import encrypt_token, decrypt_token
from ..utils.csrf import generate_csrf_token, validate_csrf_token

logger = logging.getLogger("pathway.calendar")
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


class CalendarStatusResponse(BaseModel):
    connected: bool
    connected_at: Optional[str] = None


class DisconnectResponse(BaseModel):
    success: bool
    message: str


class CreateMeetingRequest(BaseModel):
    title: str
    description: str
    start_time: datetime
    duration_minutes: int = 30
    attendee_emails: list[str]
    timezone: str = "America/Los_Angeles"


class CreateMeetingResponse(BaseModel):
    success: bool
    event_id: str
    calendar_link: str
    meet_link: Optional[str] = None


class CancelMeetingResponse(BaseModel):
    success: bool
    message: str


# Helper to get current candidate (simplified - you'd use proper auth middleware)
async def get_current_candidate(
    candidate_id: str = Query(..., description="Candidate ID"),
    db: Session = Depends(get_db),
) -> Candidate:
    """Get candidate by ID (placeholder for proper JWT auth)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/google/url", response_model=GoogleOAuthUrlResponse)
async def get_google_oauth_url():
    """
    Get Google OAuth URL for calendar authorization.
    Returns URL and state token (stored server-side for CSRF protection).
    """
    if not calendar_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar integration is not configured"
        )

    # Generate CSRF state token with proper storage
    state = generate_csrf_token(oauth_type="google_calendar", prefix="cal_")
    url = calendar_service.get_oauth_url(state)

    return GoogleOAuthUrlResponse(url=url, state=state)


@router.post("/google/callback", response_model=GoogleOAuthCallbackResponse)
async def google_oauth_callback(
    data: GoogleOAuthCallbackRequest,
    candidate: Candidate = Depends(get_current_candidate),
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

    if not validate_csrf_token(data.state, expected_type="google_calendar"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token. Please restart the OAuth flow."
        )

    try:
        # Exchange code for tokens
        tokens = await calendar_service.exchange_code(data.code)

        # Store encrypted tokens
        candidate.google_calendar_token = tokens["access_token"]
        candidate.google_calendar_refresh_token = tokens["refresh_token"]
        candidate.google_calendar_connected_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Google Calendar connected for candidate: {candidate.id}")

        return GoogleOAuthCallbackResponse(
            success=True,
            message="Google Calendar connected successfully"
        )

    except ValueError as e:
        logger.error(f"Google OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/google/status", response_model=CalendarStatusResponse)
async def get_calendar_status(
    candidate: Candidate = Depends(get_current_candidate),
):
    """Check if Google Calendar is connected."""
    connected = bool(candidate.google_calendar_token)

    return CalendarStatusResponse(
        connected=connected,
        connected_at=candidate.google_calendar_connected_at.isoformat() if candidate.google_calendar_connected_at else None
    )


@router.delete("/google/disconnect", response_model=DisconnectResponse)
async def disconnect_google_calendar(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Disconnect Google Calendar integration."""
    candidate.google_calendar_token = None
    candidate.google_calendar_refresh_token = None
    candidate.google_calendar_connected_at = None
    db.commit()

    logger.info(f"Google Calendar disconnected for candidate: {candidate.id}")

    return DisconnectResponse(
        success=True,
        message="Google Calendar disconnected successfully"
    )


@router.post("/meetings/create", response_model=CreateMeetingResponse)
async def create_meeting(
    data: CreateMeetingRequest,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Create a calendar event with Google Meet link.
    Requires connected Google Calendar.
    """
    if not candidate.google_calendar_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar is not connected. Please connect first."
        )

    try:
        # Calculate end time
        end_time = data.start_time + timedelta(minutes=data.duration_minutes)

        # Try to create the event
        try:
            result = await calendar_service.create_meeting_event(
                encrypted_access_token=candidate.google_calendar_token,
                title=data.title,
                description=data.description,
                start_time=data.start_time,
                end_time=end_time,
                attendee_emails=data.attendee_emails,
                timezone=data.timezone,
            )
        except ValueError as e:
            # Token might be expired, try refreshing
            if "Invalid access token" in str(e) or "401" in str(e):
                if candidate.google_calendar_refresh_token:
                    new_tokens = await calendar_service.refresh_access_token(
                        candidate.google_calendar_refresh_token
                    )
                    candidate.google_calendar_token = new_tokens["access_token"]
                    db.commit()

                    # Retry with new token
                    result = await calendar_service.create_meeting_event(
                        encrypted_access_token=candidate.google_calendar_token,
                        title=data.title,
                        description=data.description,
                        start_time=data.start_time,
                        end_time=end_time,
                        attendee_emails=data.attendee_emails,
                        timezone=data.timezone,
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Calendar authorization expired. Please reconnect."
                    )
            else:
                raise

        logger.info(f"Meeting created: {result['event_id']} for candidate {candidate.id}")

        return CreateMeetingResponse(
            success=True,
            event_id=result["event_id"],
            calendar_link=result["html_link"],
            meet_link=result.get("hangout_link"),
        )

    except ValueError as e:
        logger.error(f"Failed to create meeting: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/meetings/{event_id}", response_model=CancelMeetingResponse)
async def cancel_meeting(
    event_id: str,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Cancel a calendar event."""
    if not candidate.google_calendar_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar is not connected"
        )

    try:
        success = await calendar_service.cancel_event(
            encrypted_access_token=candidate.google_calendar_token,
            event_id=event_id,
        )

        if success:
            return CancelMeetingResponse(
                success=True,
                message="Meeting cancelled successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel meeting"
            )

    except ValueError as e:
        logger.error(f"Failed to cancel meeting: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
