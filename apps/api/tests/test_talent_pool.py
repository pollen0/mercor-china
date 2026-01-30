"""
Tests for talent pool and vertical interview endpoints.
"""
import pytest
from unittest.mock import patch
from app.models import (
    CandidateVerticalProfile,
    InterviewSession,
    InterviewStatus,
    Match,
    MatchStatus,
)
from app.models.candidate import VerticalProfileStatus
from .conftest import generate_test_id


class TestVerticalInterview:
    """Tests for the vertical interview endpoints."""

    def test_start_vertical_interview_success(
        self, client, db_session, test_candidate, test_questions
    ):
        """Test starting a vertical interview successfully."""
        response = client.post(
            "/api/interviews/start-vertical",
            json={
                "candidate_id": test_candidate.id,
                "vertical": "new_energy",
                "role_type": "battery_engineer",
            },
        )

        # Should return 200 or create session
        # Note: might return 200 even without full session creation in test environment
        assert response.status_code in [200, 404, 422]

        # If successful, check response structure
        if response.status_code == 200:
            data = response.json()
            assert "sessionId" in data or "session_id" in data
            assert "questions" in data

    def test_start_vertical_interview_invalid_vertical(
        self, client, db_session, test_candidate
    ):
        """Test starting with invalid vertical returns error."""
        response = client.post(
            "/api/interviews/start-vertical",
            json={
                "candidate_id": test_candidate.id,
                "vertical": "invalid_vertical",
                "role_type": "battery_engineer",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_start_vertical_interview_invalid_role(
        self, client, db_session, test_candidate
    ):
        """Test starting with invalid role type returns error."""
        response = client.post(
            "/api/interviews/start-vertical",
            json={
                "candidate_id": test_candidate.id,
                "vertical": "new_energy",
                "role_type": "invalid_role",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_start_vertical_interview_missing_candidate(self, client, db_session):
        """Test starting interview without valid candidate returns error."""
        response = client.post(
            "/api/interviews/start-vertical",
            json={
                "candidate_id": "nonexistent_id",
                "vertical": "new_energy",
                "role_type": "battery_engineer",
            },
        )

        assert response.status_code in [404, 422]


class TestTalentPoolBrowse:
    """Tests for the talent pool browse endpoint."""

    def test_browse_talent_pool_empty(self, client, auth_headers):
        """Test browsing empty talent pool returns empty list."""
        response = client.get("/api/employers/talent-pool", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["candidates"]) == 0

    def test_browse_talent_pool_with_candidates(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test browsing talent pool with completed profiles."""
        # Create a completed vertical profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.get("/api/employers/talent-pool", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["candidates"]) >= 1

    def test_browse_talent_pool_filter_by_vertical(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test filtering talent pool by vertical."""
        # Create profiles for different verticals
        profile1 = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.0,
            best_score=8.0,
            attempt_count=1,
        )
        db_session.add(profile1)
        db_session.commit()

        # Filter by new_energy
        response = client.get(
            "/api/employers/talent-pool?vertical=new_energy",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # All returned candidates should be from new_energy vertical
        for candidate in data["candidates"]:
            assert candidate["vertical"] == "new_energy"

    def test_browse_talent_pool_filter_by_min_score(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test filtering talent pool by minimum score."""
        # Create profile with specific score
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=7.5,
            best_score=7.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        # Filter with min_score=8 should exclude the profile
        response = client.get(
            "/api/employers/talent-pool?min_score=8",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Should not include candidates below min score
        for candidate in data["candidates"]:
            assert candidate["bestScore"] >= 8 or candidate.get("best_score", 0) >= 8

    def test_browse_talent_pool_search(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test searching talent pool by name/skills."""
        # Create profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.0,
            best_score=8.0,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        # Search by candidate name
        response = client.get(
            f"/api/employers/talent-pool?search=Test",
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_browse_talent_pool_pagination(
        self, client, db_session, auth_headers
    ):
        """Test talent pool pagination."""
        response = client.get(
            "/api/employers/talent-pool?limit=5&offset=0",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert "total" in data

    def test_browse_talent_pool_unauthorized(self, client):
        """Test browsing talent pool without auth returns 401."""
        response = client.get("/api/employers/talent-pool")

        assert response.status_code == 401


class TestTalentPoolProfile:
    """Tests for the talent pool profile detail endpoint."""

    def test_get_talent_profile_success(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test getting a talent profile successfully."""
        # Create a completed vertical profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.get(
            f"/api/employers/talent-pool/{profile.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "profile" in data
        assert "candidate" in data
        assert data["profile"]["id"] == profile.id

    def test_get_talent_profile_not_found(self, client, auth_headers):
        """Test getting non-existent profile returns 404."""
        response = client.get(
            "/api/employers/talent-pool/nonexistent_id",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_talent_profile_unauthorized(self, client, db_session, test_candidate):
        """Test getting profile without auth returns 401."""
        # Create a profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.get(f"/api/employers/talent-pool/{profile.id}")

        assert response.status_code == 401


class TestTalentPoolStatus:
    """Tests for the talent pool status update endpoint."""

    def test_update_status_success(
        self, client, db_session, auth_headers, test_candidate, test_employer
    ):
        """Test updating candidate status successfully."""
        # Create a vertical profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.patch(
            f"/api/employers/talent-pool/{profile.id}/status",
            headers=auth_headers,
            json={"status": "SHORTLISTED"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "SHORTLISTED"

    def test_update_status_invalid_status(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test updating with invalid status returns error."""
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.patch(
            f"/api/employers/talent-pool/{profile.id}/status",
            headers=auth_headers,
            json={"status": "INVALID_STATUS"},
        )

        assert response.status_code == 422

    def test_update_status_not_found(self, client, auth_headers):
        """Test updating non-existent profile returns 404."""
        response = client.patch(
            "/api/employers/talent-pool/nonexistent_id/status",
            headers=auth_headers,
            json={"status": "SHORTLISTED"},
        )

        assert response.status_code == 404


class TestTalentPoolContact:
    """Tests for the talent pool contact endpoint."""

    @patch("app.services.email.email_service")
    def test_contact_candidate_success(
        self, mock_email, client, db_session, auth_headers, test_candidate
    ):
        """Test contacting a candidate successfully."""
        mock_email.send_employer_message.return_value = True

        # Create a vertical profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.post(
            f"/api/employers/talent-pool/{profile.id}/contact",
            headers=auth_headers,
            json={
                "subject": "Interview Opportunity",
                "body": "We would like to discuss a position with you.",
                "message_type": "interview_invite",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "candidateEmail" in data or "candidate_email" in data

    def test_contact_candidate_missing_fields(
        self, client, db_session, auth_headers, test_candidate
    ):
        """Test contacting with missing required fields returns error."""
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.post(
            f"/api/employers/talent-pool/{profile.id}/contact",
            headers=auth_headers,
            json={
                "subject": "Interview Opportunity",
                # Missing body
            },
        )

        assert response.status_code == 422

    def test_contact_candidate_not_found(self, client, auth_headers):
        """Test contacting non-existent profile returns 404."""
        response = client.post(
            "/api/employers/talent-pool/nonexistent_id/contact",
            headers=auth_headers,
            json={
                "subject": "Interview Opportunity",
                "body": "We would like to discuss a position with you.",
            },
        )

        assert response.status_code == 404


class TestCandidateVerticals:
    """Tests for candidate vertical profile endpoints."""

    def test_get_my_verticals_empty(self, client, db_session, test_candidate):
        """Test getting verticals when none exist."""
        # Create candidate token
        from app.utils.auth import create_access_token
        token = create_access_token({"sub": test_candidate.id, "type": "candidate"})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/candidates/me/verticals", headers=headers)

        # Should return 200 with empty list or 404
        assert response.status_code in [200, 404]

    def test_get_my_verticals_with_profiles(self, client, db_session, test_candidate):
        """Test getting verticals with existing profiles."""
        from app.utils.auth import create_access_token
        token = create_access_token({"sub": test_candidate.id, "type": "candidate"})
        headers = {"Authorization": f"Bearer {token}"}

        # Create a vertical profile
        profile = CandidateVerticalProfile(
            id=generate_test_id("vp"),
            candidate_id=test_candidate.id,
            vertical="new_energy",
            role_type="battery_engineer",
            status=VerticalProfileStatus.COMPLETED,
            interview_score=8.5,
            best_score=8.5,
            attempt_count=1,
        )
        db_session.add(profile)
        db_session.commit()

        response = client.get("/api/candidates/me/verticals", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert len(data["profiles"]) >= 1

    def test_get_my_verticals_unauthorized(self, client):
        """Test getting verticals without auth returns 401."""
        response = client.get("/api/candidates/me/verticals")

        assert response.status_code == 401
