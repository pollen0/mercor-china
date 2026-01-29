"""
Tests for invite token API endpoints.
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestValidateInviteToken:
    """Tests for invite token validation."""

    def test_validate_valid_token(self, client, test_invite, test_job, test_employer):
        """Test validating a valid invite token."""
        response = client.get(f"/api/interviews/invite/validate/{test_invite.token}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert data["job_id"] == test_job.id
        assert data["job_title"] == test_job.title

    def test_validate_invalid_token(self, client):
        """Test validating an invalid token."""
        response = client.get("/api/interviews/invite/validate/invalid_token_123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert "error" in data

    def test_validate_expired_token(self, client, db_session, test_job):
        """Test validating an expired token."""
        from app.models import InviteToken
        import uuid

        expired_invite = InviteToken(
            id=f"inv{uuid.uuid4().hex[:24]}",
            token="expired_token_123",
            job_id=test_job.id,
            expires_at=datetime.utcnow() - timedelta(days=1),
            is_active=True,
        )
        db_session.add(expired_invite)
        db_session.commit()

        response = client.get("/api/interviews/invite/validate/expired_token_123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert "expired" in data["error"].lower()

    def test_validate_maxed_out_token(self, client, db_session, test_job):
        """Test validating a token that has reached max uses."""
        from app.models import InviteToken
        import uuid

        maxed_invite = InviteToken(
            id=f"inv{uuid.uuid4().hex[:24]}",
            token="maxed_token_123",
            job_id=test_job.id,
            max_uses=5,
            used_count=5,
            is_active=True,
        )
        db_session.add(maxed_invite)
        db_session.commit()

        response = client.get("/api/interviews/invite/validate/maxed_token_123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert "limit" in data["error"].lower()

    def test_validate_inactive_token(self, client, db_session, test_job):
        """Test validating an inactive token."""
        from app.models import InviteToken
        import uuid

        inactive_invite = InviteToken(
            id=f"inv{uuid.uuid4().hex[:24]}",
            token="inactive_token_123",
            job_id=test_job.id,
            is_active=False,
        )
        db_session.add(inactive_invite)
        db_session.commit()

        response = client.get("/api/interviews/invite/validate/inactive_token_123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False


class TestRegisterAndStart:
    """Tests for candidate self-registration and interview start."""

    def test_register_and_start_new_candidate(self, client, test_invite, test_questions):
        """Test self-registration with valid invite."""
        response = client.post("/api/interviews/invite/register-and-start", json={
            "name": "New Candidate",
            "email": "newcandidate@test.com",
            "phone": "13900139000",
            "invite_token": test_invite.token,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data
        assert "questions" in data
        assert len(data["questions"]) > 0

    def test_register_and_start_existing_candidate(
        self, client, test_invite, test_candidate, test_questions
    ):
        """Test registration with existing candidate email."""
        response = client.post("/api/interviews/invite/register-and-start", json={
            "name": "Updated Name",
            "email": test_candidate.email,
            "phone": "13900139999",
            "invite_token": test_invite.token,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data

    def test_register_and_start_invalid_token(self, client):
        """Test registration with invalid token."""
        response = client.post("/api/interviews/invite/register-and-start", json={
            "name": "Test User",
            "email": "test@test.com",
            "phone": "13800138000",
            "invite_token": "invalid_token",
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_and_start_expired_token(self, client, db_session, test_job):
        """Test registration with expired token."""
        from app.models import InviteToken
        import uuid

        expired_invite = InviteToken(
            id=f"inv{uuid.uuid4().hex[:24]}",
            token="expired_register_token",
            job_id=test_job.id,
            expires_at=datetime.utcnow() - timedelta(days=1),
            is_active=True,
        )
        db_session.add(expired_invite)
        db_session.commit()

        response = client.post("/api/interviews/invite/register-and-start", json={
            "name": "Test User",
            "email": "test@test.com",
            "phone": "13800138000",
            "invite_token": "expired_register_token",
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "expired" in response.json()["detail"].lower()

    def test_register_and_start_increments_usage(
        self, client, test_invite, test_questions, db_session
    ):
        """Test that registration increments invite usage count."""
        initial_count = test_invite.used_count

        response = client.post("/api/interviews/invite/register-and-start", json={
            "name": "Test User",
            "email": "incrementtest@test.com",
            "phone": "13800138001",
            "invite_token": test_invite.token,
        })

        assert response.status_code == status.HTTP_200_OK

        db_session.refresh(test_invite)
        assert test_invite.used_count == initial_count + 1


class TestCreateInviteToken:
    """Tests for creating invite tokens."""

    def test_create_invite_token_success(self, client, auth_headers, test_job):
        """Test successful invite token creation."""
        response = client.post(
            f"/api/employers/jobs/{test_job.id}/invites",
            headers=auth_headers,
            json={"max_uses": 10, "expires_in_days": 7}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "token" in data
        assert "invite_url" in data
        assert data["max_uses"] == 10
        assert data["used_count"] == 0
        assert data["is_active"] is True
        assert data["job_id"] == test_job.id

    def test_create_invite_token_unlimited(self, client, auth_headers, test_job):
        """Test creating unlimited use invite token."""
        response = client.post(
            f"/api/employers/jobs/{test_job.id}/invites",
            headers=auth_headers,
            json={"max_uses": 0}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["max_uses"] == 0

    def test_create_invite_token_job_not_found(self, client, auth_headers):
        """Test creating invite for nonexistent job."""
        response = client.post(
            "/api/employers/jobs/nonexistent_job/invites",
            headers=auth_headers,
            json={"max_uses": 10}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_invite_token_unauthorized(self, client, test_job):
        """Test creating invite without authentication."""
        response = client.post(
            f"/api/employers/jobs/{test_job.id}/invites",
            json={"max_uses": 10}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListInviteTokens:
    """Tests for listing invite tokens."""

    def test_list_invite_tokens_success(self, client, auth_headers, test_job, test_invite):
        """Test listing invite tokens for a job."""
        response = client.get(
            f"/api/employers/jobs/{test_job.id}/invites",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tokens" in data
        assert data["total"] >= 1
        assert any(t["id"] == test_invite.id for t in data["tokens"])

    def test_list_invite_tokens_empty(self, client, auth_headers, db_session, test_employer):
        """Test listing tokens for job with no invites."""
        from app.models import Job
        import uuid

        new_job = Job(
            id=f"j{uuid.uuid4().hex[:24]}",
            title="New Job",
            description="Test",
            requirements=[],
            employer_id=test_employer.id,
        )
        db_session.add(new_job)
        db_session.commit()

        response = client.get(
            f"/api/employers/jobs/{new_job.id}/invites",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0

    def test_list_invite_tokens_job_not_found(self, client, auth_headers):
        """Test listing tokens for nonexistent job."""
        response = client.get(
            "/api/employers/jobs/nonexistent_job/invites",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteInviteToken:
    """Tests for deleting invite tokens."""

    def test_delete_invite_token_success(self, client, auth_headers, test_invite, db_session):
        """Test successful invite token deletion (deactivation)."""
        response = client.delete(
            f"/api/employers/invites/{test_invite.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        db_session.refresh(test_invite)
        assert test_invite.is_active is False

    def test_delete_invite_token_not_found(self, client, auth_headers):
        """Test deleting nonexistent invite."""
        response = client.delete(
            "/api/employers/invites/nonexistent_invite",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_invite_token_unauthorized(self, client, test_invite):
        """Test deleting invite without authentication."""
        response = client.delete(f"/api/employers/invites/{test_invite.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
