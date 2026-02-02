"""
Tests for interview API endpoints.
"""
import pytest
from fastapi import status
from io import BytesIO


class TestInterviewStart:
    """Tests for starting interviews."""

    def test_start_interview_success(self, client, test_candidate, test_job, test_questions):
        """Test successful interview start."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": test_job.id,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data
        assert "questions" in data
        assert len(data["questions"]) > 0
        assert data["job_title"] == test_job.title

    def test_start_interview_creates_default_questions(self, client, test_candidate, test_job):
        """Test that default questions are created if none exist."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": test_job.id,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["questions"]) > 0

    def test_start_interview_candidate_not_found(self, client, test_job):
        """Test starting interview with nonexistent candidate."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": "nonexistent_candidate",
            "job_id": test_job.id,
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_start_interview_job_not_found(self, client, test_candidate):
        """Test starting interview with nonexistent job."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": "nonexistent_job",
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_start_interview_returns_existing(self, client, test_interview, test_candidate, test_job, test_questions):
        """Test that starting interview returns existing active session."""
        response = client.post("/api/interviews/start", json={
            "candidate_id": test_candidate.id,
            "job_id": test_job.id,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == test_interview.id


class TestGetInterview:
    """Tests for getting interview details."""

    def test_get_interview_success(self, client, test_interview, mock_storage_service):
        """Test getting interview session details."""
        response = client.get(f"/api/interviews/{test_interview.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_interview.id
        assert data["status"] == "IN_PROGRESS"

    def test_get_interview_with_responses(self, client, completed_interview, mock_storage_service):
        """Test getting interview with response details."""
        response = client.get(f"/api/interviews/{completed_interview.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["responses"]) > 0
        assert data["responses"][0]["video_url"] is not None

    def test_get_interview_not_found(self, client):
        """Test getting nonexistent interview."""
        response = client.get("/api/interviews/nonexistent_id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetUploadUrl:
    """Tests for getting presigned upload URLs."""

    def test_get_upload_url_success(self, client, test_interview, mock_storage_service):
        """Test getting upload URL."""
        response = client.get(
            f"/api/interviews/{test_interview.id}/upload-url?question_index=0"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "upload_url" in data
        assert "storage_key" in data
        assert "expires_in" in data

    def test_get_upload_url_completed_interview(self, client, completed_interview, mock_storage_service):
        """Test getting upload URL for completed interview fails."""
        response = client.get(
            f"/api/interviews/{completed_interview.id}/upload-url?question_index=0"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_upload_url_not_found(self, client, mock_storage_service):
        """Test getting upload URL for nonexistent interview."""
        response = client.get(
            "/api/interviews/nonexistent_id/upload-url?question_index=0"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSubmitResponse:
    """Tests for submitting video responses."""

    def test_submit_response_with_video_key(
        self, client, test_interview, test_questions, mock_storage_service, mock_background_tasks
    ):
        """Test submitting response with pre-uploaded video key."""
        response = client.post(
            f"/api/interviews/{test_interview.id}/response?question_index=0&video_key=videos/test/video.webm"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response_id" in data
        assert data["question_index"] == 0
        assert data["status"] == "processing"

    def test_submit_response_with_file(
        self, client, test_interview, test_questions, mock_storage_service, mock_background_tasks
    ):
        """Test submitting response with video file upload."""
        video_content = BytesIO(b"fake video content")
        response = client.post(
            f"/api/interviews/{test_interview.id}/response?question_index=0",
            files={"video": ("video.webm", video_content, "video/webm")}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response_id" in data

    def test_submit_response_no_video(self, client, test_interview, test_questions):
        """Test submitting response without video fails."""
        response = client.post(
            f"/api/interviews/{test_interview.id}/response?question_index=0"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_response_completed_interview(
        self, client, completed_interview, mock_storage_service
    ):
        """Test submitting response to completed interview fails."""
        response = client.post(
            f"/api/interviews/{completed_interview.id}/response?question_index=0&video_key=test.webm"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_response_invalid_question_index(
        self, client, test_interview, test_questions, mock_storage_service
    ):
        """Test submitting response with invalid question index."""
        response = client.post(
            f"/api/interviews/{test_interview.id}/response?question_index=99&video_key=test.webm"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCompleteInterview:
    """Tests for completing interviews."""

    def test_complete_interview_success(
        self, client, test_interview, mock_storage_service, mock_background_tasks
    ):
        """Test completing interview."""
        response = client.post(f"/api/interviews/{test_interview.id}/complete")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_complete_interview_already_completed(self, client, completed_interview, mock_storage_service):
        """Test completing already completed interview fails."""
        response = client.post(f"/api/interviews/{completed_interview.id}/complete")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_complete_interview_not_found(self, client):
        """Test completing nonexistent interview."""
        response = client.post("/api/interviews/nonexistent_id/complete")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetResults:
    """Tests for getting interview results."""

    def test_get_results_success(self, client, completed_interview, mock_storage_service):
        """Test getting interview results."""
        response = client.get(f"/api/interviews/{completed_interview.id}/results")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == completed_interview.id
        assert data["status"] == "COMPLETED"
        assert data["total_score"] is not None
        assert len(data["responses"]) > 0

    def test_get_results_with_score_details(self, client, completed_interview, mock_storage_service):
        """Test that results include score details."""
        response = client.get(f"/api/interviews/{completed_interview.id}/results")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(r.get("score_details") is not None for r in data["responses"])

    def test_get_results_not_found(self, client):
        """Test getting results for nonexistent interview."""
        response = client.get("/api/interviews/nonexistent_id/results")

        assert response.status_code == status.HTTP_404_NOT_FOUND
