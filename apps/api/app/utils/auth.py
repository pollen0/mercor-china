from datetime import datetime, timedelta
from typing import Optional, Any
import uuid
import hashlib
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..services.cache import cache_service

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
    """Create a JWT access token with unique ID for blacklisting."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiry_hours)

    # Add unique token ID (jti) for blacklisting on logout
    token_id = str(uuid.uuid4())
    to_encode.update({
        "exp": expire,
        "jti": token_id,
        "iat": datetime.utcnow(),
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def get_token_jti(token: str) -> Optional[str]:
    """Extract the JTI (token ID) from a token for blacklisting."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload.get("jti")
    except JWTError:
        # If token is invalid/expired, hash it as fallback
        return hashlib.sha256(token.encode()).hexdigest()[:32]


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        # Check if token is blacklisted (logged out)
        jti = payload.get("jti")
        if jti and cache_service.is_token_blacklisted(jti):
            return None

        return payload
    except JWTError:
        return None


def decode_token(token: str) -> dict[str, Any]:
    """Decode a JWT token without verification (for debugging)."""
    return jwt.get_unverified_claims(token)


def blacklist_token(token: str) -> bool:
    """
    Blacklist a token so it can no longer be used.
    Used for logout functionality.

    Args:
        token: The JWT token to blacklist

    Returns:
        True if successfully blacklisted
    """
    try:
        # Get the JTI from the token
        jti = get_token_jti(token)
        if not jti:
            return False

        # Get expiry time from token to set appropriate TTL
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False}  # Don't verify expiry, we want to blacklist even expired tokens
            )
            exp = payload.get("exp")
            if exp:
                # TTL = remaining time until expiry + small buffer
                remaining = int(exp - datetime.utcnow().timestamp())
                ttl = max(remaining + 60, 60)  # At least 60 seconds
            else:
                ttl = settings.jwt_expiry_hours * 3600  # Default to full expiry time
        except JWTError:
            ttl = settings.jwt_expiry_hours * 3600

        return cache_service.blacklist_token(jti, ttl)
    except Exception:
        return False


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


def create_refresh_token(
    subject: str,
    token_type: str = "employer",
) -> str:
    """
    Create a refresh token for a user.

    Refresh tokens have a longer expiry (30 days by default) and are used
    to obtain new access tokens without re-authentication.

    Args:
        subject: User ID (candidate or employer)
        token_type: Type of user ("candidate" or "employer")

    Returns:
        Refresh token string
    """
    refresh_token_id = str(uuid.uuid4())
    expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expiry_days)

    token_data = {
        "sub": subject,
        "type": token_type,
        "token_type": "refresh",
        "jti": refresh_token_id,
        "exp": expires,
        "iat": datetime.utcnow(),
    }

    refresh_token = jwt.encode(
        token_data,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )

    # Store refresh token in Redis for validation and revocation
    ttl_seconds = settings.refresh_token_expiry_days * 24 * 3600
    cache_service.set(
        f"refresh_token:{refresh_token_id}",
        {"user_id": subject, "user_type": token_type},
        ttl=ttl_seconds
    )

    return refresh_token


def verify_refresh_token(token: str) -> Optional[dict[str, Any]]:
    """
    Verify a refresh token and return its payload.

    Args:
        token: The refresh token to verify

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )

        # Verify this is a refresh token
        if payload.get("token_type") != "refresh":
            return None

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and cache_service.is_token_blacklisted(jti):
            return None

        # Verify token exists in Redis (hasn't been revoked)
        stored_data = cache_service.get(f"refresh_token:{jti}")
        if not stored_data:
            return None

        return payload
    except JWTError:
        return None


def revoke_refresh_token(token: str) -> bool:
    """
    Revoke a refresh token so it can no longer be used.

    Args:
        token: The refresh token to revoke

    Returns:
        True if successfully revoked
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}
        )

        jti = payload.get("jti")
        if not jti:
            return False

        # Remove from Redis storage
        cache_service.delete(f"refresh_token:{jti}")

        # Also blacklist it for good measure
        exp = payload.get("exp")
        if exp:
            remaining = int(exp - datetime.utcnow().timestamp())
            ttl = max(remaining + 60, 60)
        else:
            ttl = settings.refresh_token_expiry_days * 24 * 3600

        cache_service.blacklist_token(jti, ttl)
        return True
    except JWTError:
        return False


def revoke_all_user_tokens(user_id: str, user_type: str) -> int:
    """
    Revoke all refresh tokens for a user (useful for password change, security breach).

    Args:
        user_id: The user's ID
        user_type: "candidate" or "employer"

    Returns:
        Number of tokens revoked
    """
    # This would require tracking all tokens per user in Redis
    # For now, we rely on individual token revocation
    # A full implementation would use a Redis set per user
    return 0


def create_token_pair(
    subject: str,
    token_type: str = "employer",
) -> dict[str, str]:
    """
    Create both access and refresh tokens for a user.

    Args:
        subject: User ID (candidate or employer)
        token_type: Type of user ("candidate" or "employer")

    Returns:
        Dict with "access_token" and "refresh_token"
    """
    return {
        "access_token": create_token(subject, token_type),
        "refresh_token": create_refresh_token(subject, token_type),
    }


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
