"""
Pytest configuration and fixtures for ZhiPin AI API tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch
import uuid

from app.main import app
from app.database import Base, get_db
from app.models import (
    Candidate,
    Employer,
    Job,
    InterviewSession,
    InterviewResponse,
    InterviewQuestion,
    InviteToken,
    InterviewStatus,
)
from app.utils.auth import create_access_token, get_password_hash


# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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
    with patch("app.services.storage.storage_service") as mock:
        mock.upload_video_bytes.return_value = "videos/test-session/q0/video.webm"
        mock.get_signed_url.return_value = "https://example.com/signed-url"
        mock.get_upload_url.return_value = ("https://upload.example.com", "videos/test/upload.webm")
        yield mock


@pytest.fixture
def mock_background_tasks():
    """Mock background tasks to prevent actual processing."""
    with patch("app.routers.interviews.process_interview_response") as mock_process, \
         patch("app.routers.interviews.generate_interview_summary") as mock_summary, \
         patch("app.routers.interviews.send_completion_emails") as mock_email:
        yield {
            "process": mock_process,
            "summary": mock_summary,
            "email": mock_email,
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
        requirements=["Python", "FastAPI", "PostgreSQL"],
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
        target_roles=["Software Engineer", "Backend Developer"],
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
        {"text": "Tell me about yourself", "text_zh": "请介绍一下你自己", "category": "introduction"},
        {"text": "Why this role?", "text_zh": "为什么对这个职位感兴趣?", "category": "motivation"},
        {"text": "Describe a challenge", "text_zh": "描述一个你遇到的挑战", "category": "behavioral"},
    ]):
        question = InterviewQuestion(
            id=generate_test_id("q"),
            text=q_data["text"],
            text_zh=q_data["text_zh"],
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
        response = InterviewResponse(
            id=generate_test_id("r"),
            question_index=i,
            question_text=q.text_zh or q.text,
            video_url=f"videos/{session.id}/q{i}/video.webm",
            transcription=f"This is a test response for question {i}",
            ai_score=70 + (i * 5),
            ai_analysis='{"scores": {"relevance": 8, "clarity": 7, "depth": 7, "communication": 8, "job_fit": 7}, "analysis": "Good answer", "strengths": ["Clear"], "improvements": ["More detail"]}',
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
