"""
Tests for follow-up question endpoints.
"""
import os
import pytest
from fastapi import status

# Check if we're using SQLite (default in tests)
USING_SQLITE = os.environ.get("TEST_DATABASE_URL", "sqlite://").startswith("sqlite")

# Skip marker for tests requiring array support
requires_array = pytest.mark.skipif(
    USING_SQLITE,
    reason="SQLite does not support ARRAY type for generated_questions"
)


class TestGetFollowups:
    """Tests for getting follow-up questions."""

    def test_get_followups_no_followups(
        self, client, test_interview, mock_storage_service, candidate_auth_headers
    ):
        """Test getting followups when none exist."""
        response = client.get(
            f"/api/interviews/{test_interview.id}/followup?question_index=0",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["has_followups"] is False
        assert data["followup_questions"] == []

    def test_get_followups_practice_mode(
        self, client, db_session, test_candidate, test_job, candidate_auth_headers
    ):
        """Test that practice mode returns no followups."""
        from app.models import InterviewSession, InterviewStatus
        import uuid

        # Create practice session
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
            f"/api/interviews/{practice_session.id}/followup?question_index=0",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["has_followups"] is False

    def test_get_followups_session_not_found(self, client, candidate_auth_headers):
        """Test getting followups for nonexistent session."""
        response = client.get(
            "/api/interviews/nonexistent_session/followup?question_index=0",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @requires_array
    def test_get_followups_with_pending_queue(
        self, client, db_session, test_interview, candidate_auth_headers
    ):
        """Test getting followups when queue exists (PostgreSQL only)."""
        from app.models import FollowupQueue, FollowupQueueStatus
        import uuid

        # Create a followup queue
        queue = FollowupQueue(
            id=f"fq{uuid.uuid4().hex[:24]}",
            session_id=test_interview.id,
            question_index=0,
            generated_questions=["What specific challenges did you face?", "How did you measure success?"],
            status=FollowupQueueStatus.PENDING,
        )
        db_session.add(queue)
        db_session.commit()

        response = client.get(
            f"/api/interviews/{test_interview.id}/followup?question_index=0",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["has_followups"] is True
        assert len(data["followup_questions"]) == 2
        assert data["queue_id"] == queue.id


class TestAskFollowup:
    """Tests for asking follow-up questions."""

    @requires_array
    def test_ask_followup_success(
        self, client, db_session, test_interview, candidate_auth_headers
    ):
        """Test successfully asking a followup (PostgreSQL only)."""
        from app.models import FollowupQueue, FollowupQueueStatus
        import uuid

        queue = FollowupQueue(
            id=f"fq{uuid.uuid4().hex[:24]}",
            session_id=test_interview.id,
            question_index=0,
            generated_questions=["Follow-up question 1", "Follow-up question 2"],
            status=FollowupQueueStatus.PENDING,
        )
        db_session.add(queue)
        db_session.commit()

        response = client.post(
            f"/api/interviews/{test_interview.id}/followup/ask?question_index=0",
            headers=candidate_auth_headers,
            json={"followup_index": 0}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["question_text"] == "Follow-up question 1"
        assert data["is_followup"] is True
        assert data["followup_index"] == 0

        # Verify queue status updated
        db_session.refresh(queue)
        assert queue.status == FollowupQueueStatus.ASKED
        assert queue.selected_index == 0

    @requires_array
    def test_ask_followup_invalid_index(
        self, client, db_session, test_interview, candidate_auth_headers
    ):
        """Test asking followup with invalid index (PostgreSQL only)."""
        from app.models import FollowupQueue, FollowupQueueStatus
        import uuid

        queue = FollowupQueue(
            id=f"fq{uuid.uuid4().hex[:24]}",
            session_id=test_interview.id,
            question_index=0,
            generated_questions=["Only one question"],
            status=FollowupQueueStatus.PENDING,
        )
        db_session.add(queue)
        db_session.commit()

        response = client.post(
            f"/api/interviews/{test_interview.id}/followup/ask?question_index=0",
            headers=candidate_auth_headers,
            json={"followup_index": 5}  # Invalid index
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_ask_followup_no_queue(self, client, test_interview, candidate_auth_headers):
        """Test asking followup when no queue exists."""
        response = client.post(
            f"/api/interviews/{test_interview.id}/followup/ask?question_index=0",
            headers=candidate_auth_headers,
            json={"followup_index": 0}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_ask_followup_practice_mode(
        self, client, db_session, test_candidate, test_job, candidate_auth_headers
    ):
        """Test that practice mode cannot ask followups."""
        from app.models import InterviewSession, InterviewStatus
        import uuid

        practice_session = InterviewSession(
            id=f"i{uuid.uuid4().hex[:24]}",
            status=InterviewStatus.IN_PROGRESS,
            is_practice=True,
            candidate_id=test_candidate.id,
            job_id=test_job.id,
        )
        db_session.add(practice_session)
        db_session.commit()

        response = client.post(
            f"/api/interviews/{practice_session.id}/followup/ask?question_index=0",
            headers=candidate_auth_headers,
            json={"followup_index": 0}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSkipFollowup:
    """Tests for skipping follow-up questions."""

    @requires_array
    def test_skip_followup_success(
        self, client, db_session, test_interview, candidate_auth_headers
    ):
        """Test successfully skipping a followup (PostgreSQL only)."""
        from app.models import FollowupQueue, FollowupQueueStatus
        import uuid

        queue = FollowupQueue(
            id=f"fq{uuid.uuid4().hex[:24]}",
            session_id=test_interview.id,
            question_index=0,
            generated_questions=["Question 1", "Question 2"],
            status=FollowupQueueStatus.PENDING,
        )
        db_session.add(queue)
        db_session.commit()

        response = client.post(
            f"/api/interviews/{test_interview.id}/followup/skip?question_index=0",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "skipped"

        # Verify queue status
        db_session.refresh(queue)
        assert queue.status == FollowupQueueStatus.SKIPPED

    def test_skip_followup_no_queue(self, client, test_interview, candidate_auth_headers):
        """Test skipping when no followup queue exists."""
        response = client.post(
            f"/api/interviews/{test_interview.id}/followup/skip?question_index=0",
            headers=candidate_auth_headers
        )

        # Should succeed even without queue
        assert response.status_code == status.HTTP_200_OK

    def test_skip_followup_session_not_found(self, client, candidate_auth_headers):
        """Test skipping for nonexistent session."""
        response = client.post(
            "/api/interviews/nonexistent_session/followup/skip?question_index=0",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
