"""
Pytest configuration and fixtures for Pathway API tests.

Test Environment Setup:
- By default, uses SQLite in-memory for fast, isolated unit tests
- Set TEST_DATABASE_URL=postgresql://... for integration tests
- Load test environment from .env.test if it exists
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from unittest.mock import MagicMock, patch
import uuid
import json


# Load test environment variables from .env.test
env_test_path = Path(__file__).parent.parent / ".env.test"
if env_test_path.exists():
    load_dotenv(env_test_path, override=True)

# Set environment to test mode
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DISABLE_RATE_LIMITING", "true")


# Register custom visit methods for PostgreSQL types in SQLite DDL
def visit_ARRAY(self, type_, **kw):
    """Convert PostgreSQL ARRAY to SQLite TEXT."""
    return "TEXT"

def visit_JSONB(self, type_, **kw):
    """Convert PostgreSQL JSONB to SQLite TEXT."""
    return "TEXT"

SQLiteTypeCompiler.visit_ARRAY = visit_ARRAY
SQLiteTypeCompiler.visit_JSONB = visit_JSONB


from app.main import app
from app.database import Base, get_db
from app.models import (
    Candidate,
    CandidateVerticalProfile,
    Employer,
    Job,
    InterviewSession,
    InterviewResponse,
    InterviewQuestion,
    InviteToken,
    InterviewStatus,
    FollowupQueue,
    FollowupQueueStatus,
    Match,
    MatchStatus,
    Message,
    MessageType,
)
from app.utils.auth import create_access_token, get_password_hash


# Use TEST_DATABASE_URL if available, fallback to SQLite for basic tests
import os

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")

if TEST_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def generate_test_id(prefix: str = "t") -> str:
    """Generate a unique test ID."""
    return f"{prefix}{uuid.uuid4().hex[:24]}"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_storage_service():
    """Mock the storage service for tests."""
    from unittest.mock import AsyncMock

    # Need to patch in all locations where storage_service is imported
    mock = MagicMock()
    # Use AsyncMock for async methods
    mock.upload_video_bytes = AsyncMock(return_value="videos/test-session/q0/video.webm")
    mock.download_video = AsyncMock(return_value=b"fake video bytes")
    mock.get_signed_url.return_value = "https://example.com/signed-url"
    mock.get_upload_url.return_value = ("https://upload.example.com", "videos/test/upload.webm")

    with patch("app.services.storage.storage_service", mock), \
         patch("app.routers.interviews.storage_service", mock):
        yield mock


@pytest.fixture
def mock_background_tasks():
    """Mock background tasks to prevent actual processing."""
    with patch("app.routers.interviews.process_interview_response") as mock_process, \
         patch("app.routers.interviews.generate_interview_summary") as mock_summary, \
         patch("app.routers.interviews.send_completion_emails") as mock_email, \
         patch("app.routers.interviews.process_match_after_interview") as mock_match:
        yield {
            "process": mock_process,
            "summary": mock_summary,
            "email": mock_email,
            "match": mock_match,
        }


# ==================== Test Data Fixtures ====================

@pytest.fixture
def test_employer(db_session):
    """Create a test employer."""
    employer = Employer(
        id=generate_test_id("e"),
        company_name="Test Company",
        email="employer@test.com",
        password=get_password_hash("testpassword123"),
        is_verified=True,
    )
    db_session.add(employer)
    db_session.commit()
    db_session.refresh(employer)
    return employer


@pytest.fixture
def employer_token(test_employer):
    """Generate JWT token for the test employer."""
    return create_access_token({"sub": test_employer.id, "type": "employer"})


@pytest.fixture
def auth_headers(employer_token):
    """Return authorization headers with the employer token."""
    return {"Authorization": f"Bearer {employer_token}"}


@pytest.fixture
def test_job(db_session, test_employer):
    """Create a test job."""
    job = Job(
        id=generate_test_id("j"),
        title="Software Engineer",
        description="Test job description",
        requirements=None,  # None for SQLite compatibility
        location="Shanghai",
        salary_min=15000,
        salary_max=25000,
        is_active=True,
        employer_id=test_employer.id,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def test_candidate(db_session):
    """Create a test candidate."""
    candidate = Candidate(
        id=generate_test_id("c"),
        name="Test Candidate",
        email="candidate@test.com",
        phone="13800138000",
        target_roles=None,  # None for SQLite compatibility
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


@pytest.fixture
def test_questions(db_session):
    """Create default test questions."""
    questions = []
    for i, q_data in enumerate([
        {"text": "Tell me about yourself", "category": "introduction"},
        {"text": "Why are you interested in this role?", "category": "motivation"},
        {"text": "Describe a challenge you've faced", "category": "behavioral"},
    ]):
        question = InterviewQuestion(
            id=generate_test_id("q"),
            text=q_data["text"],
            category=q_data["category"],
            order=i,
            is_default=True,
            job_id=None,
        )
        db_session.add(question)
        questions.append(question)
    db_session.commit()
    return questions


@pytest.fixture
def test_interview(db_session, test_candidate, test_job):
    """Create a test interview session."""
    session = InterviewSession(
        id=generate_test_id("i"),
        status=InterviewStatus.IN_PROGRESS,
        candidate_id=test_candidate.id,
        job_id=test_job.id,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def completed_interview(db_session, test_candidate, test_job, test_questions):
    """Create a completed interview with responses."""
    session = InterviewSession(
        id=generate_test_id("i"),
        status=InterviewStatus.COMPLETED,
        total_score=75.5,
        ai_summary='{"summary": "Good candidate", "recommendation": "Proceed", "overall_strengths": ["Communication"], "overall_improvements": ["Technical depth"]}',
        candidate_id=test_candidate.id,
        job_id=test_job.id,
    )
    db_session.add(session)
    db_session.flush()

    for i, q in enumerate(test_questions):
        # Use ScoreDetails-compatible schema format
        score_details = {
            "communication": 7.5,
            "problem_solving": 7.0,
            "domain_knowledge": 7.0,
            "motivation": 8.0,
            "culture_fit": 7.0,
            "overall": 7.3,
            "analysis": "Good answer with clear communication",
            "strengths": ["Clear articulation", "Good examples"],
            "concerns": ["Could provide more technical depth"],
            "highlight_quotes": ["I learned that..."]
        }
        response = InterviewResponse(
            id=generate_test_id("r"),
            question_index=i,
            question_text=q.text,
            video_url=f"videos/{session.id}/q{i}/video.webm",
            transcription=f"This is a test response for question {i}",
            ai_score=70 + (i * 5),
            ai_analysis=json.dumps(score_details),
            duration_seconds=60 + (i * 10),
            session_id=session.id,
        )
        db_session.add(response)

    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def test_invite(db_session, test_job):
    """Create a test invite token."""
    invite = InviteToken(
        id=generate_test_id("inv"),
        token="test_invite_token_12345",
        job_id=test_job.id,
        max_uses=10,
        used_count=0,
        is_active=True,
    )
    db_session.add(invite)
    db_session.commit()
    db_session.refresh(invite)
    return invite


@pytest.fixture
def practice_interview(db_session, test_candidate, test_job):
    """Create a test practice interview session."""
    session = InterviewSession(
        id=generate_test_id("i"),
        status=InterviewStatus.IN_PROGRESS,
        is_practice=True,
        candidate_id=test_candidate.id,
        job_id=test_job.id,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def test_match(db_session, test_candidate, test_job):
    """Create a test match record."""
    match = Match(
        id=generate_test_id("m"),
        candidate_id=test_candidate.id,
        job_id=test_job.id,
        score=75.0,
        status=MatchStatus.PENDING,
        overall_match_score=0.75,
        interview_score=75.0,
        skills_match_score=0.80,
        experience_match_score=0.70,
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


@pytest.fixture
def mock_cache_service():
    """Mock the cache service for tests."""
    with patch("app.services.cache.cache_service") as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        mock.is_available = True
        mock.get_dashboard_stats.return_value = None
        mock.get_questions.return_value = None
        mock.get_top_candidates.return_value = None
        mock.get_interview_session.return_value = None
        yield mock


# ==================== AI Scoring Fixtures ====================

@pytest.fixture
def mock_scoring_service():
    """Mock the scoring service for tests."""
    from app.services.scoring import ScoreResult

    mock_result = ScoreResult(
        communication=7.5,
        problem_solving=8.0,
        domain_knowledge=7.0,
        motivation=8.5,
        culture_fit=7.5,
        overall=7.7,
        analysis="Good response with clear communication.",
        strengths=["Clear articulation", "Good examples"],
        concerns=["Could provide more technical depth"],
        highlight_quotes=["I learned that..."],
        raw_response=None,
        algorithm_version="2.0.1",
        vertical="software_engineering",
    )

    with patch("app.services.scoring.scoring_service") as mock:
        mock.analyze_response.return_value = mock_result
        mock.generate_summary.return_value = MagicMock(
            total_score=7.5,
            summary="Strong candidate overall.",
            overall_strengths=["Communication", "Problem solving"],
            overall_concerns=["Technical depth"],
            recommendation="advance",
        )
        mock.get_immediate_feedback.return_value = {
            "score_result": mock_result,
            "tips": ["Be more specific", "Use STAR method"],
            "sample_answer": "A good answer would include...",
        }
        mock.analyze_and_generate_followups.return_value = (
            mock_result,
            ["Can you elaborate on that?", "What challenges did you face?"]
        )
        mock.score_profile.return_value = {
            "profile_score": 7.0,
            "breakdown": {
                "technical_skills": 7.5,
                "experience_quality": 6.5,
                "education": 8.0,
                "github_activity": 6.0,
            },
            "strengths": ["Strong academic background"],
            "gaps": ["Limited work experience"],
            "summary": "Promising candidate with good fundamentals.",
            "completeness": 75,
            "algorithm_version": "2.0.1",
        }
        yield mock


@pytest.fixture
def mock_llm_response():
    """Mock LLM API response for AI tests."""
    def create_mock_response(scores=None, analysis="Test analysis"):
        if scores is None:
            scores = {
                "communication": 75,
                "problem_solving": 80,
                "domain_knowledge": 70,
                "motivation": 85,
                "culture_fit": 75,
            }
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "scores": scores,
                        "overall_score": 77,
                        "analysis": analysis,
                        "strengths": ["strength1", "strength2"],
                        "concerns": ["concern1"],
                        "highlight_quotes": ["quote1"],
                    })
                }
            }]
        }
    return create_mock_response


# ==================== GitHub Integration Fixtures ====================

@pytest.fixture
def mock_github_service():
    """Mock the GitHub service for tests."""
    with patch("app.services.github.GitHubService") as MockClass:
        mock_instance = MagicMock()

        # Mock user data
        mock_instance.get_user.return_value = {
            "login": "testuser",
            "name": "Test User",
            "email": "test@github.com",
            "avatar_url": "https://github.com/images/avatar.png",
            "bio": "Software developer",
            "public_repos": 15,
            "followers": 50,
            "following": 25,
        }

        # Mock repos data
        mock_instance.get_repos.return_value = [
            {
                "name": "awesome-project",
                "description": "A test project",
                "language": "Python",
                "stargazers_count": 10,
                "forks_count": 2,
                "html_url": "https://github.com/testuser/awesome-project",
            },
            {
                "name": "web-app",
                "description": "A web application",
                "language": "TypeScript",
                "stargazers_count": 5,
                "forks_count": 1,
                "html_url": "https://github.com/testuser/web-app",
            },
        ]

        # Mock languages data
        mock_instance.get_languages.return_value = {
            "Python": 50000,
            "TypeScript": 30000,
            "JavaScript": 20000,
        }

        # Mock contribution count
        mock_instance.get_contribution_count.return_value = 150

        # Mock exchange code for token
        mock_instance.exchange_code_for_token.return_value = "github_access_token_123"

        MockClass.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def test_candidate_with_github(db_session):
    """Create a test candidate with GitHub data."""
    from datetime import datetime

    candidate = Candidate(
        id=generate_test_id("c"),
        name="GitHub Test Candidate",
        email="github_candidate@test.com",
        phone="13800138001",
        github_username="testuser",
        github_data={
            "repos": [
                {"name": "project1", "language": "Python", "stars": 10},
                {"name": "project2", "language": "TypeScript", "stars": 5},
            ],
            "languages": {"Python": 60, "TypeScript": 30, "JavaScript": 10},
            "totalContributions": 150,
        },
        github_connected_at=datetime(2024, 1, 15, 12, 0, 0),
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate


# ==================== Authentication Fixtures ====================

@pytest.fixture
def candidate_token(test_candidate):
    """Generate JWT token for the test candidate."""
    return create_access_token({"sub": test_candidate.id, "type": "candidate"})


@pytest.fixture
def candidate_auth_headers(candidate_token):
    """Return authorization headers with the candidate token."""
    return {"Authorization": f"Bearer {candidate_token}"}


@pytest.fixture
def expired_token():
    """Generate an expired JWT token for testing."""
    from datetime import datetime, timedelta
    import jwt
    from app.config import settings

    payload = {
        "sub": "test-user-id",
        "type": "candidate",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture
def invalid_token():
    """Return an invalid JWT token for testing."""
    return "invalid.jwt.token.that.should.fail"


@pytest.fixture
def mock_email_service():
    """Mock the email service for tests."""
    with patch("app.services.email.email_service") as mock:
        mock.send_verification_email.return_value = True
        mock.send_interview_invitation.return_value = True
        mock.send_interview_results.return_value = True
        mock.send_match_notification.return_value = True
        yield mock


# ==================== Rate Limiting Fixtures ====================

@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Disable rate limiting for all tests."""
    # Disable rate limiting by setting the limiter's enabled flag
    from app.utils.rate_limit import limiter

    # Store original state and disable
    original_enabled = limiter.enabled
    limiter.enabled = False

    yield

    # Restore original state
    limiter.enabled = original_enabled
