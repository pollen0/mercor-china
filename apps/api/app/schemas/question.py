from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionCreate(BaseModel):
    text: str
    text_zh: Optional[str] = None
    category: Optional[str] = None  # "background", "behavioral", "technical", "roleplay", "motivation"
    order: int = 0
    job_id: Optional[str] = None
    duration_seconds: int = 180  # Default 3 minutes


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    text_zh: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    duration_seconds: Optional[int] = None


class QuestionResponse(BaseModel):
    id: str
    text: str
    text_zh: Optional[str] = None
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
# VERTICAL-SPECIFIC INTERVIEW QUESTION TEMPLATES
# =============================================================================

# Sales/BD Vertical Questions
SALES_INTERVIEW_QUESTIONS = [
    {
        "text": "Please introduce yourself and explain why you're interested in sales.",
        "text_zh": "请简单介绍一下你自己，以及你为什么对销售工作感兴趣？",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "motivation", "self_awareness"]
    },
    {
        "text": "Describe a time you successfully persuaded someone. How did you do it?",
        "text_zh": "请描述一次你成功说服别人接受你想法的经历。你是怎么做到的？",
        "category": "behavioral",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["persuasion", "problem_solving", "communication"]
    },
    {
        "text": "I'm a potential customer interested but concerned about price. How would you respond? Please demonstrate.",
        "text_zh": "假设我是一个潜在客户，对你们的产品有兴趣但觉得价格太贵。你会怎么回应？请现在演示一下。",
        "category": "roleplay",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["objection_handling", "persuasion", "composure"]
    },
    {
        "text": "Tell me about a time you missed a sales target. What happened and what did you learn?",
        "text_zh": "告诉我一次你没有完成销售目标的经历。发生了什么？你学到了什么？",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["self_awareness", "resilience", "learning_ability"]
    },
    {
        "text": "What are your career goals? Why did you choose our company?",
        "text_zh": "你的职业目标是什么？为什么选择我们公司？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "culture_fit", "preparation"]
    }
]

# New Energy/EV - Technical Roles (Battery Engineer, Embedded Software, Autonomous Driving)
NEW_ENERGY_TECHNICAL_QUESTIONS = [
    {
        "text": "Introduce your technical background and relevant experience in new energy/EV.",
        "text_zh": "请介绍一下你的技术背景，以及你在新能源/电动汽车领域的相关经验。",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "domain_knowledge", "experience"]
    },
    {
        "text": "Explain how lithium batteries work and the main factors affecting battery performance.",
        "text_zh": "请解释一下锂电池的工作原理，以及影响电池性能的主要因素有哪些？",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["domain_knowledge", "technical_depth", "communication"]
    },
    {
        "text": "If a battery shows abnormal heating during testing, how would you troubleshoot? Describe your approach.",
        "text_zh": "如果电池在测试中出现异常发热，你会如何排查问题？请描述你的思路。",
        "category": "technical",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "technical_depth", "methodology"]
    },
    {
        "text": "Describe the most challenging technical problem you've solved. What was the process?",
        "text_zh": "描述一个你解决过的最具挑战性的技术问题。过程是什么样的？",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "persistence", "technical_depth"]
    },
    {
        "text": "What's your view on the future of new energy? What contribution do you want to make?",
        "text_zh": "你对新能源行业的未来怎么看？你希望在这个领域做出什么贡献？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "industry_awareness", "vision"]
    }
]

# New Energy/EV - Sales Roles (EV Sales)
NEW_ENERGY_SALES_QUESTIONS = [
    {
        "text": "Introduce yourself and your understanding of the new energy vehicle industry.",
        "text_zh": "请介绍一下你自己，以及你对新能源汽车行业的了解。",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "industry_awareness", "motivation"]
    },
    {
        "text": "If a customer asks about your EV's advantages vs competitors, how would you respond?",
        "text_zh": "如果客户问你们的电动车和竞品相比有什么优势，你会怎么回答？",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["product_knowledge", "persuasion", "competitive_awareness"]
    },
    {
        "text": "Customer says: 'EV charging is too inconvenient, I'd rather buy a gas car.' Demonstrate your response.",
        "text_zh": "客户说：'电动车充电太麻烦了，我还是想买燃油车。' 请现场演示你如何回应。",
        "category": "roleplay",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["objection_handling", "product_knowledge", "persuasion"]
    },
    {
        "text": "Describe a time you exceeded your sales target. How did you achieve it?",
        "text_zh": "描述一次你超额完成销售目标的经历。你是怎么做到的？",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["achievement", "strategy", "persistence"]
    },
    {
        "text": "What's your career plan? Why do you want to join us?",
        "text_zh": "你的职业规划是什么？为什么想加入我们？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "culture_fit", "ambition"]
    }
]

# Embedded Software Questions
EMBEDDED_SOFTWARE_QUESTIONS = [
    {
        "text": "Introduce your embedded software development background and experience.",
        "text_zh": "请介绍一下你的嵌入式软件开发背景和经验。",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "domain_knowledge", "experience"]
    },
    {
        "text": "Explain the difference between RTOS and bare-metal programming. When would you use each?",
        "text_zh": "请解释RTOS和裸机编程的区别。什么情况下你会选择使用哪种？",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["domain_knowledge", "technical_depth", "decision_making"]
    },
    {
        "text": "How would you debug a memory leak in an embedded system with limited resources?",
        "text_zh": "在资源有限的嵌入式系统中，你会如何调试内存泄漏问题？",
        "category": "technical",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "technical_depth", "methodology"]
    },
    {
        "text": "Describe a complex embedded project you've worked on. What were the main challenges?",
        "text_zh": "描述一个你参与过的复杂嵌入式项目。主要挑战是什么？",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "project_experience", "communication"]
    },
    {
        "text": "Where do you see embedded systems going in the EV industry? What excites you about it?",
        "text_zh": "你认为嵌入式系统在电动汽车行业的发展方向是什么？什么让你感到兴奋？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "industry_awareness", "vision"]
    }
]

# Autonomous Driving Questions
AUTONOMOUS_DRIVING_QUESTIONS = [
    {
        "text": "Introduce your background in autonomous driving or related fields.",
        "text_zh": "请介绍一下你在自动驾驶或相关领域的背景。",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "domain_knowledge", "experience"]
    },
    {
        "text": "Explain the key components of an autonomous driving system and how they work together.",
        "text_zh": "请解释自动驾驶系统的关键组成部分以及它们如何协同工作。",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["domain_knowledge", "system_thinking", "communication"]
    },
    {
        "text": "How would you approach validating the safety of an autonomous driving algorithm?",
        "text_zh": "你会如何验证自动驾驶算法的安全性？",
        "category": "technical",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "safety_awareness", "methodology"]
    },
    {
        "text": "Describe a challenging algorithm or simulation problem you've solved.",
        "text_zh": "描述一个你解决过的具有挑战性的算法或仿真问题。",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "technical_depth", "persistence"]
    },
    {
        "text": "What's your view on the timeline for Level 4/5 autonomy? What role do you want to play?",
        "text_zh": "你对L4/L5级自动驾驶实现的时间线有什么看法？你想在其中扮演什么角色？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "industry_awareness", "vision"]
    }
]

# Supply Chain Questions
SUPPLY_CHAIN_QUESTIONS = [
    {
        "text": "Introduce your supply chain management background and experience.",
        "text_zh": "请介绍一下你的供应链管理背景和经验。",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
        "evaluation_criteria": ["communication", "domain_knowledge", "experience"]
    },
    {
        "text": "How would you approach supplier evaluation and selection for EV battery components?",
        "text_zh": "你会如何评估和选择电动汽车电池组件的供应商？",
        "category": "technical",
        "order": 1,
        "duration_seconds": 180,
        "evaluation_criteria": ["domain_knowledge", "analytical_thinking", "methodology"]
    },
    {
        "text": "A key supplier suddenly announces a 30% price increase. How would you handle this?",
        "text_zh": "一个关键供应商突然宣布价格上涨30%。你会如何处理这种情况？",
        "category": "roleplay",
        "order": 2,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "negotiation", "composure"]
    },
    {
        "text": "Describe a supply chain crisis you've managed. What was your approach?",
        "text_zh": "描述一次你处理过的供应链危机。你的处理方法是什么？",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
        "evaluation_criteria": ["problem_solving", "crisis_management", "leadership"]
    },
    {
        "text": "What unique challenges does supply chain in the EV industry face? How do you see it evolving?",
        "text_zh": "电动汽车行业的供应链面临哪些独特挑战？你认为它会如何发展？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
        "evaluation_criteria": ["motivation", "industry_awareness", "strategic_thinking"]
    }
]

# Default generic questions (fallback)
DEFAULT_QUESTIONS = [
    {
        "text": "Tell me about yourself and your background",
        "text_zh": "请介绍一下你自己和你的背景",
        "category": "background",
        "order": 0,
        "duration_seconds": 180,
    },
    {
        "text": "Why are you interested in this role?",
        "text_zh": "你为什么对这个职位感兴趣？",
        "category": "motivation",
        "order": 1,
        "duration_seconds": 180,
    },
    {
        "text": "Describe a challenging project you've worked on",
        "text_zh": "描述一个你曾经参与过的具有挑战性的项目",
        "category": "behavioral",
        "order": 2,
        "duration_seconds": 180,
    },
    {
        "text": "How do you handle working under pressure?",
        "text_zh": "你是如何应对工作压力的？",
        "category": "behavioral",
        "order": 3,
        "duration_seconds": 180,
    },
    {
        "text": "What are your career goals for the next 3-5 years?",
        "text_zh": "你未来3-5年的职业目标是什么？",
        "category": "motivation",
        "order": 4,
        "duration_seconds": 180,
    },
]


def get_questions_for_role(vertical: str, role_type: str) -> list[dict]:
    """Get the appropriate question template based on vertical and role type."""
    # Map role types to question templates
    role_question_map = {
        # New Energy Technical Roles
        "battery_engineer": NEW_ENERGY_TECHNICAL_QUESTIONS,
        "embedded_software": EMBEDDED_SOFTWARE_QUESTIONS,
        "autonomous_driving": AUTONOMOUS_DRIVING_QUESTIONS,
        "supply_chain": SUPPLY_CHAIN_QUESTIONS,
        # New Energy Sales
        "ev_sales": NEW_ENERGY_SALES_QUESTIONS,
        # General Sales
        "sales_rep": SALES_INTERVIEW_QUESTIONS,
        "bd_manager": SALES_INTERVIEW_QUESTIONS,
        "account_manager": SALES_INTERVIEW_QUESTIONS,
    }

    # Try to get role-specific questions
    if role_type and role_type in role_question_map:
        return role_question_map[role_type]

    # Fall back to vertical-based questions
    if vertical == "new_energy":
        return NEW_ENERGY_TECHNICAL_QUESTIONS
    elif vertical == "sales":
        return SALES_INTERVIEW_QUESTIONS

    # Final fallback to default questions
    return DEFAULT_QUESTIONS
