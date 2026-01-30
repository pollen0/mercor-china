from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from ..database import get_db
from ..models import InterviewQuestion, Job, CodingChallenge
from ..schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionList,
    DEFAULT_QUESTIONS,
)
from ..schemas.coding_challenge import (
    CodingChallengeResponse,
    DEFAULT_CODING_CHALLENGES,
)
from ..services.cache import cache_service

router = APIRouter()


def generate_cuid() -> str:
    return f"q{uuid.uuid4().hex[:24]}"


@router.get("/", response_model=QuestionList)
async def list_questions(
    job_id: Optional[str] = None,
    include_defaults: bool = True,
    db: Session = Depends(get_db)
):
    """
    List interview questions.
    - If job_id is provided, returns questions for that job
    - If include_defaults is True, also includes default questions
    """
    # Try cache first
    cache_key = f"questions:list:{job_id or 'defaults'}:{include_defaults}"
    cached = cache_service.get(cache_key)
    if cached:
        return QuestionList(questions=cached["questions"], total=cached["total"])

    query = db.query(InterviewQuestion)

    if job_id:
        if include_defaults:
            query = query.filter(
                (InterviewQuestion.job_id == job_id) |
                (InterviewQuestion.is_default == True)
            )
        else:
            query = query.filter(InterviewQuestion.job_id == job_id)
    else:
        query = query.filter(InterviewQuestion.is_default == True)

    questions = query.order_by(InterviewQuestion.order).all()

    # Cache the result
    questions_data = [
        {
            "id": q.id,
            "text": q.text,
            "text_zh": q.text_zh,
            "category": q.category,
            "order": q.order,
            "is_default": q.is_default,
            "job_id": q.job_id,
        }
        for q in questions
    ]
    cache_service.set(cache_key, {"questions": questions_data, "total": len(questions)}, ttl=cache_service.TTL_LONG)

    return QuestionList(questions=questions, total=len(questions))


@router.get("/defaults", response_model=QuestionList)
async def get_default_questions(db: Session = Depends(get_db)):
    """Get all default interview questions."""
    # Try cache first
    cached = cache_service.get_questions()
    if cached:
        return QuestionList(questions=cached, total=len(cached))

    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.is_default == True
    ).order_by(InterviewQuestion.order).all()

    # Cache the result
    questions_data = [
        {
            "id": q.id,
            "text": q.text,
            "text_zh": q.text_zh,
            "category": q.category,
            "order": q.order,
            "is_default": q.is_default,
            "job_id": q.job_id,
        }
        for q in questions
    ]
    cache_service.set_questions(questions_data)

    return QuestionList(questions=questions, total=len(questions))


@router.get("/job/{job_id}", response_model=QuestionList)
async def get_job_questions(job_id: str, db: Session = Depends(get_db)):
    """Get questions for a specific job, including defaults."""
    # Try cache first
    cached = cache_service.get_questions(job_id)
    if cached:
        return QuestionList(questions=cached, total=len(cached))

    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    # Get job-specific questions
    job_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.job_id == job_id
    ).order_by(InterviewQuestion.order).all()

    # If no custom questions, return defaults
    if not job_questions:
        default_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.is_default == True
        ).order_by(InterviewQuestion.order).all()

        # Cache defaults
        questions_data = [
            {
                "id": q.id,
                "text": q.text,
                "text_zh": q.text_zh,
                "category": q.category,
                "order": q.order,
                "is_default": q.is_default,
                "job_id": q.job_id,
            }
            for q in default_questions
        ]
        cache_service.set_questions(questions_data, job_id)
        return QuestionList(questions=default_questions, total=len(default_questions))

    # Cache job questions
    questions_data = [
        {
            "id": q.id,
            "text": q.text,
            "text_zh": q.text_zh,
            "category": q.category,
            "order": q.order,
            "is_default": q.is_default,
            "job_id": q.job_id,
        }
        for q in job_questions
    ]
    cache_service.set_questions(questions_data, job_id)

    return QuestionList(questions=job_questions, total=len(job_questions))


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db)
):
    """Create a custom interview question for a job."""
    # Verify job exists if job_id provided
    if question_data.job_id:
        job = db.query(Job).filter(Job.id == question_data.job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="职位不存在"
            )

    question = InterviewQuestion(
        id=generate_cuid(),
        text=question_data.text,
        text_zh=question_data.text_zh,
        category=question_data.category,
        order=question_data.order,
        is_default=False,
        job_id=question_data.job_id,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    # Invalidate cache for this job's questions
    if question_data.job_id:
        cache_service.invalidate_questions(question_data.job_id)

    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db)
):
    """Update an interview question."""
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问题不存在"
        )

    if question.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法修改默认问题"
        )

    job_id = question.job_id  # Store before potential update

    update_data = question_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)

    # Invalidate cache for this job's questions
    if job_id:
        cache_service.invalidate_questions(job_id)
    # Also invalidate new job_id if changed
    if question.job_id and question.job_id != job_id:
        cache_service.invalidate_questions(question.job_id)

    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: str, db: Session = Depends(get_db)):
    """Delete an interview question."""
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问题不存在"
        )

    if question.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法删除默认问题"
        )

    job_id = question.job_id  # Store before delete

    db.delete(question)
    db.commit()

    # Invalidate cache for this job's questions
    if job_id:
        cache_service.invalidate_questions(job_id)


@router.post("/seed-defaults", response_model=QuestionList)
async def seed_default_questions(db: Session = Depends(get_db)):
    """
    Seed the default interview questions.
    Only creates them if they don't already exist.
    """
    existing = db.query(InterviewQuestion).filter(
        InterviewQuestion.is_default == True
    ).count()

    if existing > 0:
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.is_default == True
        ).order_by(InterviewQuestion.order).all()
        return QuestionList(questions=questions, total=len(questions))

    created_questions = []
    for q_data in DEFAULT_QUESTIONS:
        question = InterviewQuestion(
            id=generate_cuid(),
            text=q_data["text"],
            text_zh=q_data["text_zh"],
            category=q_data["category"],
            order=q_data["order"],
            is_default=True,
            job_id=None,
        )
        db.add(question)
        created_questions.append(question)

    db.commit()

    for q in created_questions:
        db.refresh(q)

    # Invalidate all questions cache since defaults were just created
    cache_service.invalidate_questions()

    return QuestionList(questions=created_questions, total=len(created_questions))


# ==================== CODING CHALLENGES ====================

def generate_challenge_cuid() -> str:
    return f"cc{uuid.uuid4().hex[:22]}"


@router.get("/coding-challenges", response_model=list[CodingChallengeResponse])
async def list_coding_challenges(db: Session = Depends(get_db)):
    """List all available coding challenges."""
    challenges = db.query(CodingChallenge).order_by(CodingChallenge.difficulty).all()
    return challenges


@router.get("/coding-challenges/{challenge_id}", response_model=CodingChallengeResponse)
async def get_coding_challenge(challenge_id: str, db: Session = Depends(get_db)):
    """Get a specific coding challenge by ID."""
    challenge = db.query(CodingChallenge).filter(
        CodingChallenge.id == challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="编程挑战不存在"
        )

    return challenge


@router.post("/seed-coding-challenges", response_model=list[CodingChallengeResponse])
async def seed_coding_challenges(db: Session = Depends(get_db)):
    """
    Seed default coding challenges.
    Only creates them if they don't already exist.
    """
    existing = db.query(CodingChallenge).count()

    if existing > 0:
        challenges = db.query(CodingChallenge).order_by(CodingChallenge.difficulty).all()
        return challenges

    created_challenges = []
    for c_data in DEFAULT_CODING_CHALLENGES:
        # Convert TestCase objects to dicts if needed
        test_cases = [
            tc.model_dump() if hasattr(tc, 'model_dump') else tc
            for tc in c_data["test_cases"]
        ]

        challenge = CodingChallenge(
            id=generate_challenge_cuid(),
            title=c_data["title"],
            title_zh=c_data.get("title_zh"),
            description=c_data["description"],
            description_zh=c_data.get("description_zh"),
            starter_code=c_data.get("starter_code"),
            test_cases=test_cases,
            time_limit_seconds=c_data.get("time_limit_seconds", 5),
            difficulty=c_data.get("difficulty", "easy"),
        )
        db.add(challenge)
        created_challenges.append(challenge)

    db.commit()

    for c in created_challenges:
        db.refresh(c)

    return created_challenges


@router.post("/create-coding-question", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_coding_question(
    job_id: str,
    challenge_id: str,
    order: int = 0,
    db: Session = Depends(get_db)
):
    """
    Create a coding question for a job, linked to a coding challenge.
    This allows adding coding challenges to an interview flow.
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    # Verify challenge exists
    challenge = db.query(CodingChallenge).filter(
        CodingChallenge.id == challenge_id
    ).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="编程挑战不存在"
        )

    question = InterviewQuestion(
        id=generate_cuid(),
        text=f"Coding Challenge: {challenge.title}",
        text_zh=f"编程题: {challenge.title_zh or challenge.title}",
        category="technical",
        order=order,
        is_default=False,
        job_id=job_id,
        question_type="coding",
        coding_challenge_id=challenge.id,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    # Invalidate cache for this job's questions
    cache_service.invalidate_questions(job_id)

    return question
