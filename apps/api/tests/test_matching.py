"""
Tests for matching and top candidates endpoints.
"""
import pytest
from fastapi import status


class TestTopCandidates:
    """Tests for top candidates endpoints."""

    def test_get_top_candidates_empty(self, client, auth_headers, test_job):
        """Test getting top candidates when none exist."""
        response = client.get(
            f"/api/employers/jobs/{test_job.id}/top-candidates",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_get_top_candidates_with_matches(
        self, client, auth_headers, db_session, test_job, test_candidate
    ):
        """Test getting top candidates with match records."""
        from app.models import Match, MatchStatus
        import uuid

        # Create a match
        match = Match(
            id=f"m{uuid.uuid4().hex[:24]}",
            candidate_id=test_candidate.id,
            job_id=test_job.id,
            score=85.0,
            status=MatchStatus.PENDING,
            overall_match_score=0.78,
            interview_score=85.0,
            skills_match_score=0.80,
            experience_match_score=0.75,
        )
        db_session.add(match)
        db_session.commit()

        response = client.get(
            f"/api/employers/jobs/{test_job.id}/top-candidates",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["candidate_id"] == test_candidate.id
        assert data[0]["overall_match_score"] == 0.78

    def test_get_top_candidates_excludes_rejected(
        self, client, auth_headers, db_session, test_job, test_candidate
    ):
        """Test that rejected candidates are excluded."""
        from app.models import Match, MatchStatus
        import uuid

        # Create a rejected match
        match = Match(
            id=f"m{uuid.uuid4().hex[:24]}",
            candidate_id=test_candidate.id,
            job_id=test_job.id,
            score=85.0,
            status=MatchStatus.REJECTED,
            overall_match_score=0.90,
        )
        db_session.add(match)
        db_session.commit()

        response = client.get(
            f"/api/employers/jobs/{test_job.id}/top-candidates",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0  # Rejected should not appear

    def test_get_top_candidates_respects_limit(
        self, client, auth_headers, db_session, test_job
    ):
        """Test that limit parameter works."""
        from app.models import Match, MatchStatus, Candidate
        import uuid

        # Create multiple candidates and matches
        for i in range(5):
            candidate = Candidate(
                id=f"c{uuid.uuid4().hex[:24]}",
                name=f"Candidate {i}",
                email=f"candidate{i}@test.com",
                phone=f"1380013800{i}",
                target_roles=None,  # Use None instead of [] for SQLite compatibility
            )
            db_session.add(candidate)
            db_session.flush()

            match = Match(
                id=f"m{uuid.uuid4().hex[:24]}",
                candidate_id=candidate.id,
                job_id=test_job.id,
                score=80.0 + i,
                status=MatchStatus.PENDING,
                overall_match_score=0.70 + (i * 0.05),
            )
            db_session.add(match)

        db_session.commit()

        response = client.get(
            f"/api/employers/jobs/{test_job.id}/top-candidates?limit=3",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_top_candidates_job_not_found(self, client, auth_headers):
        """Test getting top candidates for nonexistent job."""
        response = client.get(
            "/api/employers/jobs/nonexistent_job/top-candidates",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_top_candidates_unauthorized(self, client, test_job):
        """Test getting top candidates without authentication."""
        response = client.get(
            f"/api/employers/jobs/{test_job.id}/top-candidates"
        )

        # HTTPBearer returns 403 when no Authorization header is present
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestAllTopCandidates:
    """Tests for getting top candidates across all jobs."""

    def test_get_all_top_candidates_empty(self, client, auth_headers, test_job):
        """Test getting all top candidates when none exist."""
        response = client.get(
            "/api/employers/top-candidates",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {}

    def test_get_all_top_candidates_with_data(
        self, client, auth_headers, db_session, test_job, test_candidate
    ):
        """Test getting all top candidates with match data."""
        from app.models import Match, MatchStatus
        import uuid

        match = Match(
            id=f"m{uuid.uuid4().hex[:24]}",
            candidate_id=test_candidate.id,
            job_id=test_job.id,
            score=85.0,
            status=MatchStatus.SHORTLISTED,
            overall_match_score=0.85,
            interview_score=85.0,
        )
        db_session.add(match)
        db_session.commit()

        response = client.get(
            "/api/employers/top-candidates",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert test_job.id in data
        assert data[test_job.id]["job_title"] == test_job.title
        assert len(data[test_job.id]["candidates"]) == 1


class TestContactCandidate:
    """Tests for contacting candidates."""

    def test_contact_candidate_success(
        self, client, auth_headers, test_candidate
    ):
        """Test successfully contacting a candidate."""
        response = client.post(
            f"/api/employers/candidates/{test_candidate.id}/contact",
            headers=auth_headers,
            json={
                "subject": "Interview Invitation",
                "body": "We would like to invite you for an interview.",
                "message_type": "interview_request",
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["subject"] == "Interview Invitation"
        assert "id" in data

    def test_contact_candidate_with_job(
        self, client, auth_headers, test_candidate, test_job
    ):
        """Test contacting candidate with job reference."""
        response = client.post(
            f"/api/employers/candidates/{test_candidate.id}/contact",
            headers=auth_headers,
            json={
                "subject": "Position Update",
                "body": "Regarding your application for the position.",
                "message_type": "custom",
                "job_id": test_job.id,
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["job_id"] == test_job.id

    def test_contact_candidate_not_found(self, client, auth_headers):
        """Test contacting nonexistent candidate."""
        response = client.post(
            "/api/employers/candidates/nonexistent_candidate/contact",
            headers=auth_headers,
            json={
                "subject": "Test",
                "body": "Test message",
                "message_type": "custom",
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_contact_candidate_invalid_job(
        self, client, auth_headers, test_candidate
    ):
        """Test contacting candidate with invalid job reference."""
        response = client.post(
            f"/api/employers/candidates/{test_candidate.id}/contact",
            headers=auth_headers,
            json={
                "subject": "Test",
                "body": "Test message",
                "message_type": "custom",
                "job_id": "invalid_job_id",
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_contact_candidate_rejection_message(
        self, client, auth_headers, test_candidate
    ):
        """Test sending rejection message."""
        response = client.post(
            f"/api/employers/candidates/{test_candidate.id}/contact",
            headers=auth_headers,
            json={
                "subject": "Application Update",
                "body": "Thank you for your interest. Unfortunately...",
                "message_type": "rejection",
            }
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_contact_candidate_unauthorized(self, client, test_candidate):
        """Test contacting candidate without authentication."""
        response = client.post(
            f"/api/employers/candidates/{test_candidate.id}/contact",
            json={
                "subject": "Test",
                "body": "Test",
                "message_type": "custom",
            }
        )

        # HTTPBearer returns 403 when no Authorization header is present
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
