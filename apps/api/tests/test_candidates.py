"""
Tests for candidate API endpoints.
"""
import pytest
from fastapi import status


class TestCandidateRegistration:
    """Tests for candidate registration."""

    def test_register_candidate_success(self, client):
        """Test successful candidate registration."""
        response = client.post("/api/candidates/", json={
            "name": "John Doe",
            "email": "john.doe@test.com",
            "phone": "13800138000",
            "target_roles": ["Software Engineer", "Backend Developer"],
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@test.com"
        assert "id" in data

    def test_register_candidate_minimal(self, client):
        """Test candidate registration with minimal data."""
        response = client.post("/api/candidates/", json={
            "name": "Jane Doe",
            "email": "jane.doe@test.com",
            "phone": "13900139000",
            "target_roles": [],
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_register_candidate_duplicate_email(self, client, test_candidate):
        """Test registration with existing email fails."""
        response = client.post("/api/candidates/", json={
            "name": "Another Person",
            "email": test_candidate.email,
            "phone": "13700137000",
            "target_roles": [],
        })

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_candidate_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post("/api/candidates/", json={
            "name": "Test",
            "email": "invalid-email",
            "phone": "13800138000",
            "target_roles": [],
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_candidate_international_phone(self, client):
        """Test registration with international phone number."""
        response = client.post("/api/candidates/", json={
            "name": "International User",
            "email": "intl@test.com",
            "phone": "+14155551234",
            "target_roles": ["Software Engineer"],
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["phone"] == "+14155551234"

    def test_register_candidate_short_phone(self, client):
        """Test registration with too short phone number fails."""
        response = client.post("/api/candidates/", json={
            "name": "Test User",
            "email": "short@test.com",
            "phone": "12345",
            "target_roles": [],
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_candidate_with_university(self, client):
        """Test registration with university info."""
        response = client.post("/api/candidates/", json={
            "name": "John Smith",
            "email": "john.smith@berkeley.edu",
            "password": "testpass123",
            "university": "UC Berkeley",
            "major": "Computer Science",
            "graduation_year": 2026,
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["candidate"]["name"] == "John Smith"


class TestGetCandidate:
    """Tests for getting candidate details."""

    def test_get_candidate_success(self, client, test_candidate):
        """Test getting candidate by ID."""
        response = client.get(f"/api/candidates/{test_candidate.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_candidate.id
        assert data["name"] == test_candidate.name

    def test_get_candidate_not_found(self, client):
        """Test getting nonexistent candidate."""
        response = client.get("/api/candidates/nonexistent_id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
