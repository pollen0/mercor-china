"""
Authentication and email verification endpoints.
"""
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..models import Candidate, Employer
from ..services.email import email_service

logger = logging.getLogger("pathway.auth")
router = APIRouter()


# Schemas
class VerifyEmailRequest(BaseModel):
    token: str
    user_type: str  # "candidate" or "employer"


class VerifyEmailResponse(BaseModel):
    success: bool
    message: str
    user_type: str
    email: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr
    user_type: str  # "candidate" or "employer"


class ResendVerificationResponse(BaseModel):
    success: bool
    message: str


# Helper functions
def generate_verification_token() -> str:
    """Generate a unique verification token."""
    return f"v{uuid.uuid4().hex}"


def get_token_expiry() -> datetime:
    """Get token expiry (24 hours from now)."""
    return datetime.now(timezone.utc) + timedelta(hours=24)


def send_verification_email_background(
    email: str,
    name: str,
    token: str,
    user_type: str
):
    """Background task to send verification email."""
    try:
        email_service.send_verification_email(
            email=email,
            name=name,
            verification_token=token,
            user_type=user_type,
        )
        logger.info(f"Sent verification email to {email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")


# Public functions for use by other routers
def create_verification_for_candidate(
    candidate: Candidate,
    db: Session,
    background_tasks: BackgroundTasks,
):
    """Create verification token and send email for a candidate."""
    token = generate_verification_token()
    candidate.email_verification_token = token
    candidate.email_verification_expires_at = get_token_expiry()
    candidate.email_verified = False
    db.commit()

    background_tasks.add_task(
        send_verification_email_background,
        email=candidate.email,
        name=candidate.name,
        token=token,
        user_type="candidate",
    )


def create_verification_for_employer(
    employer: Employer,
    db: Session,
    background_tasks: BackgroundTasks,
):
    """Create verification token and send email for an employer."""
    token = generate_verification_token()
    employer.email_verification_token = token
    employer.email_verification_expires_at = get_token_expiry()
    employer.is_verified = False
    db.commit()

    background_tasks.add_task(
        send_verification_email_background,
        email=employer.email,
        name=employer.company_name,
        token=token,
        user_type="employer",
    )


# Endpoints
@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """
    Verify user email with token.
    """
    if data.user_type == "candidate":
        user = db.query(Candidate).filter(
            Candidate.email_verification_token == data.token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification link"
            )

        if user.email_verification_expires_at and user.email_verification_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link has expired. Please request a new one."
            )

        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_expires_at = None
        db.commit()

        return VerifyEmailResponse(
            success=True,
            message="Email verified successfully",
            user_type="candidate",
            email=user.email,
        )

    elif data.user_type == "employer":
        user = db.query(Employer).filter(
            Employer.email_verification_token == data.token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification link"
            )

        if user.email_verification_expires_at and user.email_verification_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link has expired. Please request a new one."
            )

        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires_at = None
        db.commit()

        return VerifyEmailResponse(
            success=True,
            message="Email verified successfully",
            user_type="employer",
            email=user.email,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type"
        )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    data: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Resend verification email.
    """
    if data.user_type == "candidate":
        user = db.query(Candidate).filter(Candidate.email == data.email).first()

        if not user:
            # Don't reveal if email exists
            return ResendVerificationResponse(
                success=True,
                message="If an account exists, a verification email will be sent."
            )

        if user.email_verified:
            return ResendVerificationResponse(
                success=True,
                message="Email is already verified"
            )

        create_verification_for_candidate(user, db, background_tasks)

        return ResendVerificationResponse(
            success=True,
            message="Verification email sent"
        )

    elif data.user_type == "employer":
        user = db.query(Employer).filter(Employer.email == data.email).first()

        if not user:
            return ResendVerificationResponse(
                success=True,
                message="If an account exists, a verification email will be sent."
            )

        if user.is_verified:
            return ResendVerificationResponse(
                success=True,
                message="Email is already verified"
            )

        create_verification_for_employer(user, db, background_tasks)

        return ResendVerificationResponse(
            success=True,
            message="Verification email sent"
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type"
        )


@router.get("/verification-status")
async def get_verification_status(
    email: str,
    user_type: str,
    db: Session = Depends(get_db),
):
    """
    Check if an email is verified.
    """
    if user_type == "candidate":
        user = db.query(Candidate).filter(Candidate.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"verified": user.email_verified}

    elif user_type == "employer":
        user = db.query(Employer).filter(Employer.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"verified": user.is_verified}

    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
