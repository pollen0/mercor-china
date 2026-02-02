from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiry_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> dict[str, Any]:
    """Decode a JWT token without verification (for debugging)."""
    return jwt.get_unverified_claims(token)


def create_token(
    subject: str,
    token_type: str = "employer",
    expires_hours: Optional[int] = None,
) -> str:
    """
    Create a JWT token for a user.

    Args:
        subject: User ID (candidate or employer)
        token_type: Type of user ("candidate" or "employer")
        expires_hours: Token expiry in hours (defaults to settings)

    Returns:
        JWT token string
    """
    expires_delta = timedelta(hours=expires_hours or settings.jwt_expiry_hours)
    return create_access_token(
        data={
            "sub": subject,
            "type": token_type,
        },
        expires_delta=expires_delta,
    )


async def get_current_candidate(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency to get the current authenticated candidate.

    Validates JWT token and returns the Candidate object.
    Raises HTTPException if token is invalid or user is not a candidate.
    """
    from ..models.candidate import Candidate

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    if user_id is None:
        raise credentials_exception

    if token_type != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student authentication required",
        )

    candidate = db.query(Candidate).filter(Candidate.id == user_id).first()

    if candidate is None:
        raise credentials_exception

    return candidate


async def get_current_employer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency to get the current authenticated employer.

    Validates JWT token and returns the Employer object.
    Raises HTTPException if token is invalid or user is not an employer.
    """
    from ..models.employer import Employer

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    if user_id is None:
        raise credentials_exception

    if token_type != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer authentication required",
        )

    employer = db.query(Employer).filter(Employer.id == user_id).first()

    if employer is None:
        raise credentials_exception

    return employer


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency to get the current authenticated user (candidate or employer).

    Returns a tuple of (user_object, user_type).
    """
    from ..models.candidate import Candidate
    from ..models.employer import Employer

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    if user_id is None or token_type is None:
        raise credentials_exception

    if token_type == "candidate":
        user = db.query(Candidate).filter(Candidate.id == user_id).first()
    elif token_type == "employer":
        user = db.query(Employer).filter(Employer.id == user_id).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return user, token_type
