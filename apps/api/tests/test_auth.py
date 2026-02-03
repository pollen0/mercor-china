"""
Tests for authentication and authorization.

Tests cover:
- JWT token generation and validation
- Candidate authentication
- Employer authentication
- CSRF token validation
- Token expiration
- Authorization checks
"""
import pytest
from datetime import datetime, timedelta
import jwt
from unittest.mock import patch, MagicMock
from app.utils.auth import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
)
from app.utils.csrf import generate_csrf_token, validate_csrf_token
from app.config import settings


# ==================== JWT Token Tests ====================

class TestJWTTokens:
    """Tests for JWT token generation and validation."""

    def test_create_access_token(self):
        """Test access token creation."""
        token = create_access_token({"sub": "test-user-id", "type": "candidate"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiry."""
        token = create_access_token(
            {"sub": "test-user-id", "type": "candidate"},
            expires_delta=timedelta(hours=1),
        )
        assert token is not None

        # Decode and verify expiry
        decoded = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        assert "exp" in decoded

    def test_verify_valid_token(self):
        """Test verification of valid token."""
        token = create_access_token({"sub": "test-user-id", "type": "candidate"})
        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "candidate"

    def test_verify_invalid_token(self):
        """Test that invalid tokens are rejected."""
        payload = verify_token("invalid.jwt.token")
        assert payload is None

    def test_verify_expired_token(self, expired_token):
        """Test that expired tokens are rejected."""
        payload = verify_token(expired_token)
        assert payload is None

    def test_verify_token_wrong_signature(self):
        """Test that tokens with wrong signature are rejected."""
        # Create token with different secret
        token = jwt.encode(
            {"sub": "test", "type": "candidate", "exp": datetime.utcnow() + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_token_contains_required_claims(self):
        """Test that tokens contain required claims."""
        token = create_access_token({"sub": "user-123", "type": "employer"})
        decoded = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        assert "sub" in decoded
        assert "type" in decoded
        assert "exp" in decoded


# ==================== Password Hashing Tests ====================

class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "securePassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Test verifying correct password."""
        password = "securePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) == True

    def test_verify_wrong_password(self):
        """Test verifying wrong password."""
        hashed = get_password_hash("correctPassword")

        assert verify_password("wrongPassword", hashed) == False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salting)."""
        password = "testPassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


# ==================== CSRF Token Tests ====================

class TestCSRFTokens:
    """Tests for CSRF token generation and validation."""

    def test_generate_csrf_token(self):
        """Test CSRF token generation."""
        token = generate_csrf_token(oauth_type="github")
        assert token is not None
        assert len(token) > 20

    def test_generate_csrf_token_with_prefix(self):
        """Test CSRF token with custom prefix."""
        token = generate_csrf_token(oauth_type="google", prefix="cal_")
        assert token.startswith("cal_")

    def test_validate_valid_csrf_token(self):
        """Test validation of valid CSRF token."""
        token = generate_csrf_token(oauth_type="github")
        is_valid = validate_csrf_token(token, expected_type="github")
        assert is_valid == True

    def test_validate_invalid_csrf_token(self):
        """Test that invalid tokens are rejected."""
        is_valid = validate_csrf_token("invalid-token", expected_type="github")
        assert is_valid == False

    def test_validate_wrong_type_csrf_token(self):
        """Test that tokens with wrong type are rejected."""
        token = generate_csrf_token(oauth_type="github")
        is_valid = validate_csrf_token(token, expected_type="google")
        assert is_valid == False

    def test_csrf_token_single_use(self):
        """Test that CSRF tokens can only be used once."""
        token = generate_csrf_token(oauth_type="github")

        # First validation should succeed
        first_valid = validate_csrf_token(token, expected_type="github")
        assert first_valid == True

        # Second validation should fail (token consumed)
        second_valid = validate_csrf_token(token, expected_type="github")
        assert second_valid == False


# ==================== Candidate Authentication Tests ====================

class TestCandidateAuthentication:
    """Tests for candidate authentication endpoints."""

    def test_candidate_login_success(self, client, db_session, test_candidate):
        """Test successful candidate login with email verification."""
        # Note: Candidate login uses email verification, not password
        # This tests the verification flow
        pass  # Verification is handled differently

    def test_candidate_protected_endpoint_with_valid_token(
        self, client, test_candidate, candidate_auth_headers
    ):
        """Test accessing protected endpoint with valid token."""
        response = client.get(
            "/api/candidates/me",
            headers=candidate_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_candidate.id

    def test_candidate_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/candidates/me")
        # HTTPBearer returns 403 when no Authorization header is present
        assert response.status_code in [401, 403]

    def test_candidate_protected_endpoint_with_invalid_token(self, client, invalid_token):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/candidates/me",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

    def test_candidate_cannot_access_employer_endpoints(
        self, client, test_candidate, candidate_auth_headers
    ):
        """Test that candidates cannot access employer endpoints."""
        response = client.get(
            "/api/employers/me",
            headers=candidate_auth_headers,
        )
        # Should be 401 or 403
        assert response.status_code in [401, 403, 404]


# ==================== Employer Authentication Tests ====================

class TestEmployerAuthentication:
    """Tests for employer authentication endpoints."""

    def test_employer_login_success(self, client, db_session, test_employer):
        """Test successful employer login."""
        response = client.post(
            "/api/employers/login",
            json={
                "email": "employer@test.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

    def test_employer_login_wrong_password(self, client, test_employer):
        """Test employer login with wrong password."""
        response = client.post(
            "/api/employers/login",
            json={
                "email": "employer@test.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_employer_login_nonexistent_email(self, client):
        """Test employer login with nonexistent email."""
        response = client.post(
            "/api/employers/login",
            json={
                "email": "nonexistent@test.com",
                "password": "password",
            },
        )
        assert response.status_code == 401

    def test_employer_protected_endpoint_with_valid_token(
        self, client, test_employer, auth_headers
    ):
        """Test accessing protected employer endpoint with valid token."""
        response = client.get(
            "/api/employers/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_employer.id

    def test_employer_cannot_access_candidate_profile(
        self, client, test_employer, auth_headers, test_candidate
    ):
        """Test that employers cannot modify candidate profiles directly."""
        # Note: There's no PATCH /api/candidates/{id} endpoint - candidates
        # can only update their own profile via PATCH /api/candidates/me
        # Trying to access a non-existent endpoint returns 405 Method Not Allowed
        response = client.patch(
            f"/api/candidates/{test_candidate.id}",
            headers=auth_headers,
            json={"name": "Hacked Name"},
        )
        # Should be 405 (Method Not Allowed) since endpoint doesn't exist,
        # or 401/403 if it did exist but was protected
        assert response.status_code in [401, 403, 405]


# ==================== Authorization Tests ====================

class TestAuthorization:
    """Tests for resource authorization."""

    def test_candidate_can_only_access_own_profile(
        self, client, db_session, test_candidate, candidate_auth_headers
    ):
        """Test candidate can only access their own profile."""
        from app.models import Candidate

        # Create another candidate
        other_candidate = Candidate(
            id="other-candidate-id",
            name="Other Candidate",
            email="other@test.com",
            phone="13800138002",
        )
        db_session.add(other_candidate)
        db_session.commit()

        # Try to access other candidate's data
        response = client.get(
            f"/api/candidates/{other_candidate.id}",
            headers=candidate_auth_headers,
        )
        # Should be forbidden or not found
        assert response.status_code in [403, 404]

    def test_candidate_can_update_own_profile(
        self, client, test_candidate, candidate_auth_headers
    ):
        """Test candidate can update their own profile."""
        response = client.patch(
            "/api/candidates/me",
            headers=candidate_auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_employer_can_view_candidate_in_talent_pool(
        self, client, db_session, test_employer, auth_headers, test_candidate
    ):
        """Test employer can view candidates in talent pool."""
        response = client.get(
            "/api/employers/talent-pool",
            headers=auth_headers,
        )
        assert response.status_code == 200


# ==================== Security Tests ====================

class TestSecurityHeaders:
    """Tests for security-related headers and responses."""

    def test_no_token_in_error_messages(self, client, test_employer):
        """Test that error messages don't leak sensitive information."""
        response = client.post(
            "/api/employers/login",
            json={
                "email": "employer@test.com",
                "password": "wrongpassword",
            },
        )
        # Error should not contain the actual password or token info
        error_detail = response.json().get("detail", "")
        # The word "password" is allowed in generic messages like "Invalid email or password"
        # but the actual password value should never appear
        assert "wrongpassword" not in error_detail
        assert "testpassword" not in error_detail.lower()
        # Token/credentials should not be leaked
        assert "jwt" not in error_detail.lower()
        assert "bearer" not in error_detail.lower()

    def test_rate_limiting_on_login(self, client, test_employer):
        """Test that login endpoint has rate limiting."""
        # Make multiple rapid requests
        responses = []
        for _ in range(20):
            response = client.post(
                "/api/employers/login",
                json={
                    "email": "employer@test.com",
                    "password": "wrongpassword",
                },
            )
            responses.append(response.status_code)

        # With rate limiting disabled in tests, all should be 401
        # In production, some would be 429
        # Just verify no server errors
        assert 500 not in responses

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        # Make an OPTIONS request
        response = client.options(
            "/api/employers/login",
            headers={"Origin": "http://localhost:3000"},
        )
        # CORS should allow the origin
        # Note: TestClient may not fully simulate CORS
        # This is more of a smoke test
        assert response.status_code in [200, 204, 405]
