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
# PROGRESSIVE INTERVIEW QUESTION TEMPLATES FOR US COLLEGE STUDENTS
# Based on actual new grad job market (2026 SWE College Jobs)
#
# DIFFICULTY LEVELS:
# Level 1 (Foundational): First interview - basic behavioral and intro technical
# Level 2 (Intermediate): 2nd+ interview with score 5-7 - deeper technical, real scenarios
# Level 3 (Advanced): 3rd+ interview with score 7+ - system design, leadership, complex scenarios
# =============================================================================

# =============================================================================
# SOFTWARE ENGINEERING QUESTIONS - MULTI-LEVEL
# =============================================================================

SOFTWARE_ENGINEERING_LEVEL_1 = [
    {
        "text": "Tell me about yourself and what got you interested in software engineering.",
        "question_key": "swe_l1_intro",
        "category": "background",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Describe a technical project you've built. What was the most challenging part and how did you overcome it?",
        "question_key": "swe_l1_project",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "technical_depth", "communication"]
    },
    {
        "text": "Tell me about a bug that took you a long time to fix. Walk me through your debugging process.",
        "question_key": "swe_l1_debugging",
        "category": "problem_solving",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "persistence", "methodology"]
    },
    {
        "text": "Describe a time you worked on a team project. What was your role and how did you handle disagreements?",
        "question_key": "swe_l1_teamwork",
        "category": "behavioral",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["teamwork", "communication", "collaboration"]
    },
    {
        "text": "What technology or programming concept are you most excited to learn next and why?",
        "question_key": "swe_l1_learning",
        "category": "motivation",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "curiosity", "industry_awareness"]
    },
    {
        "text": "Walk me through how you approach learning a new programming language or framework.",
        "question_key": "swe_l1_learning_approach",
        "category": "problem_solving",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["learning_ability", "methodology", "self_awareness"]
    },
]

SOFTWARE_ENGINEERING_LEVEL_2 = [
    {
        "text": "Tell me about a time you had to make a significant technical decision. What trade-offs did you consider?",
        "question_key": "swe_l2_tradeoffs",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["decision_making", "technical_depth", "communication"]
    },
    {
        "text": "Describe a situation where you had to optimize code for performance. What was your approach?",
        "question_key": "swe_l2_optimization",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["performance_awareness", "problem_solving", "technical_depth"]
    },
    {
        "text": "Tell me about a time you had to work with legacy code. How did you approach understanding and modifying it?",
        "question_key": "swe_l2_legacy",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["code_comprehension", "adaptability", "methodology"]
    },
    {
        "text": "How do you ensure code quality in your projects? Tell me about your testing and review practices.",
        "question_key": "swe_l2_quality",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["quality_mindset", "best_practices", "thoroughness"]
    },
    {
        "text": "Describe a time you had to push back on a technical decision or deadline. How did you handle it?",
        "question_key": "swe_l2_pushback",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["assertiveness", "communication", "professionalism"]
    },
    {
        "text": "Tell me about a time you mentored someone or helped a teammate learn something new.",
        "question_key": "swe_l2_mentoring",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "communication", "patience"]
    },
    {
        "text": "How do you stay current with rapidly changing technology trends? Give specific examples.",
        "question_key": "swe_l2_trends",
        "category": "motivation",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "industry_awareness", "self_improvement"]
    },
    {
        "text": "Describe a project where you had to integrate with external APIs or services. What challenges did you face?",
        "question_key": "swe_l2_integration",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["systems_thinking", "problem_solving", "communication"]
    },
]

SOFTWARE_ENGINEERING_LEVEL_3 = [
    {
        "text": "If you were designing a system to handle millions of users, what architectural patterns would you consider?",
        "question_key": "swe_l3_system_design",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["system_design", "scalability", "technical_breadth"]
    },
    {
        "text": "Tell me about a time you identified a systemic problem in a codebase or process and drove a solution.",
        "question_key": "swe_l3_systemic",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "systems_thinking", "initiative"]
    },
    {
        "text": "How would you approach breaking down a large, ambiguous project into manageable pieces?",
        "question_key": "swe_l3_breakdown",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["planning", "ambiguity_tolerance", "structured_thinking"]
    },
    {
        "text": "Describe a situation where you had to balance technical debt against feature development. How did you decide?",
        "question_key": "swe_l3_tech_debt",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["prioritization", "business_acumen", "technical_judgment"]
    },
    {
        "text": "Tell me about a time you had to lead a technical project or coordinate multiple engineers.",
        "question_key": "swe_l3_leadership",
        "category": "behavioral",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "coordination", "communication"]
    },
    {
        "text": "How would you design a CI/CD pipeline for a team of 10 engineers? What would you prioritize?",
        "question_key": "swe_l3_devops",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["devops_knowledge", "systems_thinking", "team_awareness"]
    },
    {
        "text": "Describe how you would approach refactoring a critical system without disrupting users.",
        "question_key": "swe_l3_refactor",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["risk_management", "planning", "technical_depth"]
    },
    {
        "text": "What's a technical opinion you hold strongly? Defend it while acknowledging counterarguments.",
        "question_key": "swe_l3_opinion",
        "category": "motivation",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["critical_thinking", "communication", "intellectual_humility"]
    },
]

# Keep legacy constant for backwards compatibility
SOFTWARE_ENGINEERING_QUESTIONS = SOFTWARE_ENGINEERING_LEVEL_1[:5]

# =============================================================================
# DATA SCIENCE/ML QUESTIONS - MULTI-LEVEL
# =============================================================================

DATA_LEVEL_1 = [
    {
        "text": "Tell me about yourself and what drew you to data science.",
        "question_key": "data_l1_intro",
        "category": "background",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Describe a data analysis or ML project you've worked on. What insights did you find?",
        "question_key": "data_l1_project",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["analytical_thinking", "technical_depth", "communication"]
    },
    {
        "text": "How would you explain a complex model or statistical finding to a non-technical stakeholder?",
        "question_key": "data_l1_explain",
        "category": "problem_solving",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "simplification", "business_acumen"]
    },
    {
        "text": "Tell me about a time you had to deal with messy or incomplete data. What was your approach?",
        "question_key": "data_l1_messy_data",
        "category": "behavioral",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "attention_to_detail", "methodology"]
    },
    {
        "text": "What excites you about the future of AI and machine learning? What risks concern you?",
        "question_key": "data_l1_future",
        "category": "motivation",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "curiosity", "industry_awareness"]
    },
    {
        "text": "Walk me through how you would approach a new dataset. What's your exploration process?",
        "question_key": "data_l1_eda",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["methodology", "curiosity", "technical_depth"]
    },
]

DATA_LEVEL_2 = [
    {
        "text": "How do you choose between different ML algorithms for a given problem? Walk me through your decision process.",
        "question_key": "data_l2_algo_selection",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["technical_depth", "decision_making", "methodology"]
    },
    {
        "text": "Describe a time when your model performed well in training but poorly in production. What did you learn?",
        "question_key": "data_l2_production",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["ml_engineering", "problem_solving", "learning_ability"]
    },
    {
        "text": "How do you handle class imbalance in a classification problem? What techniques have you used?",
        "question_key": "data_l2_imbalance",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["technical_depth", "practical_knowledge", "methodology"]
    },
    {
        "text": "Tell me about a time when your analysis contradicted stakeholder expectations. How did you handle it?",
        "question_key": "data_l2_stakeholder",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "integrity", "stakeholder_management"]
    },
    {
        "text": "How do you ensure reproducibility in your data science projects?",
        "question_key": "data_l2_reproducibility",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["best_practices", "rigor", "methodology"]
    },
    {
        "text": "Describe your experience with A/B testing. What makes a good experiment design?",
        "question_key": "data_l2_ab_testing",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["experimentation", "statistics", "practical_knowledge"]
    },
]

DATA_LEVEL_3 = [
    {
        "text": "How would you design an ML system that needs to make real-time predictions at scale?",
        "question_key": "data_l3_realtime",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["system_design", "ml_engineering", "scalability"]
    },
    {
        "text": "Tell me about a time you had to build buy-in for a data-driven approach in a skeptical organization.",
        "question_key": "data_l3_buy_in",
        "category": "behavioral",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["influence", "communication", "leadership"]
    },
    {
        "text": "How do you approach model monitoring and detecting data drift in production?",
        "question_key": "data_l3_monitoring",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["ml_ops", "systems_thinking", "practical_knowledge"]
    },
    {
        "text": "Describe how you would prioritize multiple data science projects with different stakeholders.",
        "question_key": "data_l3_prioritization",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["prioritization", "stakeholder_management", "business_acumen"]
    },
    {
        "text": "What ethical considerations do you think about when building ML systems? Give specific examples.",
        "question_key": "data_l3_ethics",
        "category": "motivation",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["ethics", "critical_thinking", "responsibility"]
    },
    {
        "text": "How would you design a recommendation system for a product with millions of users?",
        "question_key": "data_l3_recsys",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["system_design", "ml_knowledge", "scalability"]
    },
]

# Keep legacy constant for backwards compatibility
DATA_QUESTIONS = DATA_LEVEL_1[:5]

# =============================================================================
# PRODUCT MANAGEMENT QUESTIONS - MULTI-LEVEL
# =============================================================================

PRODUCT_LEVEL_1 = [
    {
        "text": "Tell me about yourself and what drew you to product management.",
        "question_key": "pm_l1_intro",
        "category": "background",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Tell me about a product you love. What makes it great and what would you improve?",
        "question_key": "pm_l1_product",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["product_sense", "analytical_thinking", "communication"]
    },
    {
        "text": "How would you prioritize features for a new product with limited engineering resources?",
        "question_key": "pm_l1_prioritize",
        "category": "problem_solving",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["prioritization", "decision_making", "strategic_thinking"]
    },
    {
        "text": "Tell me about a time you had to influence others without having direct authority.",
        "question_key": "pm_l1_influence",
        "category": "behavioral",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "persuasion", "collaboration"]
    },
    {
        "text": "Describe a product launch or project that didn't go as planned. What did you learn?",
        "question_key": "pm_l1_failure",
        "category": "motivation",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "self_awareness", "resilience"]
    },
]

PRODUCT_LEVEL_2 = [
    {
        "text": "How do you gather and synthesize user feedback to inform product decisions?",
        "question_key": "pm_l2_user_feedback",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["user_empathy", "methodology", "synthesis"]
    },
    {
        "text": "Tell me about a time you had to say no to a stakeholder's feature request. How did you handle it?",
        "question_key": "pm_l2_say_no",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "prioritization", "stakeholder_management"]
    },
    {
        "text": "How do you measure the success of a feature? What metrics would you track?",
        "question_key": "pm_l2_metrics",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["data_driven", "analytical_thinking", "strategic_thinking"]
    },
    {
        "text": "Describe how you would conduct a competitive analysis for a new market.",
        "question_key": "pm_l2_competitive",
        "category": "problem_solving",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["strategic_thinking", "research", "market_awareness"]
    },
    {
        "text": "How do you manage technical debt vs. new feature development with your engineering team?",
        "question_key": "pm_l2_tech_debt",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["technical_acumen", "prioritization", "collaboration"]
    },
]

PRODUCT_LEVEL_3 = [
    {
        "text": "How would you develop a go-to-market strategy for a new B2B product?",
        "question_key": "pm_l3_gtm",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["strategy", "market_awareness", "execution"]
    },
    {
        "text": "Tell me about a time you had to pivot a product strategy based on new data or market conditions.",
        "question_key": "pm_l3_pivot",
        "category": "behavioral",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["adaptability", "decision_making", "leadership"]
    },
    {
        "text": "How do you balance short-term revenue goals with long-term product vision?",
        "question_key": "pm_l3_balance",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["strategic_thinking", "business_acumen", "prioritization"]
    },
    {
        "text": "Describe how you would approach building a platform product with multiple stakeholder groups.",
        "question_key": "pm_l3_platform",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["systems_thinking", "stakeholder_management", "strategy"]
    },
    {
        "text": "How would you structure and lead a product team through a major company transformation?",
        "question_key": "pm_l3_transformation",
        "category": "behavioral",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "change_management", "communication"]
    },
]

# Keep legacy constant for backwards compatibility
PRODUCT_QUESTIONS = PRODUCT_LEVEL_1[:5]

# =============================================================================
# DESIGN QUESTIONS - MULTI-LEVEL
# =============================================================================

DESIGN_LEVEL_1 = [
    {
        "text": "Tell me about yourself and your design journey.",
        "question_key": "design_l1_intro",
        "category": "background",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Walk me through your design process for a recent project.",
        "question_key": "design_l1_process",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["design_thinking", "methodology", "communication"]
    },
    {
        "text": "How do you handle critical feedback on your designs? Give me a specific example.",
        "question_key": "design_l1_feedback",
        "category": "behavioral",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "collaboration", "professionalism"]
    },
    {
        "text": "Describe a time you had to balance user needs with business requirements.",
        "question_key": "design_l1_balance",
        "category": "problem_solving",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["user_empathy", "business_acumen", "decision_making"]
    },
    {
        "text": "What design trends or tools are you following right now and why?",
        "question_key": "design_l1_trends",
        "category": "motivation",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["growth_mindset", "curiosity", "industry_awareness"]
    },
]

DESIGN_LEVEL_2 = [
    {
        "text": "How do you conduct user research and translate findings into design decisions?",
        "question_key": "design_l2_research",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["research_skills", "synthesis", "user_empathy"]
    },
    {
        "text": "Describe how you measure the success of your designs after launch.",
        "question_key": "design_l2_metrics",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["data_driven", "iteration", "impact_awareness"]
    },
    {
        "text": "Tell me about a time you had to advocate strongly for a design decision against pushback.",
        "question_key": "design_l2_advocate",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["advocacy", "communication", "conviction"]
    },
    {
        "text": "How do you approach designing for accessibility? Give specific examples.",
        "question_key": "design_l2_accessibility",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["accessibility_awareness", "inclusive_design", "technical_depth"]
    },
    {
        "text": "How do you collaborate with engineers to ensure design fidelity in implementation?",
        "question_key": "design_l2_collaboration",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["collaboration", "communication", "technical_understanding"]
    },
]

DESIGN_LEVEL_3 = [
    {
        "text": "How would you establish a design system for a growing company?",
        "question_key": "design_l3_system",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["systems_thinking", "scalability", "leadership"]
    },
    {
        "text": "Describe how you would approach redesigning a complex enterprise product.",
        "question_key": "design_l3_enterprise",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["complexity_management", "stakeholder_management", "strategy"]
    },
    {
        "text": "How do you mentor junior designers and elevate design culture in an organization?",
        "question_key": "design_l3_mentoring",
        "category": "behavioral",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["leadership", "mentoring", "culture_building"]
    },
    {
        "text": "Tell me about a design that had significant business impact. How did you measure and communicate that impact?",
        "question_key": "design_l3_impact",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["business_acumen", "impact_measurement", "communication"]
    },
    {
        "text": "How do you balance innovation with consistency when evolving a mature product?",
        "question_key": "design_l3_innovation",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["strategic_thinking", "balance", "user_awareness"]
    },
]

# Keep legacy constant for backwards compatibility
DESIGN_QUESTIONS = DESIGN_LEVEL_1[:5]

# =============================================================================
# FINANCE QUESTIONS - MULTI-LEVEL
# =============================================================================

FINANCE_LEVEL_1 = [
    {
        "text": "Tell me about yourself and why you're interested in finance/investment banking.",
        "question_key": "fin_l1_intro",
        "category": "background",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Walk me through a DCF analysis. What are the key inputs?",
        "question_key": "fin_l1_dcf",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["technical_knowledge", "analytical_thinking", "communication"]
    },
    {
        "text": "Walk me through the three main valuation methodologies.",
        "question_key": "fin_l1_valuation",
        "category": "technical",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["technical_knowledge", "structured_thinking", "communication"]
    },
    {
        "text": "Tell me about a deal or market event you've been following. What's your view?",
        "question_key": "fin_l1_market",
        "category": "problem_solving",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["market_awareness", "analytical_thinking", "communication"]
    },
    {
        "text": "Why investment banking over other finance roles?",
        "question_key": "fin_l1_why_ib",
        "category": "motivation",
        "difficulty_level": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "self_awareness", "commitment"]
    },
]

FINANCE_LEVEL_2 = [
    {
        "text": "How would you analyze whether a company should pursue an M&A transaction?",
        "question_key": "fin_l2_ma_analysis",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["strategic_thinking", "technical_depth", "business_acumen"]
    },
    {
        "text": "Walk me through how you would build an LBO model. What are the key drivers?",
        "question_key": "fin_l2_lbo",
        "category": "technical",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["technical_knowledge", "modeling_skills", "communication"]
    },
    {
        "text": "How do you stay current with market trends and economic developments?",
        "question_key": "fin_l2_current",
        "category": "motivation",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["market_awareness", "proactivity", "intellectual_curiosity"]
    },
    {
        "text": "Describe a time you had to work under extreme time pressure. How did you manage?",
        "question_key": "fin_l2_pressure",
        "category": "behavioral",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["stress_management", "time_management", "execution"]
    },
    {
        "text": "How would you advise a client choosing between different financing options?",
        "question_key": "fin_l2_financing",
        "category": "problem_solving",
        "difficulty_level": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["advisory_skills", "technical_knowledge", "communication"]
    },
]

FINANCE_LEVEL_3 = [
    {
        "text": "If a company's stock dropped 20% today, walk me through how you would analyze what happened.",
        "question_key": "fin_l3_stock_drop",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["analytical_thinking", "market_awareness", "structured_thinking"]
    },
    {
        "text": "How would you structure a sell-side process for a mid-market tech company?",
        "question_key": "fin_l3_sellside",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["process_knowledge", "strategic_thinking", "execution"]
    },
    {
        "text": "What's your view on current Fed policy and its implications for deal activity?",
        "question_key": "fin_l3_macro",
        "category": "problem_solving",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["macro_awareness", "critical_thinking", "synthesis"]
    },
    {
        "text": "Tell me about a time you had to manage a difficult client relationship.",
        "question_key": "fin_l3_client",
        "category": "behavioral",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["client_management", "professionalism", "relationship_building"]
    },
    {
        "text": "How would you pitch a potential acquisition target to a strategic buyer?",
        "question_key": "fin_l3_pitch",
        "category": "technical",
        "difficulty_level": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["pitching_skills", "strategic_thinking", "persuasion"]
    },
]

# Keep legacy constant for backwards compatibility
FINANCE_QUESTIONS = FINANCE_LEVEL_1[:5]

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
    # Map verticals to question templates (based on 2026 new grad job market)
    vertical_question_map = {
        "software_engineering": SOFTWARE_ENGINEERING_QUESTIONS,
        "data": DATA_QUESTIONS,
        "product": PRODUCT_QUESTIONS,
        "design": DESIGN_QUESTIONS,
        "finance": FINANCE_QUESTIONS,
        # Legacy mappings for backwards compatibility
        "engineering": SOFTWARE_ENGINEERING_QUESTIONS,
        "business": PRODUCT_QUESTIONS,  # Map old business to product
    }

    # Try to get vertical-specific questions
    if vertical and vertical in vertical_question_map:
        return vertical_question_map[vertical]

    # Final fallback to default questions
    return DEFAULT_QUESTIONS
