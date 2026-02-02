"""
Tests for question management endpoints.
"""
import pytest
from fastapi import status


class TestListQuestions:
    """Tests for listing questions."""

    def test_list_default_questions(self, client, test_questions):
        """Test listing default questions."""
        response = client.get("/api/questions/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "questions" in data
        assert data["total"] == len(test_questions)

    def test_list_questions_for_job(self, client, db_session, test_job, test_questions):
        """Test listing questions for a specific job."""
        response = client.get(f"/api/questions/?job_id={test_job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] > 0

    def test_list_questions_without_defaults(self, client, test_job, test_questions):
        """Test listing questions without defaults."""
        response = client.get(
            f"/api/questions/?job_id={test_job.id}&include_defaults=false"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only have job-specific questions (none in this case)
        assert all(
            q.get("job_id") == test_job.id or q.get("is_default") is False
            for q in data["questions"]
        )


class TestGetDefaultQuestions:
    """Tests for getting default questions."""

    def test_get_default_questions(self, client, test_questions):
        """Test getting default questions."""
        response = client.get("/api/questions/defaults")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == len(test_questions)
        assert all(q.get("is_default", True) for q in data["questions"])

    def test_get_default_questions_empty(self, client):
        """Test getting defaults when none exist."""
        response = client.get("/api/questions/defaults")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0


class TestGetJobQuestions:
    """Tests for getting job-specific questions."""

    def test_get_job_questions_returns_defaults(
        self, client, test_job, test_questions
    ):
        """Test that job questions endpoint returns defaults when no custom questions."""
        response = client.get(f"/api/questions/job/{test_job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should return defaults when no custom questions
        assert data["total"] == len(test_questions)

    def test_get_job_questions_not_found(self, client):
        """Test getting questions for nonexistent job."""
        response = client.get("/api/questions/job/nonexistent_job")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateQuestion:
    """Tests for creating questions."""

    def test_create_question_success(self, client, test_job):
        """Test creating a custom question."""
        response = client.post("/api/questions/", json={
            "text": "What is your biggest achievement?",
            "category": "behavioral",
            "order": 10,
            "job_id": test_job.id,
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["text"] == "What is your biggest achievement?"
        assert data["is_default"] is False
        assert data["job_id"] == test_job.id

    def test_create_question_minimal(self, client, test_job):
        """Test creating question with minimal data."""
        response = client.post("/api/questions/", json={
            "text": "Why should we hire you?",
            "category": "motivation",
            "order": 5,
            "job_id": test_job.id,
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_question_invalid_job(self, client):
        """Test creating question with invalid job ID."""
        response = client.post("/api/questions/", json={
            "text": "Test question",
            "category": "test",
            "order": 1,
            "job_id": "invalid_job",
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateQuestion:
    """Tests for updating questions."""

    def test_update_question_success(self, client, db_session, test_job):
        """Test updating a custom question."""
        from app.models import InterviewQuestion
        import uuid

        # Create a custom question first
        question = InterviewQuestion(
            id=f"q{uuid.uuid4().hex[:24]}",
            text="Original text",
            category="test",
            order=1,
            is_default=False,
            job_id=test_job.id,
        )
        db_session.add(question)
        db_session.commit()

        response = client.put(f"/api/questions/{question.id}", json={
            "text": "Updated text",
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["text"] == "Updated text"

    def test_update_default_question_fails(self, client, test_questions):
        """Test that updating default questions fails."""
        default_question = test_questions[0]

        response = client.put(f"/api/questions/{default_question.id}", json={
            "text": "Modified text",
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_question_not_found(self, client):
        """Test updating nonexistent question."""
        response = client.put("/api/questions/nonexistent_id", json={
            "text": "New text",
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteQuestion:
    """Tests for deleting questions."""

    def test_delete_question_success(self, client, db_session, test_job):
        """Test deleting a custom question."""
        from app.models import InterviewQuestion
        import uuid

        question = InterviewQuestion(
            id=f"q{uuid.uuid4().hex[:24]}",
            text="To be deleted",
            category="test",
            order=1,
            is_default=False,
            job_id=test_job.id,
        )
        db_session.add(question)
        db_session.commit()

        response = client.delete(f"/api/questions/{question.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_default_question_fails(self, client, test_questions):
        """Test that deleting default questions fails."""
        default_question = test_questions[0]

        response = client.delete(f"/api/questions/{default_question.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_question_not_found(self, client):
        """Test deleting nonexistent question."""
        response = client.delete("/api/questions/nonexistent_id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSeedDefaultQuestions:
    """Tests for seeding default questions."""

    def test_seed_defaults_creates_questions(self, client):
        """Test seeding default questions when none exist."""
        response = client.post("/api/questions/seed-defaults")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] > 0
        assert all(q.get("is_default", True) for q in data["questions"])

    def test_seed_defaults_returns_existing(self, client, test_questions):
        """Test that seeding returns existing defaults if they exist."""
        response = client.post("/api/questions/seed-defaults")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == len(test_questions)
