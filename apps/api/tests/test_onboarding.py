"""
Comprehensive tests for user onboarding flows.

Tests both student and employer registration, login, email verification,
and GitHub OAuth integration.
"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone


class TestStudentRegistration:
    """Tests for student registration flow."""

    def test_register_student_with_university(self, client):
        """Test successful student registration with university info."""
        response = client.post("/api/candidates/", json={
            "name": "John Smith",
            "email": "john.smith@berkeley.edu",
            "password": "securepassword123",
            "university": "UC Berkeley",
            "major": "Computer Science",
            "graduation_year": 2026,
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "candidate" in data
        assert "token" in data
        assert data["candidate"]["name"] == "John Smith"
        assert data["candidate"]["email"] == "john.smith@berkeley.edu"
        assert data["candidate"]["university"] == "UC Berkeley"
        assert data["candidate"]["major"] == "Computer Science"
        assert data["candidate"]["graduation_year"] == 2026

    def test_register_student_minimal(self, client):
        """Test student registration with minimal required fields."""
        response = client.post("/api/candidates/", json={
            "name": "Jane Doe",
            "email": "jane.doe@test.com",
            "password": "password123",
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["candidate"]["name"] == "Jane Doe"
        assert data["candidate"]["university"] is None

    def test_register_student_duplicate_email(self, client, test_candidate):
        """Test registration with existing email fails."""
        response = client.post("/api/candidates/", json={
            "name": "Another Person",
            "email": test_candidate.email,
            "password": "password123",
        })

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "email already exists" in response.json()["detail"].lower()

    def test_register_student_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post("/api/candidates/", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123",
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_student_weak_password(self, client):
        """Test registration with short password."""
        response = client.post("/api/candidates/", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "123",  # Too short
        })

        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_student_returns_token(self, client):
        """Test that registration returns a valid JWT token."""
        response = client.post("/api/candidates/", json={
            "name": "Token Test",
            "email": "token.test@example.com",
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 20  # JWT tokens are long

    def test_register_student_with_all_fields(self, client):
        """Test registration with all optional fields."""
        response = client.post("/api/candidates/", json={
            "name": "Complete Profile",
            "email": "complete@stanford.edu",
            "password": "securepassword123",
            "university": "Stanford University",
            "major": "Computer Science",
            "graduation_year": 2027,  # Must be 2026 or later
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["candidate"]["university"] == "Stanford University"


class TestStudentLogin:
    """Tests for student login flow."""

    def test_login_success(self, client, db_session):
        """Test successful student login."""
        # First register a student
        from app.models import Candidate
        from app.utils.auth import get_password_hash
        import uuid

        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Login Test",
            email="login.test@example.com",
            password_hash=get_password_hash("testpassword123"),
        )
        db_session.add(candidate)
        db_session.commit()

        # Now login
        response = client.post("/api/candidates/login", json={
            "email": "login.test@example.com",
            "password": "testpassword123",
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert "candidate" in data
        assert data["candidate"]["email"] == "login.test@example.com"

    def test_login_wrong_password(self, client, db_session):
        """Test login with wrong password."""
        from app.models import Candidate
        from app.utils.auth import get_password_hash
        import uuid

        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Wrong Pass Test",
            email="wrongpass@example.com",
            password_hash=get_password_hash("correctpassword"),
        )
        db_session.add(candidate)
        db_session.commit()

        response = client.post("/api/candidates/login", json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email(self, client):
        """Test login with email that doesn't exist."""
        response = client.post("/api/candidates/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_github_only_user(self, client, db_session):
        """Test login for user who registered via GitHub."""
        from app.models import Candidate
        import uuid

        # Create user without password (GitHub OAuth user)
        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="GitHub User",
            email="github.user@example.com",
            password_hash=None,  # No password for GitHub users
            github_username="githubuser",
        )
        db_session.add(candidate)
        db_session.commit()

        response = client.post("/api/candidates/login", json={
            "email": "github.user@example.com",
            "password": "anypassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "github" in response.json()["detail"].lower()


class TestEmployerRegistration:
    """Tests for employer registration flow."""

    def test_register_employer_success(self, client):
        """Test successful employer registration."""
        response = client.post("/api/employers/register", json={
            "company_name": "Tech Corp",
            "email": "hr@techcorp.com",
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "employer" in data
        assert "token" in data
        assert data["employer"]["company_name"] == "Tech Corp"
        assert data["employer"]["email"] == "hr@techcorp.com"

    def test_register_employer_duplicate_email(self, client, test_employer):
        """Test employer registration with existing email."""
        response = client.post("/api/employers/register", json={
            "company_name": "Another Corp",
            "email": test_employer.email,
            "password": "password123",
        })

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_employer_returns_token(self, client):
        """Test that employer registration returns JWT token."""
        response = client.post("/api/employers/register", json={
            "company_name": "Token Corp",
            "email": "token@corp.com",
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 20


class TestEmployerLogin:
    """Tests for employer login flow."""

    def test_login_success(self, client, test_employer):
        """Test successful employer login."""
        response = client.post("/api/employers/login", json={
            "email": test_employer.email,
            "password": "testpassword123",
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert "employer" in data

    def test_login_wrong_password(self, client, test_employer):
        """Test employer login with wrong password."""
        response = client.post("/api/employers/login", json={
            "email": test_employer.email,
            "password": "wrongpassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email(self, client):
        """Test employer login with nonexistent email."""
        response = client.post("/api/employers/login", json={
            "email": "nonexistent@corp.com",
            "password": "anypassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEmailVerification:
    """Tests for email verification flow."""

    def test_verify_candidate_email(self, client, db_session):
        """Test email verification for student."""
        from app.models import Candidate
        import uuid

        # Create unverified candidate with token
        token = f"v{uuid.uuid4().hex}"
        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Unverified User",
            email="unverified@example.com",
            password_hash="hashed",
            email_verified=False,
            email_verification_token=token,
            email_verification_expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(candidate)
        db_session.commit()

        # Verify email
        response = client.post("/api/auth/verify-email", json={
            "token": token,
            "user_type": "candidate",
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["email"] == "unverified@example.com"

        # Check database was updated
        db_session.refresh(candidate)
        assert candidate.email_verified is True
        assert candidate.email_verification_token is None

    def test_verify_employer_email(self, client, db_session):
        """Test email verification for employer."""
        from app.models import Employer
        from app.utils.auth import get_password_hash
        import uuid

        token = f"v{uuid.uuid4().hex}"
        employer = Employer(
            id=f"e{uuid.uuid4().hex[:24]}",
            company_name="Unverified Corp",
            email="unverified@corp.com",
            password=get_password_hash("password"),
            is_verified=False,
            email_verification_token=token,
            email_verification_expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(employer)
        db_session.commit()

        response = client.post("/api/auth/verify-email", json={
            "token": token,
            "user_type": "employer",
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True

        db_session.refresh(employer)
        assert employer.is_verified is True

    def test_verify_expired_token(self, client, db_session):
        """Test verification with expired token."""
        from app.models import Candidate
        import uuid

        token = f"v{uuid.uuid4().hex}"
        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Expired Token User",
            email="expired@example.com",
            password_hash="hashed",
            email_verified=False,
            email_verification_token=token,
            email_verification_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
        )
        db_session.add(candidate)
        db_session.commit()

        response = client.post("/api/auth/verify-email", json={
            "token": token,
            "user_type": "candidate",
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "expired" in response.json()["detail"].lower()

    def test_verify_invalid_token(self, client):
        """Test verification with invalid token."""
        response = client.post("/api/auth/verify-email", json={
            "token": "invalid_token_12345",
            "user_type": "candidate",
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_resend_verification_email(self, client, db_session):
        """Test resending verification email."""
        from app.models import Candidate
        import uuid

        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Resend Test",
            email="resend@example.com",
            password_hash="hashed",
            email_verified=False,
        )
        db_session.add(candidate)
        db_session.commit()

        response = client.post("/api/auth/resend-verification", json={
            "email": "resend@example.com",
            "user_type": "candidate",
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True


class TestGitHubOAuth:
    """Tests for GitHub OAuth integration."""

    def test_get_github_auth_url(self, client):
        """Test getting GitHub OAuth URL."""
        with patch("app.services.github.github_service.is_configured", return_value=True):
            with patch("app.services.github.github_service.get_auth_url", return_value="https://github.com/login/oauth/authorize?..."):
                response = client.get("/api/candidates/auth/github/url")

                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "auth_url" in data
                assert "state" in data
                assert "github.com" in data["auth_url"]

    def test_github_not_configured(self, client):
        """Test GitHub auth when not configured."""
        with patch("app.services.github.github_service.is_configured", return_value=False):
            response = client.get("/api/candidates/auth/github/url")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_github_callback_success(self, client, db_session):
        """Test GitHub OAuth callback for authenticated user."""
        from app.models import Candidate
        from app.utils.auth import create_token
        import uuid

        # Create authenticated candidate
        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="GitHub Connect Test",
            email="github.connect@example.com",
            password_hash="hashed",
        )
        db_session.add(candidate)
        db_session.commit()

        token = create_token(candidate.id, "candidate", 24)

        # Mock GitHub service
        with patch("app.services.github.github_service.is_configured", return_value=True):
            with patch("app.services.github.github_service.exchange_code_for_token", return_value="mock_access_token"):
                with patch("app.services.github.github_service.get_full_profile", return_value={
                    "username": "testuser",
                    "public_repos": 10,
                    "languages": {"Python": 50000, "JavaScript": 30000},
                    "top_repos": [{"name": "awesome-project", "stars": 100}],
                }):
                    response = client.post(
                        "/api/candidates/auth/github/callback",
                        json={"code": "mock_code"},
                        headers={"Authorization": f"Bearer {token}"}
                    )

                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["success"] is True
                    assert data["github_username"] == "testuser"

    def test_github_callback_duplicate_account(self, client, db_session):
        """Test GitHub callback when account already connected to another user."""
        from app.models import Candidate
        from app.utils.auth import create_token
        import uuid

        # Create first user with GitHub connected
        existing = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Existing GitHub User",
            email="existing@example.com",
            password_hash="hashed",
            github_username="testuser",
        )
        db_session.add(existing)

        # Create second user trying to connect same GitHub
        new_user = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="New User",
            email="new@example.com",
            password_hash="hashed",
        )
        db_session.add(new_user)
        db_session.commit()

        token = create_token(new_user.id, "candidate", 24)

        with patch("app.services.github.github_service.is_configured", return_value=True):
            with patch("app.services.github.github_service.exchange_code_for_token", return_value="mock_token"):
                with patch("app.services.github.github_service.get_full_profile", return_value={
                    "username": "testuser",  # Same username as existing
                }):
                    response = client.post(
                        "/api/candidates/auth/github/callback",
                        json={"code": "mock_code"},
                        headers={"Authorization": f"Bearer {token}"}
                    )

                    assert response.status_code == status.HTTP_409_CONFLICT


class TestAuthenticatedAccess:
    """Tests for authenticated endpoint access."""

    def test_get_profile_authenticated(self, client, db_session):
        """Test getting profile with valid token."""
        from app.models import Candidate
        from app.utils.auth import create_token
        import uuid

        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Auth Test",
            email="auth.test@example.com",
            password_hash="hashed",
        )
        db_session.add(candidate)
        db_session.commit()

        token = create_token(candidate.id, "candidate", 24)

        response = client.get(
            "/api/candidates/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "auth.test@example.com"

    def test_get_profile_no_token(self, client):
        """Test getting profile without token."""
        response = client.get("/api/candidates/me")

        # API returns 403 when no token is provided
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token."""
        response = client.get(
            "/api/candidates/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_employer_dashboard_authenticated(self, client, test_employer, employer_token):
        """Test employer dashboard access with valid token."""
        response = client.get(
            "/api/employers/dashboard",
            headers={"Authorization": f"Bearer {employer_token}"}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_employer_dashboard_no_token(self, client):
        """Test employer dashboard without token."""
        response = client.get("/api/employers/dashboard")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProfileUpdate:
    """Tests for profile update functionality."""

    def test_update_student_profile(self, client, db_session):
        """Test updating student profile."""
        from app.models import Candidate
        from app.utils.auth import create_token
        import uuid

        candidate = Candidate(
            id=f"c{uuid.uuid4().hex[:24]}",
            name="Update Test",
            email="update.test@example.com",
            password_hash="hashed",
        )
        db_session.add(candidate)
        db_session.commit()

        token = create_token(candidate.id, "candidate", 24)

        response = client.patch(
            "/api/candidates/me",
            json={
                "university": "MIT",
                "major": "Computer Science",
                "graduation_year": 2027,
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["university"] == "MIT"
        assert data["major"] == "Computer Science"
        assert data["graduation_year"] == 2027
