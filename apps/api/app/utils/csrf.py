"""
CSRF token management for OAuth flows.
Stores state tokens with TTL for validation on callback.
"""
import time
import secrets
import logging
from typing import Optional, Dict
from threading import Lock

logger = logging.getLogger("pathway.csrf")

# In-memory store with TTL (for production, use Redis)
# Format: {token: {"created_at": timestamp, "user_id": optional_user_id, "type": oauth_type}}
_csrf_store: Dict[str, dict] = {}
_store_lock = Lock()

# Token TTL in seconds (10 minutes for OAuth flows)
CSRF_TOKEN_TTL = 600

# Maximum tokens to store (prevent memory exhaustion)
MAX_TOKENS = 10000


def _cleanup_expired_tokens():
    """Remove expired tokens from store."""
    current_time = time.time()
    expired = [
        token for token, data in _csrf_store.items()
        if current_time - data["created_at"] > CSRF_TOKEN_TTL
    ]
    for token in expired:
        del _csrf_store[token]


def generate_csrf_token(
    oauth_type: str,
    user_id: Optional[str] = None,
    prefix: str = ""
) -> str:
    """
    Generate a CSRF state token for OAuth flows.

    Args:
        oauth_type: Type of OAuth (github, google_calendar, google_employer_calendar)
        user_id: Optional user ID to bind the token to
        prefix: Optional prefix for the token (e.g., "emp_" for employer)

    Returns:
        State token string
    """
    with _store_lock:
        # Cleanup old tokens periodically
        if len(_csrf_store) > MAX_TOKENS * 0.9:
            _cleanup_expired_tokens()

        # Generate secure random token
        random_part = secrets.token_urlsafe(32)
        token = f"{prefix}{random_part}" if prefix else random_part

        _csrf_store[token] = {
            "created_at": time.time(),
            "user_id": user_id,
            "type": oauth_type,
        }

        logger.debug(f"Generated CSRF token for {oauth_type}: {token[:16]}...")
        return token


def validate_csrf_token(
    token: str,
    expected_type: str,
    user_id: Optional[str] = None,
    consume: bool = True
) -> bool:
    """
    Validate a CSRF state token.

    Args:
        token: The state token to validate
        expected_type: Expected OAuth type
        user_id: Optional user ID to validate against
        consume: If True, remove token after validation (one-time use)

    Returns:
        True if valid, False otherwise
    """
    if not token:
        logger.warning("CSRF validation failed: empty token")
        return False

    with _store_lock:
        # Check if token exists
        if token not in _csrf_store:
            logger.warning(f"CSRF validation failed: token not found {token[:16]}...")
            return False

        data = _csrf_store[token]

        # Check expiration
        if time.time() - data["created_at"] > CSRF_TOKEN_TTL:
            del _csrf_store[token]
            logger.warning(f"CSRF validation failed: token expired {token[:16]}...")
            return False

        # Check type
        if data["type"] != expected_type:
            logger.warning(f"CSRF validation failed: type mismatch (expected {expected_type}, got {data['type']})")
            return False

        # Check user ID if provided
        if user_id and data.get("user_id") and data["user_id"] != user_id:
            logger.warning(f"CSRF validation failed: user ID mismatch")
            return False

        # Consume token (one-time use)
        if consume:
            del _csrf_store[token]

        logger.debug(f"CSRF token validated successfully: {token[:16]}...")
        return True


def get_token_data(token: str) -> Optional[dict]:
    """Get token data without consuming it."""
    with _store_lock:
        return _csrf_store.get(token)


# For testing - clear all tokens
def clear_all_tokens():
    """Clear all stored tokens (for testing only)."""
    with _store_lock:
        _csrf_store.clear()
