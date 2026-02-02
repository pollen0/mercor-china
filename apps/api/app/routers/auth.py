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

from passlib.context import CryptContext

from ..database import get_db
from ..models import Candidate, Employer
from ..services.email import email_service

logger = logging.getLogger("pathway.auth")
router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_token_expired(expires_at) -> bool:
    """Check if a verification token is expired, handling timezone-naive datetimes."""
    if not expires_at:
        return False
    # Make timezone-aware if needed
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    user_type: str  # "candidate" or "employer"


class ForgotPasswordResponse(BaseModel):
    success: bool
    message: str


class ResetPasswordRequest(BaseModel):
    token: str
    user_type: str  # "candidate" or "employer"
    new_password: str


class ResetPasswordResponse(BaseModel):
    success: bool
    message: str


# Helper functions
def generate_verification_token() -> str:
    """Generate a unique verification token."""
    return f"v{uuid.uuid4().hex}"


def get_token_expiry() -> datetime:
    """Get token expiry (24 hours from now)."""
    return datetime.now(timezone.utc) + timedelta(hours=24)


def generate_password_reset_token() -> str:
    """Generate a unique password reset token."""
    return f"r{uuid.uuid4().hex}"


def get_password_reset_expiry() -> datetime:
    """Get password reset token expiry (1 hour from now)."""
    return datetime.now(timezone.utc) + timedelta(hours=1)


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

        if is_token_expired(user.email_verification_expires_at):
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

        if is_token_expired(user.email_verification_expires_at):
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


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Request a password reset email.
    Always returns success to prevent email enumeration.
    """
    if data.user_type == "candidate":
        user = db.query(Candidate).filter(Candidate.email == data.email).first()

        if user:
            # Generate reset token
            token = generate_password_reset_token()
            user.password_reset_token = token
            user.password_reset_expires_at = get_password_reset_expiry()
            db.commit()

            # Send email in background
            background_tasks.add_task(
                email_service.send_password_reset_email,
                email=user.email,
                name=user.name,
                reset_token=token,
                user_type="candidate",
            )
            logger.info(f"Password reset email queued for candidate: {user.email}")

    elif data.user_type == "employer":
        user = db.query(Employer).filter(Employer.email == data.email).first()

        if user:
            # Generate reset token
            token = generate_password_reset_token()
            user.password_reset_token = token
            user.password_reset_expires_at = get_password_reset_expiry()
            db.commit()

            # Send email in background
            background_tasks.add_task(
                email_service.send_password_reset_email,
                email=user.email,
                name=user.company_name,
                reset_token=token,
                user_type="employer",
            )
            logger.info(f"Password reset email queued for employer: {user.email}")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type"
        )

    # Always return success to prevent email enumeration
    return ForgotPasswordResponse(
        success=True,
        message="If an account exists with this email, a password reset link will be sent."
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Reset password using token from email.
    """
    # Validate password
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    if data.user_type == "candidate":
        user = db.query(Candidate).filter(
            Candidate.password_reset_token == data.token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset link"
            )

        if is_token_expired(user.password_reset_expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link has expired. Please request a new one."
            )

        # Update password
        user.password_hash = pwd_context.hash(data.new_password)
        user.password_reset_token = None
        user.password_reset_expires_at = None
        db.commit()

        logger.info(f"Password reset successful for candidate: {user.email}")

        return ResetPasswordResponse(
            success=True,
            message="Password has been reset successfully. You can now log in."
        )

    elif data.user_type == "employer":
        user = db.query(Employer).filter(
            Employer.password_reset_token == data.token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset link"
            )

        if is_token_expired(user.password_reset_expires_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset link has expired. Please request a new one."
            )

        # Update password
        user.password = pwd_context.hash(data.new_password)
        user.password_reset_token = None
        user.password_reset_expires_at = None
        db.commit()

        logger.info(f"Password reset successful for employer: {user.email}")

        return ResetPasswordResponse(
            success=True,
            message="Password has been reset successfully. You can now log in."
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type"
        )
