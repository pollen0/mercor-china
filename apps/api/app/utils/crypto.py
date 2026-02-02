"""
Encryption utilities for sensitive data like OAuth tokens.
Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
"""
import logging
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

from ..config import settings

logger = logging.getLogger("pathway.crypto")

# Cache the Fernet instance
_fernet: Optional[Fernet] = None


def _get_fernet() -> Optional[Fernet]:
    """
    Get or create the Fernet encryption instance.
    Returns None if encryption key is not configured.
    """
    global _fernet

    if _fernet is not None:
        return _fernet

    if not settings.encryption_key:
        logger.warning("ENCRYPTION_KEY not set - token encryption disabled")
        return None

    try:
        # Validate and use the key
        key = settings.encryption_key.encode()

        # If the key isn't a valid Fernet key (32 bytes base64), derive one from it
        try:
            _fernet = Fernet(key)
        except Exception:
            # Derive a valid key from the provided secret
            derived_key = base64.urlsafe_b64encode(
                hashlib.sha256(key).digest()
            )
            _fernet = Fernet(derived_key)

        return _fernet
    except Exception as e:
        logger.error(f"Failed to initialize encryption: {e}")
        return None


def encrypt_token(plaintext: str) -> str:
    """
    Encrypt a token (e.g., GitHub OAuth access token).

    Args:
        plaintext: The token to encrypt

    Returns:
        Encrypted token string (base64 encoded)
        If encryption is not configured, returns the plaintext with a prefix
    """
    if not plaintext:
        return plaintext

    fernet = _get_fernet()

    if fernet is None:
        # Encryption not configured - store with prefix to identify unencrypted tokens
        logger.warning("Storing token without encryption (ENCRYPTION_KEY not set)")
        return f"plain:{plaintext}"

    try:
        encrypted = fernet.encrypt(plaintext.encode())
        return f"enc:{encrypted.decode()}"
    except Exception as e:
        logger.error(f"Token encryption failed: {e}")
        # Fall back to plaintext with prefix
        return f"plain:{plaintext}"


def decrypt_token(encrypted: str) -> str:
    """
    Decrypt a token.

    Args:
        encrypted: The encrypted token string

    Returns:
        Decrypted plaintext token
        Handles both encrypted and legacy plaintext tokens
    """
    if not encrypted:
        return encrypted

    # Handle prefixed tokens
    if encrypted.startswith("enc:"):
        fernet = _get_fernet()
        if fernet is None:
            logger.error("Cannot decrypt token - ENCRYPTION_KEY not set")
            raise ValueError("Encryption key not configured")

        try:
            encrypted_data = encrypted[4:].encode()  # Remove "enc:" prefix
            return fernet.decrypt(encrypted_data).decode()
        except InvalidToken:
            logger.error("Token decryption failed - invalid token or wrong key")
            raise ValueError("Failed to decrypt token - key may have changed")
        except Exception as e:
            logger.error(f"Token decryption error: {e}")
            raise ValueError(f"Token decryption failed: {e}")

    elif encrypted.startswith("plain:"):
        # Unencrypted token (logged warning when stored)
        return encrypted[6:]  # Remove "plain:" prefix

    else:
        # Legacy token without prefix - assume plaintext for backwards compatibility
        logger.warning("Found legacy unencrypted token - consider re-encrypting")
        return encrypted


def is_token_encrypted(token: str) -> bool:
    """Check if a token is properly encrypted."""
    if not token:
        return False
    return token.startswith("enc:")


def rotate_token_encryption(old_token: str) -> str:
    """
    Re-encrypt a token with the current key.
    Useful when rotating encryption keys.

    Args:
        old_token: Token to re-encrypt (may be plaintext or encrypted with old key)

    Returns:
        Newly encrypted token
    """
    # First decrypt
    plaintext = decrypt_token(old_token)

    # Then encrypt with current key
    return encrypt_token(plaintext)
