"""
Security headers middleware for FastAPI.
Adds security headers to all responses to protect against common attacks.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger("pathway.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Legacy XSS protection (browsers)
    - Strict-Transport-Security: Enforces HTTPS
    - Referrer-Policy: Controls referrer information
    - Content-Security-Policy: Restricts resource loading
    - Permissions-Policy: Restricts browser features
    """

    def __init__(
        self,
        app: ASGIApp,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        frame_options: str = "DENY",
        content_type_options: str = "nosniff",
        xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        csp_policy: str | None = None,
        permissions_policy: str | None = None,
    ):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.frame_options = frame_options
        self.content_type_options = content_type_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy

        # Default CSP policy - restrictive but allows necessary functionality
        self.csp_policy = csp_policy or self._default_csp()

        # Default Permissions-Policy
        self.permissions_policy = permissions_policy or self._default_permissions_policy()

    def _default_csp(self) -> str:
        """
        Default Content-Security-Policy.
        Restricts loading of resources to same origin and trusted sources.
        """
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # May need adjustment for frontend
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data:",
            "connect-src 'self' https://api.anthropic.com https://api.openai.com https://api.deepseek.com https://api.github.com https://accounts.google.com https://oauth2.googleapis.com https://www.googleapis.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "object-src 'none'",
        ])

    def _default_permissions_policy(self) -> str:
        """
        Default Permissions-Policy.
        Restricts access to sensitive browser features.
        """
        return ", ".join([
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=()",
            "battery=()",
            "camera=(self)",  # Allow camera for video interviews
            "display-capture=()",
            "document-domain=()",
            "encrypted-media=()",
            "fullscreen=(self)",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=(self)",  # Allow microphone for video interviews
            "midi=()",
            "payment=()",
            "picture-in-picture=()",
            "publickey-credentials-get=()",
            "screen-wake-lock=()",
            "sync-xhr=()",
            "usb=()",
            "xr-spatial-tracking=()",
        ])

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = self.content_type_options
        response.headers["X-Frame-Options"] = self.frame_options
        response.headers["X-XSS-Protection"] = self.xss_protection
        response.headers["Referrer-Policy"] = self.referrer_policy

        # Content-Security-Policy
        if self.csp_policy:
            response.headers["Content-Security-Policy"] = self.csp_policy

        # Permissions-Policy
        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy

        # HSTS - only add if enabled (should only be used in production with HTTPS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains"

        # Remove potentially dangerous headers
        if "Server" in response.headers:
            del response.headers["Server"]

        return response


def get_security_middleware(debug: bool = False) -> SecurityHeadersMiddleware:
    """
    Get security headers middleware with appropriate settings.

    Args:
        debug: If True, relaxes some security headers for development
    """
    if debug:
        # More permissive settings for development
        return SecurityHeadersMiddleware(
            app=None,  # Will be set by FastAPI
            enable_hsts=False,  # Don't enforce HTTPS in dev
            csp_policy="; ".join([
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https: blob: http:",
                "font-src 'self' data:",
                "connect-src *",  # Allow any connection in dev
                "frame-ancestors 'self'",
            ]),
        )
    else:
        # Production settings
        return SecurityHeadersMiddleware(app=None)
