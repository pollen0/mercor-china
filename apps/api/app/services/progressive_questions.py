"""
Progressive Question Generation Service

Generates personalized interview questions using AI based on:
- Candidate's resume, GitHub, and transcript data
- Previous interview history and performance
- Avoiding redundant topics they've already been asked about
- Appropriate difficulty level based on past scores
"""

import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..config import settings
from ..models import (
    Candidate, CandidateVerticalProfile, InterviewSession,
    InterviewResponse, Vertical, RoleType
)
from ..models.employer import CandidateQuestionHistory

logger = logging.getLogger("pathway.progressive_questions")


# Topic categories to track (prevents asking about same themes)
QUESTION_TOPIC_CATEGORIES = [
    "background_intro",  # Tell me about yourself
    "project_technical",  # Technical project walkthrough
    "debugging_problem_solving",  # Bug fixing, debugging approach
    "teamwork_collaboration",  # Team projects, disagreements
    "learning_growth",  # Learning new things, growth mindset
    "technical_decisions",  # Trade-offs, architecture decisions
    "code_quality",  # Testing, code review, best practices
    "legacy_systems",  # Working with existing code
    "mentoring_leadership",  # Helping others, leading
    "system_design",  # Scalability, architecture
    "technical_debt",  # Balancing debt vs features
    "stakeholder_management",  # Working with non-technical people
    "failure_resilience",  # Handling failures, learning from mistakes
    "current_trends",  # Industry awareness, new technologies
    "ethics_responsibility",  # Ethical considerations
    "performance_optimization",  # Speed, efficiency
    "production_issues",  # Real-world deployment challenges
    "prioritization",  # Making decisions with constraints
]


def get_candidate_interview_history(
    db: Session,
    candidate_id: str,
    vertical: Optional[Vertical] = None
) -> Dict[str, Any]:
    """
    Get comprehensive interview history for a candidate.

    Returns:
        - Previous questions asked (by topic) with their texts and scores
        - Scores received
        - Number of interviews taken
        - Best/average performance
        - Areas of strength and weakness
        - Previous question details for knowledge evolution testing
    """
    # Get all completed interviews for this candidate
    query = db.query(InterviewSession).filter(
        InterviewSession.candidate_id == candidate_id,
        InterviewSession.status == "COMPLETED"
    )

    if vertical:
        query = query.filter(InterviewSession.vertical == vertical)

    sessions = query.order_by(InterviewSession.completed_at.desc()).all()

    if not sessions:
        return {
            "interview_count": 0,
            "topics_asked": [],
            "scores": [],
            "average_score": None,
            "best_score": None,
            "category_scores": {},
            "recommended_difficulty": 1,
            "focus_areas": [],
            "previous_questions": [],  # For knowledge evolution testing
        }

    # Collect all topics asked and performance by category
    topics_asked = set()
    scores = []
    category_scores: Dict[str, List[float]] = {}

    # Track previous questions with their performance for knowledge evolution testing
    previous_questions: List[Dict[str, Any]] = []

    for session in sessions:
        if session.total_score:
            scores.append(session.total_score)

        # Get question history for this session (what was asked and how they scored)
        question_history = db.query(CandidateQuestionHistory).filter(
            CandidateQuestionHistory.interview_session_id == session.id,
            CandidateQuestionHistory.candidate_id == candidate_id
        ).all()

        for qh in question_history:
            if qh.category:
                topics_asked.add(qh.category)

                # Track scores by category
                if qh.score:
                    if qh.category not in category_scores:
                        category_scores[qh.category] = []
                    category_scores[qh.category].append(qh.score)

            # Store question details for knowledge evolution testing
            # Include questions where candidate scored low - AI should probe these areas deeper
            previous_questions.append({
                "question_text": qh.question_text[:200] if qh.question_text else "",  # Truncate for prompt size
                "category": qh.category,
                "topic": qh.question_key,
                "score": qh.score,
                "asked_at": qh.asked_at.isoformat() if qh.asked_at else None,
                "difficulty_level": qh.difficulty_level,
            })

    # Calculate average scores per category
    avg_category_scores = {
        cat: sum(s) / len(s) for cat, s in category_scores.items() if s
    }

    # Determine weak areas (below 6.5) and strong areas (above 7.5)
    weak_areas = [cat for cat, score in avg_category_scores.items() if score < 6.5]
    strong_areas = [cat for cat, score in avg_category_scores.items() if score >= 7.5]

    # Determine recommended difficulty based on best score
    best_score = max(scores) if scores else None
    avg_score = sum(scores) / len(scores) if scores else None

    if best_score is None:
        recommended_difficulty = 1
    elif best_score >= 7.5:
        recommended_difficulty = 3  # Advanced
    elif best_score >= 5.5:
        recommended_difficulty = 2  # Intermediate
    else:
        recommended_difficulty = 1  # Stay foundational

    # Get low-scoring questions (< 6.5) for targeted improvement testing
    low_score_questions = [
        q for q in previous_questions
        if q.get("score") and q["score"] < 6.5
    ]

    return {
        "interview_count": len(sessions),
        "topics_asked": list(topics_asked),
        "scores": scores,
        "average_score": avg_score,
        "best_score": best_score,
        "category_scores": avg_category_scores,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
        "recommended_difficulty": recommended_difficulty,
        "focus_areas": weak_areas if weak_areas else [],
        "previous_questions": previous_questions[-10:],  # Last 10 questions for context
        "low_score_questions": low_score_questions[:5],  # Top 5 weak spots to probe
    }


def build_progressive_question_prompt(
    candidate_data: Dict[str, Any],
    interview_history: Dict[str, Any],
    vertical: str,
    role_type: Optional[str],
    num_questions: int = 5
) -> str:
    """
    Build a prompt for AI to generate progressive, non-redundant questions.

    Key capabilities:
    - Avoids asking questions on topics already covered
    - Increases difficulty based on past performance
    - Probes deeper into weak areas to test improvement
    - Uses candidate profile (resume, GitHub, transcript) for personalization
    """
    # Extract candidate profile data
    resume_summary = candidate_data.get("resume_summary", "No resume available")
    github_summary = candidate_data.get("github_summary", "No GitHub data")
    transcript_summary = candidate_data.get("transcript_summary", "No transcript data")

    # Interview history context
    interview_count = interview_history.get("interview_count", 0)
    topics_asked = interview_history.get("topics_asked", [])
    best_score = interview_history.get("best_score")
    avg_score = interview_history.get("average_score")
    weak_areas = interview_history.get("weak_areas", [])
    strong_areas = interview_history.get("strong_areas", [])
    recommended_difficulty = interview_history.get("recommended_difficulty", 1)
    previous_questions = interview_history.get("previous_questions", [])
    low_score_questions = interview_history.get("low_score_questions", [])

    difficulty_descriptions = {
        1: "foundational (basic behavioral and intro technical questions)",
        2: "intermediate (deeper technical scenarios, real-world challenges, trade-offs)",
        3: "advanced (system design, leadership, complex ambiguous problems, strategic thinking)"
    }

    prompt = f"""You are an expert interviewer for {vertical.replace('_', ' ')} roles{f', specifically {role_type.replace("_", " ")}' if role_type else ''}.

Generate {num_questions} interview questions for this candidate based on their profile and interview history.
Your goal is to assess whether they have GROWN and IMPROVED since their last interview.

## CANDIDATE PROFILE:

**Resume:**
{resume_summary}

**GitHub Activity:**
{github_summary}

**Academic Transcript:**
{transcript_summary}

## INTERVIEW HISTORY:

- This is interview #{interview_count + 1} for this candidate
- Previous best score: {f'{best_score:.1f}/10' if best_score else 'First interview'}
- Average score across interviews: {f'{avg_score:.1f}/10' if avg_score else 'N/A'}
- Recommended difficulty level: {difficulty_descriptions[recommended_difficulty]}
"""

    if topics_asked:
        prompt += f"""
- Topics ALREADY asked in previous interviews (DO NOT repeat these exact themes):
  {', '.join(topics_asked)}
"""

    if weak_areas:
        prompt += f"""
- WEAK AREAS needing improvement (probe these to test if they've improved):
  {', '.join(weak_areas)}
"""

    if strong_areas:
        prompt += f"""
- STRONG AREAS (push them to demonstrate even deeper expertise here):
  {', '.join(strong_areas)}
"""

    # Include previous questions and scores for knowledge evolution testing
    if low_score_questions:
        prompt += """
## PREVIOUS LOW-SCORING QUESTIONS (Test if they've improved in these areas):
"""
        for q in low_score_questions[:3]:  # Top 3 weak spots
            prompt += f"""
- Previous Q: "{q.get('question_text', 'N/A')[:150]}..."
  Score: {q.get('score', 'N/A')}/10 | Category: {q.get('category', 'N/A')}
  → Generate a FOLLOW-UP question that tests if they've deepened their understanding
"""

    if previous_questions and interview_count > 0:
        prompt += """
## RECENT QUESTIONS ASKED (For context - avoid repetition but build on these):
"""
        for q in previous_questions[:5]:  # Last 5 questions
            if q.get('question_text'):
                score_str = f"{q.get('score'):.1f}/10" if q.get('score') else "Not scored"
                prompt += f"""- "{q.get('question_text', '')[:100]}..." ({q.get('category', 'N/A')}, Score: {score_str})
"""

    prompt += f"""
## REQUIREMENTS:

1. **Personalization**: Questions should reference specific details from their resume, GitHub projects, or coursework
2. **No Redundancy**: DO NOT repeat topics already covered. Ask about NEW aspects or deeper layers.
3. **Progressive Difficulty**: Questions should be at {difficulty_descriptions[recommended_difficulty]} level
4. **Variety**: Cover different categories (technical, behavioral, problem-solving, motivation)
5. **Knowledge Evolution Testing**: If this is a repeat interview:
   - For WEAK areas: Ask questions that test if they've studied and improved
   - For STRONG areas: Push them to demonstrate mastery with harder scenarios
   - Reference their growth: "Last time we discussed X, now let's explore Y..."
6. **Growth Mindset**: Frame questions to reveal learning, adaptation, and improvement

## OUTPUT FORMAT:

Return a JSON array with exactly {num_questions} questions:
```json
[
  {{
    "text": "The full question text, personalized to the candidate",
    "category": "One of: background, technical, behavioral, problem_solving, motivation",
    "topic": "Specific topic this covers (for tracking, e.g., 'system_design', 'debugging_problem_solving')",
    "why_this_question": "Brief explanation of why this question tests their growth or is appropriate",
    "tests_improvement_in": "If testing improvement, specify which weak area this probes (or null)",
    "evaluation_criteria": ["criterion1", "criterion2", "criterion3"]
  }}
]
```

Generate exactly {num_questions} questions now:"""

    return prompt


async def generate_progressive_questions(
    db: Session,
    candidate: Candidate,
    vertical: Vertical,
    role_type: Optional[RoleType] = None,
    num_questions: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate personalized, progressive interview questions using AI.

    This function:
    1. Gathers candidate profile data (resume, GitHub, transcript)
    2. Gets their interview history to avoid redundant topics
    3. Uses AI to generate personalized questions at appropriate difficulty
    4. Tracks what was asked for future interviews
    """
    from .resume import ResumeService  # Import here to avoid circular imports

    # Gather candidate data
    candidate_data = {}

    # Resume summary
    if candidate.resume_parsed_data:
        resume_data = candidate.resume_parsed_data
        candidate_data["resume_summary"] = f"""
- Education: {resume_data.get('education', 'Not specified')}
- Skills: {', '.join(resume_data.get('skills', [])) if resume_data.get('skills') else 'Not specified'}
- Experience: {resume_data.get('experience_summary', 'Not specified')}
- Projects: {resume_data.get('projects_summary', 'Not specified')}
"""
    else:
        candidate_data["resume_summary"] = "No resume data available"

    # GitHub summary
    if candidate.github_username and candidate.github_data:
        gh_data = candidate.github_data
        repos = gh_data.get('repos', [])[:5]  # Top 5 repos
        languages = gh_data.get('languages', {})

        repos_summary = "\n".join([
            f"  - {r.get('name', 'Unknown')}: {r.get('description', 'No description')[:100] if r.get('description') else 'No description'}"
            for r in repos
        ]) if repos else "No public repos"

        candidate_data["github_summary"] = f"""
- Username: {candidate.github_username}
- Top Languages: {', '.join(list(languages.keys())[:5]) if languages else 'Not available'}
- Notable Repos:
{repos_summary}
- Total Contributions: {gh_data.get('total_contributions', 'Not available')}
"""
    else:
        candidate_data["github_summary"] = "GitHub not connected"

    # Transcript summary (if available)
    if hasattr(candidate, 'transcript') and candidate.transcript:
        candidate_data["transcript_summary"] = f"""
- University: {candidate.university or 'Not specified'}
- Major: {candidate.major or 'Not specified'}
- GPA: {candidate.gpa or 'Not specified'}
- Notable Courses: (from transcript data)
"""
    else:
        candidate_data["transcript_summary"] = f"""
- University: {candidate.university or 'Not specified'}
- Major: {candidate.major or 'Not specified'}
- GPA: {candidate.gpa if hasattr(candidate, 'gpa') else 'Not specified'}
"""

    # Get interview history
    interview_history = get_candidate_interview_history(
        db, candidate.id, vertical
    )

    # Build the AI prompt
    prompt = build_progressive_question_prompt(
        candidate_data=candidate_data,
        interview_history=interview_history,
        vertical=vertical.value if isinstance(vertical, Vertical) else vertical,
        role_type=role_type.value if isinstance(role_type, RoleType) else role_type,
        num_questions=num_questions
    )

    # Call AI to generate questions
    try:
        questions = await _call_ai_for_questions(prompt)

        # Validate and return
        if questions and len(questions) >= num_questions:
            return questions[:num_questions]
        else:
            logger.warning(f"AI returned insufficient questions, using fallback")
            return _get_fallback_questions(vertical, interview_history, num_questions)

    except Exception as e:
        logger.error(f"Error generating progressive questions: {e}")
        return _get_fallback_questions(vertical, interview_history, num_questions)


async def _call_ai_for_questions(prompt: str) -> List[Dict[str, Any]]:
    """Call Claude API to generate questions."""
    import httpx

    # Use Claude exclusively
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured - cannot generate questions")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.claude_model,
                "max_tokens": 2000,
                "system": "You are an expert technical interviewer. Always respond with valid JSON.",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code != 200:
            logger.error(f"Claude API error: {response.status_code} - {response.text}")
            raise Exception(f"Claude API returned {response.status_code}")

        result = response.json()
        content = result["content"][0]["text"]

        # Parse JSON from response
        # Handle markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        questions = json.loads(content.strip())
        return questions


def _get_fallback_questions(
    vertical: Vertical,
    interview_history: Dict[str, Any],
    num_questions: int
) -> List[Dict[str, Any]]:
    """Get fallback questions if AI generation fails."""
    from ..schemas.question import (
        SOFTWARE_ENGINEERING_LEVEL_1, SOFTWARE_ENGINEERING_LEVEL_2, SOFTWARE_ENGINEERING_LEVEL_3,
        DATA_LEVEL_1, DATA_LEVEL_2, DATA_LEVEL_3,
        PRODUCT_LEVEL_1, PRODUCT_LEVEL_2, PRODUCT_LEVEL_3,
        DESIGN_LEVEL_1, DESIGN_LEVEL_2, DESIGN_LEVEL_3,
        FINANCE_LEVEL_1, FINANCE_LEVEL_2, FINANCE_LEVEL_3,
        DEFAULT_QUESTIONS
    )

    difficulty = interview_history.get("recommended_difficulty", 1)
    topics_asked = set(interview_history.get("topics_asked", []))

    vertical_str = vertical.value if isinstance(vertical, Vertical) else vertical

    # Get appropriate question set based on vertical and difficulty
    question_sets = {
        "software_engineering": {1: SOFTWARE_ENGINEERING_LEVEL_1, 2: SOFTWARE_ENGINEERING_LEVEL_2, 3: SOFTWARE_ENGINEERING_LEVEL_3},
        "data": {1: DATA_LEVEL_1, 2: DATA_LEVEL_2, 3: DATA_LEVEL_3},
        "product": {1: PRODUCT_LEVEL_1, 2: PRODUCT_LEVEL_2, 3: PRODUCT_LEVEL_3},
        "design": {1: DESIGN_LEVEL_1, 2: DESIGN_LEVEL_2, 3: DESIGN_LEVEL_3},
        "finance": {1: FINANCE_LEVEL_1, 2: FINANCE_LEVEL_2, 3: FINANCE_LEVEL_3},
    }

    if vertical_str in question_sets:
        questions = question_sets[vertical_str].get(difficulty, question_sets[vertical_str][1])
    else:
        questions = DEFAULT_QUESTIONS

    # Filter out questions on topics already asked
    filtered = [
        q for q in questions
        if q.get("category") not in topics_asked
    ]

    # If not enough filtered, include all
    if len(filtered) < num_questions:
        filtered = questions

    return filtered[:num_questions]


def record_questions_asked(
    db: Session,
    candidate_id: str,
    session_id: str,
    questions: List[Dict[str, Any]],
    vertical: Optional[Vertical] = None
) -> None:
    """
    Record which questions were asked to prevent future repetition.
    """
    import uuid

    for q in questions:
        history_entry = CandidateQuestionHistory(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            question_key=q.get("question_key", q.get("topic", "unknown")),
            question_text=q.get("text", ""),
            vertical=vertical,
            difficulty_level=q.get("difficulty_level", 1),
            category=q.get("category") or q.get("topic"),
            interview_session_id=session_id,
        )
        db.add(history_entry)

    db.commit()


def update_question_scores(
    db: Session,
    session_id: str,
    question_scores: Dict[int, float]  # question_index -> score
) -> None:
    """
    Update scores for questions asked in a session.
    Called after scoring is complete.
    """
    history_entries = db.query(CandidateQuestionHistory).filter(
        CandidateQuestionHistory.interview_session_id == session_id
    ).all()

    for i, entry in enumerate(history_entries):
        if i in question_scores:
            entry.score = question_scores[i]

    db.commit()
