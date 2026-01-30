"""
Tests for bulk actions and export endpoints.
"""
import pytest
from fastapi import status


class TestBulkActions:
    """Tests for bulk interview actions."""

    def test_bulk_shortlist_success(
        self, client, auth_headers, completed_interview, mock_storage_service
    ):
        """Test bulk shortlisting candidates."""
        response = client.post(
            "/api/employers/interviews/bulk-action",
            headers=auth_headers,
            json={
                "interview_ids": [completed_interview.id],
                "action": "shortlist"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["processed"] == 1
        assert data["failed"] == 0

    def test_bulk_reject_success(
        self, client, auth_headers, completed_interview, mock_storage_service
    ):
        """Test bulk rejecting candidates."""
        response = client.post(
            "/api/employers/interviews/bulk-action",
            headers=auth_headers,
            json={
                "interview_ids": [completed_interview.id],
                "action": "reject"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["processed"] == 1

    def test_bulk_action_mixed_results(
        self, client, auth_headers, completed_interview, mock_storage_service
    ):
        """Test bulk action with some invalid IDs."""
        response = client.post(
            "/api/employers/interviews/bulk-action",
            headers=auth_headers,
            json={
                "interview_ids": [completed_interview.id, "invalid_id_1", "invalid_id_2"],
                "action": "shortlist"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["processed"] == 1
        assert data["failed"] == 2
        assert len(data["errors"]) == 2

    def test_bulk_action_empty_list(self, client, auth_headers):
        """Test bulk action with empty interview list."""
        response = client.post(
            "/api/employers/interviews/bulk-action",
            headers=auth_headers,
            json={
                "interview_ids": [],
                "action": "shortlist"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["processed"] == 0
        assert data["success"] is True

    def test_bulk_action_unauthorized(self, client, completed_interview):
        """Test bulk action without authentication."""
        response = client.post(
            "/api/employers/interviews/bulk-action",
            json={
                "interview_ids": [completed_interview.id],
                "action": "shortlist"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bulk_action_no_jobs(self, client, db_session):
        """Test bulk action when employer has no jobs."""
        from app.models import Employer
        from app.utils.auth import create_access_token, get_password_hash
        import uuid

        # Create employer with no jobs
        employer = Employer(
            id=f"e{uuid.uuid4().hex[:24]}",
            company_name="No Jobs Corp",
            email="nojobs@test.com",
            password=get_password_hash("password123"),
            is_verified=True,
        )
        db_session.add(employer)
        db_session.commit()

        token = create_access_token({"sub": employer.id, "type": "employer"})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/employers/interviews/bulk-action",
            headers=headers,
            json={
                "interview_ids": ["some_id"],
                "action": "shortlist"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCSVExport:
    """Tests for CSV export functionality."""

    def test_export_csv_success(
        self, client, auth_headers, completed_interview, mock_storage_service
    ):
        """Test successful CSV export."""
        response = client.get(
            "/api/employers/interviews/export",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")

        # Check CSV content
        csv_content = response.content.decode("utf-8")
        assert "Candidate Name" in csv_content
        assert "Email" in csv_content
        assert "Score" in csv_content

    def test_export_csv_with_job_filter(
        self, client, auth_headers, completed_interview, test_job, mock_storage_service
    ):
        """Test CSV export filtered by job."""
        response = client.get(
            f"/api/employers/interviews/export?job_id={test_job.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

    def test_export_csv_empty(self, client, auth_headers, test_employer):
        """Test CSV export with no interviews."""
        # Employer has a job but no interviews
        response = client.get(
            "/api/employers/interviews/export",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        # Should still have headers
        csv_content = response.content.decode("utf-8")
        assert "Candidate Name" in csv_content

    def test_export_csv_unauthorized(self, client):
        """Test CSV export without authentication."""
        response = client.get("/api/employers/interviews/export")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_csv_no_jobs(self, client, db_session):
        """Test CSV export when employer has no jobs."""
        from app.models import Employer
        from app.utils.auth import create_access_token, get_password_hash
        import uuid

        employer = Employer(
            id=f"e{uuid.uuid4().hex[:24]}",
            company_name="No Jobs Corp",
            email="nojobs_export@test.com",
            password=get_password_hash("password123"),
            is_verified=True,
        )
        db_session.add(employer)
        db_session.commit()

        token = create_access_token({"sub": employer.id, "type": "employer"})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/employers/interviews/export",
            headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
