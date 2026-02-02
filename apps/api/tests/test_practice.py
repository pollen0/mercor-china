"""
Tests for practice mode interview endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


class TestPracticeMode:
    """Tests for practice mode interviews."""

    def test_start_practice_interview(self, client, test_candidate, test_job, test_questions):
        """Test starting a practice interview."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": test_job.id,
            "is_practice": True,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data
        assert data["is_practice"] is True
        assert "Practice" in data["job_title"]

    def test_practice_interview_not_reused(
        self, client, db_session, test_candidate, test_job, test_questions
    ):
        """Test that practice sessions are not reused (new session each time)."""
        # Start first practice interview
        response1 = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": test_job.id,
            "is_practice": True,
        })
        session_id_1 = response1.json()["session_id"]

        # Complete the first session
        client.post(f"/api/interviews/{session_id_1}/complete")

        # Start second practice interview
        response2 = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": test_job.id,
            "is_practice": True,
        })
        session_id_2 = response2.json()["session_id"]

        # Sessions should be different
        assert session_id_1 != session_id_2

    def test_practice_interview_without_job(self, client, test_candidate, test_questions):
        """Test starting practice interview without a specific job."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": None,
            "is_practice": True,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_practice"] is True
        assert data["job_title"] == "Practice Interview"


class TestPracticeFeedback:
    """Tests for practice mode immediate feedback."""

    def test_get_practice_feedback_not_practice_session(
        self, client, completed_interview, mock_storage_service
    ):
        """Test that practice feedback fails for non-practice sessions."""
        # completed_interview is not a practice session
        response = client.get(
            f"/api/interviews/{completed_interview.id}/practice-feedback/fake_response_id"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "practice" in response.json()["detail"].lower()

    def test_get_practice_feedback_session_not_found(self, client):
        """Test practice feedback for nonexistent session."""
        response = client.get(
            "/api/interviews/nonexistent_session/practice-feedback/fake_response_id"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_practice_feedback_response_not_found(
        self, client, db_session, test_candidate, test_job, test_questions
    ):
        """Test practice feedback for nonexistent response."""
        from app.models import InterviewSession, InterviewStatus
        import uuid

        # Create a practice session
        practice_session = InterviewSession(
            id=f"i{uuid.uuid4().hex[:24]}",
            status=InterviewStatus.IN_PROGRESS,
            is_practice=True,
            candidate_id=test_candidate.id,
            job_id=test_job.id,
        )
        db_session.add(practice_session)
        db_session.commit()

        response = client.get(
            f"/api/interviews/{practice_session.id}/practice-feedback/nonexistent_response"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPracticeExcludedFromEmployer:
    """Tests to ensure practice interviews are excluded from employer views."""

    def test_employer_dashboard_excludes_practice(
        self, client, auth_headers, db_session, test_candidate, test_job, test_questions
    ):
        """Test that dashboard stats exclude practice interviews."""
        from app.models import InterviewSession, InterviewStatus
        import uuid

        # Create a practice interview
        practice_session = InterviewSession(
            id=f"i{uuid.uuid4().hex[:24]}",
            status=InterviewStatus.COMPLETED,
            is_practice=True,
            total_score=80.0,
            candidate_id=test_candidate.id,
            job_id=test_job.id,
        )
        db_session.add(practice_session)
        db_session.commit()

        # Get dashboard stats
        response = client.get("/api/employers/dashboard", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Practice interview should not be counted
        assert data["total_interviews"] == 0

    def test_employer_interview_list_excludes_practice(
        self, client, auth_headers, db_session, test_candidate, test_job
    ):
        """Test that interview list excludes practice interviews."""
        from app.models import InterviewSession, InterviewStatus
        import uuid

        # Create a practice interview
        practice_session = InterviewSession(
            id=f"i{uuid.uuid4().hex[:24]}",
            status=InterviewStatus.COMPLETED,
            is_practice=True,
            total_score=80.0,
            candidate_id=test_candidate.id,
            job_id=test_job.id,
        )
        db_session.add(practice_session)
        db_session.commit()

        # List interviews
        response = client.get("/api/employers/interviews", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Practice interview should not appear in list
        assert not any(i["id"] == practice_session.id for i in data["interviews"])
