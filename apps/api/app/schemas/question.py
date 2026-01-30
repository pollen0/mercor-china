from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionCreate(BaseModel):
    text: str
    category: Optional[str] = None  # "background", "behavioral", "technical", "problem_solving", "motivation"
    order: int = 0
    job_id: Optional[str] = None
    duration_seconds: int = 180  # Default 3 minutes


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    duration_seconds: Optional[int] = None


class QuestionResponse(BaseModel):
    id: str
    text: str
    category: Optional[str] = None
    order: int
    is_default: bool
    job_id: Optional[str] = None
    duration_seconds: int = 180
    question_type: str = "video"  # "video" or "coding"
    coding_challenge_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionList(BaseModel):
    questions: list[QuestionResponse]
    total: int


# =============================================================================
# INTERVIEW QUESTION TEMPLATES FOR US COLLEGE STUDENTS
# =============================================================================

# Engineering/Tech Vertical Questions
ENGINEERING_QUESTIONS = [
    {
        "text": "Tell me about yourself and what got you interested in technology.",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Describe a technical project you've built. What was the most challenging part?",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "technical_depth", "communication"]
    },
    {
        "text": "Tell me about a bug that took you a long time to fix. How did you approach debugging it?",
        "category": "problem_solving",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "persistence", "methodology"]
    },
    {
        "text": "Describe a time you worked on a team project. What was your role and how did you collaborate?",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["teamwork", "communication", "collaboration"]
    },
    {
        "text": "What technology are you most excited to learn and why?",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "curiosity", "industry_awareness"]
    }
]

# Data Science/Analytics Vertical Questions
DATA_QUESTIONS = [
    {
        "text": "Tell me about yourself and your interest in data.",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Describe a data analysis project you've worked on. What insights did you find?",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["analytical_thinking", "technical_depth", "communication"]
    },
    {
        "text": "How would you explain a complex data finding to a non-technical stakeholder?",
        "category": "problem_solving",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "simplification", "business_acumen"]
    },
    {
        "text": "Tell me about a time you had to clean messy data. What was your approach?",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "attention_to_detail", "methodology"]
    },
    {
        "text": "What excites you about the future of data science and AI?",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "curiosity", "industry_awareness"]
    }
]

# Business/Product Vertical Questions
BUSINESS_QUESTIONS = [
    {
        "text": "Tell me about yourself and what drew you to business/product.",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Describe a time you had to analyze data to make a decision. What was your process?",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["analytical_thinking", "decision_making", "communication"]
    },
    {
        "text": "Tell me about a time you had to influence others without having direct authority.",
        "category": "behavioral",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "persuasion", "collaboration"]
    },
    {
        "text": "How do you prioritize when you have multiple competing deadlines?",
        "category": "problem_solving",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["organization", "decision_making", "stress_management"]
    },
    {
        "text": "Tell me about a failure and what you learned from it.",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "self_awareness", "resilience"]
    }
]

# Design Vertical Questions
DESIGN_QUESTIONS = [
    {
        "text": "Tell me about yourself and your design journey.",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Walk me through your design process for a recent project.",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["design_thinking", "methodology", "communication"]
    },
    {
        "text": "How do you handle feedback on your designs, especially critical feedback?",
        "category": "behavioral",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "collaboration", "professionalism"]
    },
    {
        "text": "Describe a time you had to balance user needs with business requirements.",
        "category": "problem_solving",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["user_empathy", "business_acumen", "decision_making"]
    },
    {
        "text": "What design trends are you following and why?",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "curiosity", "industry_awareness"]
    }
]

# Default generic questions (fallback)
DEFAULT_QUESTIONS = [
    {
        "text": "Tell me about yourself and your background.",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
    },
    {
        "text": "What are you most passionate about in your field of study?",
        "category": "motivation",
        "order": 1,
        "duration_seconds": 180,
    },
    {
        "text": "Describe a challenging project you've worked on.",
        "category": "behavioral",
        "order": 2,
        "duration_seconds": 180,
    },
    {
        "text": "Tell me about a time you had to learn something new quickly.",
        "category": "problem_solving",
        "order": 3,
        "duration_seconds": 180,
    },
    {
        "text": "What are your career goals and how does this role fit into them?",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
    },
]


def get_questions_for_role(vertical: str, role_type: str) -> list[dict]:
    """Get the appropriate question template based on vertical and role type."""
    # Map verticals to question templates
    vertical_question_map = {
        "engineering": ENGINEERING_QUESTIONS,
        "data": DATA_QUESTIONS,
        "business": BUSINESS_QUESTIONS,
        "design": DESIGN_QUESTIONS,
    }

    # Try to get vertical-specific questions
    if vertical and vertical in vertical_question_map:
        return vertical_question_map[vertical]

    # Final fallback to default questions
    return DEFAULT_QUESTIONS
