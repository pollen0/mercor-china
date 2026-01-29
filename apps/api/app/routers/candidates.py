from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import uuid

from ..database import get_db
from ..models.candidate import Candidate
from ..schemas.candidate import CandidateCreate, CandidateResponse, CandidateList

router = APIRouter()


def generate_cuid() -> str:
    return f"c{uuid.uuid4().hex[:24]}"


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    candidate = Candidate(
        id=generate_cuid(),
        name=candidate_data.name,
        email=candidate_data.email,
        phone=candidate_data.phone,
        target_roles=candidate_data.target_roles,
    )

    try:
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    return candidate


@router.get("/", response_model=CandidateList)
async def list_candidates(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Candidate.name.ilike(search_filter)) |
            (Candidate.email.ilike(search_filter))
        )

    total = query.count()
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()

    return CandidateList(candidates=candidates, total=total)


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人不存在"
        )

    return candidate
