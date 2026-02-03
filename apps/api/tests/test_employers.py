"""
Tests for employer API endpoints.
"""
import os
import pytest
from fastapi import status

# Check if we're using SQLite (default in tests)
USING_SQLITE = os.environ.get("TEST_DATABASE_URL", "sqlite://").startswith("sqlite")

# Skip marker for tests requiring array support
requires_array = pytest.mark.skipif(
    USING_SQLITE,
    reason="SQLite does not support ARRAY type"
)


class TestEmployerRegistration:
    """Tests for employer registration endpoint."""

    def test_register_employer_success(self, client):
        """Test successful employer registration."""
        response = client.post("/api/employers/register", json={
            "company_name": "New Tech Corp",
            "email": "new@techcorp.com",
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "employer" in data
        assert "token" in data
        assert data["employer"]["company_name"] == "New Tech Corp"
        assert data["employer"]["email"] == "new@techcorp.com"
        assert data["employer"]["is_verified"] is False
        assert "password" not in data["employer"]

    def test_register_employer_duplicate_email(self, client, test_employer):
        """Test registration with existing email fails."""
        response = client.post("/api/employers/register", json={
            "company_name": "Another Company",
            "email": test_employer.email,
            "password": "password123",
        })

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already" in response.json()["detail"].lower() or "exist" in response.json()["detail"].lower()

    def test_register_employer_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post("/api/employers/register", json={
            "company_name": "Test Corp",
            "email": "invalid-email",
            "password": "password123",
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestEmployerLogin:
    """Tests for employer login endpoint."""

    def test_login_success(self, client, test_employer):
        """Test successful login."""
        response = client.post("/api/employers/login", json={
            "email": test_employer.email,
            "password": "testpassword123",
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "employer" in data
        assert "token" in data
        assert data["employer"]["email"] == test_employer.email

    def test_login_wrong_password(self, client, test_employer):
        """Test login with wrong password."""
        response = client.post("/api/employers/login", json={
            "email": test_employer.email,
            "password": "wrongpassword",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower() or "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_email(self, client):
        """Test login with nonexistent email."""
        response = client.post("/api/employers/login", json={
            "email": "nonexistent@test.com",
            "password": "password123",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEmployerProfile:
    """Tests for employer profile endpoint."""

    def test_get_profile_authenticated(self, client, auth_headers, test_employer):
        """Test getting profile with valid token."""
        response = client.get("/api/employers/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_employer.id
        assert data["company_name"] == test_employer.company_name

    def test_get_profile_no_token(self, client):
        """Test getting profile without token."""
        response = client.get("/api/employers/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_invalid_token(self, client):
        """Test getting profile with invalid token."""
        response = client.get("/api/employers/me", headers={
            "Authorization": "Bearer invalid_token"
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDashboard:
    """Tests for employer dashboard endpoint."""

    def test_dashboard_no_data(self, client, auth_headers, test_employer):
        """Test dashboard with no interview data."""
        response = client.get("/api/employers/dashboard", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_interviews"] == 0
        assert data["pending_review"] == 0
        assert data["shortlisted"] == 0
        assert data["rejected"] == 0
        assert data["average_score"] is None

    def test_dashboard_with_interviews(self, client, auth_headers, completed_interview):
        """Test dashboard with interview data."""
        response = client.get("/api/employers/dashboard", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_interviews"] >= 1


class TestJobManagement:
    """Tests for job management endpoints."""

    @requires_array
    def test_create_job_success(self, client, auth_headers):
        """Test successful job creation with requirements array (PostgreSQL only)."""
        response = client.post("/api/employers/jobs", headers=auth_headers, json={
            "title": "Frontend Developer",
            "description": "Build amazing UIs",
            "requirements": ["React", "TypeScript"],
            "location": "Beijing",
            "salary_min": 20000,
            "salary_max": 35000,
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Frontend Developer"
        assert data["is_active"] is True
        assert "id" in data

    @requires_array
    def test_create_job_minimal(self, client, auth_headers):
        """Test job creation with minimal data (PostgreSQL only)."""
        response = client.post("/api/employers/jobs", headers=auth_headers, json={
            "title": "Backend Developer",
            "description": "Build APIs",
            "requirements": ["Python"],
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_list_jobs(self, client, auth_headers, test_job):
        """Test listing jobs."""
        response = client.get("/api/employers/jobs", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "jobs" in data
        assert data["total"] >= 1
        assert any(j["id"] == test_job.id for j in data["jobs"])

    def test_list_jobs_filter_active(self, client, auth_headers, test_job):
        """Test listing only active jobs."""
        response = client.get("/api/employers/jobs?is_active=true", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(j["is_active"] for j in data["jobs"])

    def test_get_job(self, client, auth_headers, test_job):
        """Test getting a specific job."""
        response = client.get(f"/api/employers/jobs/{test_job.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_job.id
        assert data["title"] == test_job.title

    def test_get_job_not_found(self, client, auth_headers):
        """Test getting a nonexistent job."""
        response = client.get("/api/employers/jobs/nonexistent_id", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_job(self, client, auth_headers, test_job):
        """Test updating a job."""
        response = client.put(f"/api/employers/jobs/{test_job.id}", headers=auth_headers, json={
            "title": "Senior Software Engineer",
            "salary_max": 40000,
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Senior Software Engineer"
        assert data["salary_max"] == 40000

    def test_delete_job(self, client, auth_headers, test_job):
        """Test deleting a job."""
        response = client.delete(f"/api/employers/jobs/{test_job.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/api/employers/jobs/{test_job.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInterviewManagement:
    """Tests for interview management endpoints."""

    def test_list_interviews(self, client, auth_headers, completed_interview):
        """Test listing interviews."""
        response = client.get("/api/employers/interviews", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "interviews" in data
        assert data["total"] >= 1

    def test_list_interviews_with_filters(self, client, auth_headers, completed_interview, test_job):
        """Test listing interviews with filters."""
        response = client.get(
            f"/api/employers/interviews?job_id={test_job.id}&status_filter=COMPLETED",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(i["status"] == "COMPLETED" for i in data["interviews"])

    def test_list_interviews_pagination(self, client, auth_headers, completed_interview):
        """Test interview listing pagination."""
        response = client.get(
            "/api/employers/interviews?skip=0&limit=5",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["interviews"]) <= 5

    def test_get_interview_detail(self, client, auth_headers, completed_interview, mock_storage_service):
        """Test getting interview detail."""
        response = client.get(
            f"/api/employers/interviews/{completed_interview.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == completed_interview.id
        assert data["status"] == "COMPLETED"
        assert len(data["responses"]) > 0

    def test_get_interview_not_found(self, client, auth_headers):
        """Test getting nonexistent interview."""
        response = client.get(
            "/api/employers/interviews/nonexistent_id",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_interview_status_shortlist(self, client, auth_headers, completed_interview, mock_storage_service):
        """Test shortlisting a candidate."""
        response = client.patch(
            f"/api/employers/interviews/{completed_interview.id}",
            headers=auth_headers,
            json={"status": "SHORTLISTED"}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_update_interview_status_reject(self, client, auth_headers, completed_interview, mock_storage_service):
        """Test rejecting a candidate."""
        response = client.patch(
            f"/api/employers/interviews/{completed_interview.id}",
            headers=auth_headers,
            json={"status": "REJECTED"}
        )

        assert response.status_code == status.HTTP_200_OK
