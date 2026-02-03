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
            "password": "securepassword123",
            "university": "UC Berkeley",
            "major": "Computer Science",
            "graduation_year": 2026,
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "candidate" in data
        assert "token" in data
        assert data["candidate"]["name"] == "John Doe"
        assert data["candidate"]["email"] == "john.doe@test.com"

    def test_register_candidate_minimal(self, client):
        """Test candidate registration with minimal data."""
        response = client.post("/api/candidates/", json={
            "name": "Jane Doe",
            "email": "jane.doe@test.com",
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "candidate" in data
        assert "token" in data

    def test_register_candidate_duplicate_email(self, client, test_candidate):
        """Test registration with existing email fails."""
        response = client.post("/api/candidates/", json={
            "name": "Another Person",
            "email": test_candidate.email,
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_candidate_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post("/api/candidates/", json={
            "name": "Test",
            "email": "invalid-email",
            "password": "securepassword123",
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_candidate_short_password(self, client):
        """Test registration with too short password fails."""
        response = client.post("/api/candidates/", json={
            "name": "Test User",
            "email": "short@test.com",
            "password": "123",
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetCandidate:
    """Tests for getting candidate profile."""

    def test_get_candidate_success(self, client, test_candidate, candidate_auth_headers):
        """Test getting candidate profile with auth."""
        response = client.get(
            "/api/candidates/me",
            headers=candidate_auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_candidate.id
        assert data["name"] == test_candidate.name
        assert data["email"] == test_candidate.email

    def test_get_candidate_not_found(self, client, candidate_auth_headers):
        """Test getting profile without auth returns error."""
        response = client.get("/api/candidates/me")

        # Should return 403 (no auth) rather than 404
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestUpdateCandidate:
    """Tests for updating candidate profile."""

    def test_update_candidate_success(self, client, test_candidate, candidate_auth_headers):
        """Test updating candidate profile."""
        response = client.patch(
            "/api/candidates/me",
            headers=candidate_auth_headers,
            json={
                "university": "Stanford University",
                "major": "Computer Science",
                "graduation_year": 2025,
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["university"] == "Stanford University"
        assert data["major"] == "Computer Science"
        assert data["graduation_year"] == 2025

    def test_update_candidate_unauthorized(self, client):
        """Test updating without auth fails."""
        response = client.patch("/api/candidates/me", json={
            "university": "Test",
        })

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
