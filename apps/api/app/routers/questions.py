from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from ..database import get_db
from ..models import InterviewQuestion, Job
from ..schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionList,
    DEFAULT_QUESTIONS,
)

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
    return QuestionList(questions=questions, total=len(questions))


@router.get("/defaults", response_model=QuestionList)
async def get_default_questions(db: Session = Depends(get_db)):
    """Get all default interview questions."""
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.is_default == True
    ).order_by(InterviewQuestion.order).all()

    return QuestionList(questions=questions, total=len(questions))


@router.get("/job/{job_id}", response_model=QuestionList)
async def get_job_questions(job_id: str, db: Session = Depends(get_db)):
    """Get questions for a specific job, including defaults."""
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
        return QuestionList(questions=default_questions, total=len(default_questions))

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

    update_data = question_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)

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

    db.delete(question)
    db.commit()


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

    return QuestionList(questions=created_questions, total=len(created_questions))
