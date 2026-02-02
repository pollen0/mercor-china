import httpx
import json
import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from ..config import settings

logger = logging.getLogger("pathway.scoring")

# =============================================================================
# SCORING ALGORITHM VERSION - INCREMENT WHEN CHANGING SCORING LOGIC
# =============================================================================
SCORING_ALGORITHM_VERSION = "2.0.0"  # Major.Minor.Patch
# Version history:
# 1.0.0 - Initial scoring with generic rubric
# 2.0.0 - Vertical-specific rubrics with industry-standard questions


@dataclass
class ScoreResult:
    """Result of AI scoring for a single response."""
    communication: float  # Clarity and articulation
    problem_solving: float  # Analytical thinking
    domain_knowledge: float  # Technical knowledge
    motivation: float  # Growth mindset
    culture_fit: float  # Teamwork and values
    overall: float
    analysis: str
    strengths: list[str]
    concerns: list[str]
    highlight_quotes: list[str]
    raw_response: Optional[dict] = None
    # Versioning for future re-scoring
    algorithm_version: str = SCORING_ALGORITHM_VERSION
    scored_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    vertical: Optional[str] = None
    raw_score_before_normalization: Optional[float] = None


@dataclass
class InterviewSummary:
    """Overall interview summary."""
    total_score: float
    summary: str
    overall_strengths: list[str]
    overall_concerns: list[str]
    recommendation: str  # "advance", "maybe", "reject"
    raw_response: Optional[dict] = None


class ScoringService:
    """Service for AI-powered interview scoring using Claude Sonnet 4.5."""

    # =============================================================================
    # VERTICAL-SPECIFIC SCORING WEIGHTS & RUBRICS
    # Each vertical has different priorities based on industry standards
    # =============================================================================

    VERTICAL_SCORING_CONFIG = {
        'software_engineering': {
            'weights': {
                'communication': 0.15,
                'problem_solving': 0.30,  # Higher for SWE
                'domain_knowledge': 0.30,  # Technical depth important
                'motivation': 0.10,
                'culture_fit': 0.15
            },
            'rubric': """
SCORING RUBRIC FOR SOFTWARE ENGINEERING:

1. Communication (15%)
   - Clear explanation of technical concepts
   - Structured thinking (STAR method)
   - Can explain complex ideas simply

2. Problem Solving (30%) - CRITICAL FOR SWE
   - Systematic debugging approach
   - Algorithm design thinking
   - Edge case consideration
   - Time/space complexity awareness

3. Technical Knowledge (30%) - CRITICAL FOR SWE
   - Programming fundamentals (data structures, algorithms)
   - System design basics
   - Software engineering practices (testing, version control)
   - Technology stack familiarity

4. Growth Mindset (10%)
   - Learning new technologies
   - Handling technical challenges
   - Staying current with industry

5. Culture Fit (15%)
   - Team collaboration (code reviews, pair programming)
   - Communication in technical teams
   - Handling disagreements professionally
"""
        },
        'data': {
            'weights': {
                'communication': 0.20,  # Data storytelling important
                'problem_solving': 0.25,
                'domain_knowledge': 0.30,  # Statistical/ML knowledge
                'motivation': 0.10,
                'culture_fit': 0.15
            },
            'rubric': """
SCORING RUBRIC FOR DATA ROLES:

1. Communication (20%) - Data Storytelling
   - Explaining complex findings to non-technical stakeholders
   - Data visualization intuition
   - Clear and concise insights

2. Problem Solving (25%)
   - Analytical thinking
   - Hypothesis formation and testing
   - Handling ambiguous problems

3. Technical Knowledge (30%) - DATA SPECIFIC
   - Statistics and probability fundamentals
   - SQL and data manipulation
   - ML concepts (for DS/MLE roles)
   - Data pipeline understanding (for DE roles)

4. Growth Mindset (10%)
   - Keeping up with ML/AI advances
   - Learning new tools and frameworks

5. Culture Fit (15%)
   - Cross-functional collaboration
   - Stakeholder management
"""
        },
        'product': {
            'weights': {
                'communication': 0.25,  # Critical for PM
                'problem_solving': 0.25,  # Prioritization, strategy
                'domain_knowledge': 0.20,  # Product sense
                'motivation': 0.15,
                'culture_fit': 0.15
            },
            'rubric': """
SCORING RUBRIC FOR PRODUCT MANAGEMENT:

1. Communication (25%) - CRITICAL FOR PM
   - Stakeholder communication
   - Presenting ideas persuasively
   - Written and verbal clarity

2. Problem Solving (25%) - Product Strategy
   - Prioritization frameworks (RICE, MoSCoW)
   - Trade-off analysis
   - Root cause analysis
   - Customer problem identification

3. Product Knowledge (20%)
   - Product sense and intuition
   - Market awareness
   - Metrics and analytics understanding
   - Technical feasibility assessment

4. Motivation (15%)
   - Product passion and curiosity
   - User empathy
   - Drive to ship products

5. Culture Fit (15%)
   - Cross-functional leadership
   - Influence without authority
   - Handling conflict and ambiguity
"""
        },
        'design': {
            'weights': {
                'communication': 0.20,
                'problem_solving': 0.25,  # Design thinking
                'domain_knowledge': 0.25,  # Design skills
                'motivation': 0.15,
                'culture_fit': 0.15
            },
            'rubric': """
SCORING RUBRIC FOR DESIGN ROLES:

1. Communication (20%)
   - Presenting design decisions
   - Receiving and giving feedback
   - Explaining design rationale

2. Problem Solving (25%) - Design Thinking
   - User research interpretation
   - Iterative design process
   - Balancing user needs with business goals

3. Design Knowledge (25%)
   - Design principles and patterns
   - Accessibility awareness
   - Design tool proficiency
   - Visual design fundamentals

4. Motivation (15%)
   - Design passion and curiosity
   - User empathy
   - Following design trends

5. Culture Fit (15%)
   - Collaboration with engineers and PMs
   - Handling design critiques
   - Stakeholder management
"""
        },
        'finance': {
            'weights': {
                'communication': 0.20,
                'problem_solving': 0.20,
                'domain_knowledge': 0.35,  # CRITICAL for finance - technical knowledge
                'motivation': 0.15,
                'culture_fit': 0.10
            },
            'rubric': """
SCORING RUBRIC FOR FINANCE/IB ROLES:

1. Communication (20%)
   - Professional communication
   - Presenting financial analysis
   - Client-facing skills

2. Problem Solving (20%)
   - Analytical reasoning
   - Quantitative problem-solving
   - Deal structuring logic

3. Technical Knowledge (35%) - CRITICAL FOR FINANCE
   - Valuation methodologies (DCF, Comps, Precedents)
   - Financial statement analysis
   - Accounting fundamentals
   - M&A concepts
   - Capital markets understanding
   - Excel/modeling proficiency

4. Motivation (15%) - Very Important for IB
   - Understanding of IB lifestyle
   - Deal passion and market interest
   - Long-term career goals
   - Why IB specifically

5. Culture Fit (10%)
   - Team player mentality
   - Handling high-pressure situations
   - Attention to detail
"""
        }
    }

    # Default weights for backwards compatibility
    SCORING_WEIGHTS = {
        'communication': 0.20,
        'problem_solving': 0.20,
        'domain_knowledge': 0.25,
        'motivation': 0.15,
        'culture_fit': 0.20
    }

    SYSTEM_PROMPT_BASE = """You are an expert interviewer evaluating college student responses.
Analyze the transcript and provide scores and feedback.

Be objective, fair, and focus only on job-relevant factors.
Evaluate potential and trajectory, not just current skills.
Do NOT penalize for accent, appearance, or background.
Always respond in valid JSON format."""

    # Alias for backwards compatibility - many methods reference SYSTEM_PROMPT
    @property
    def SYSTEM_PROMPT(self) -> str:
        """Alias for SYSTEM_PROMPT_BASE for backwards compatibility."""
        return self.SYSTEM_PROMPT_BASE

    def __init__(self):
        # Claude API (exclusive - all AI uses Claude Sonnet 4.5)
        self.anthropic_api_key = settings.anthropic_api_key
        self.claude_model = settings.claude_model
        self.anthropic_base_url = "https://api.anthropic.com/v1"

        if not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set - AI features will not work")

    async def _call_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> dict:
        """Call Claude API for fast, accurate AI processing."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.anthropic_base_url}/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.claude_model,
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()
            content = result["content"][0]["text"]

            # Extract JSON from response (Claude may include markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return {"parsed": json.loads(content.strip())}

    async def _call_llm(self, messages: list[dict], temperature: float = 0.3) -> dict:
        """Call Claude API for all AI processing."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured - cannot process AI request")

        # Extract system and user messages
        system_prompt = ""
        user_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                user_prompt = msg["content"]

        result = await self._call_claude(system_prompt, user_prompt)
        # Convert to standard format for compatibility
        return {
            "choices": [{
                "message": {
                    "content": json.dumps(result["parsed"])
                }
            }]
        }

    def _get_vertical_config(self, vertical: Optional[str]) -> tuple[dict, str]:
        """Get the scoring weights and rubric for a vertical."""
        # Map legacy verticals to new ones
        vertical_map = {
            'engineering': 'software_engineering',
            'business': 'product',
        }
        normalized_vertical = vertical_map.get(vertical, vertical) if vertical else None

        if normalized_vertical and normalized_vertical in self.VERTICAL_SCORING_CONFIG:
            config = self.VERTICAL_SCORING_CONFIG[normalized_vertical]
            return config['weights'], config['rubric']

        # Default fallback
        return self.SCORING_WEIGHTS, ""

    async def analyze_response(
        self,
        question: str,
        transcript: str,
        job_title: str,
        job_requirements: list[str],
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        language: str = "en"
    ) -> ScoreResult:
        """
        Analyze a single interview response with vertical-specific scoring.

        Args:
            question: The interview question
            transcript: Transcribed response from candidate
            job_title: Title of the job
            job_requirements: List of job requirements
            vertical: Industry vertical (software_engineering, data, product, design, finance)
            role_type: Specific role type
            language: Response language ("zh" for Chinese, "en" for English)

        Returns:
            ScoreResult with detailed scoring and version tracking
        """
        # Get vertical-specific weights and rubric
        weights, rubric = self._get_vertical_config(vertical)

        requirements_text = "\n".join(f"- {req}" for req in job_requirements) if job_requirements else "No specific requirements provided"

        # Build vertical-specific system prompt
        system_prompt = self.SYSTEM_PROMPT_BASE
        if rubric:
            system_prompt += f"\n\n{rubric}"

        user_prompt = f"""JOB: {job_title}
VERTICAL: {vertical or 'General'}
ROLE TYPE: {role_type or 'General'}

JOB REQUIREMENTS:
{requirements_text}

INTERVIEW QUESTION: {question}

CANDIDATE'S RESPONSE (transcript):
{transcript}

Evaluate this candidate response using the rubric for {vertical or 'general'} roles.
Score each dimension 0-100, applying the vertical-specific criteria.

Respond in JSON format:
{{
    "scores": {{
        "communication": <0-100>,
        "problem_solving": <0-100>,
        "domain_knowledge": <0-100>,
        "motivation": <0-100>,
        "culture_fit": <0-100>
    }},
    "overall_score": <0-100 weighted average>,
    "analysis": "<2-3 sentence analysis in {'Chinese' if language == 'zh' else 'English'}>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "concerns": ["<concern 1>", "<concern 2>"],
    "highlight_quotes": ["<notable quote from transcript>"]
}}"""

        result = await self._call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        try:
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            scores = parsed["scores"]

            # Calculate weighted overall score using vertical-specific weights
            overall = sum(
                (scores[dim] / 10) * weight
                for dim, weight in weights.items()
            )

            logger.info(f"Scored response for {vertical}/{role_type}: overall={overall:.2f}, "
                       f"version={SCORING_ALGORITHM_VERSION}")

            return ScoreResult(
                communication=scores["communication"] / 10,  # Convert to 0-10 scale
                problem_solving=scores["problem_solving"] / 10,
                domain_knowledge=scores["domain_knowledge"] / 10,
                motivation=scores["motivation"] / 10,
                culture_fit=scores["culture_fit"] / 10,
                overall=round(overall, 2),
                analysis=parsed["analysis"],
                strengths=parsed.get("strengths", []),
                concerns=parsed.get("concerns", []),
                highlight_quotes=parsed.get("highlight_quotes", []),
                raw_response=parsed,
                algorithm_version=SCORING_ALGORITHM_VERSION,
                vertical=vertical,
                raw_score_before_normalization=round(overall, 2)
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse AI response: {e}")

    async def generate_summary(
        self,
        responses: list[dict],
        job_title: str,
        job_requirements: list[str],
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        language: str = "en"
    ) -> InterviewSummary:
        """
        Generate an overall interview summary.

        Args:
            responses: List of response data with questions, transcripts, and scores
            job_title: Title of the job
            job_requirements: List of job requirements
            vertical: Industry vertical
            role_type: Specific role type
            language: Response language

        Returns:
            InterviewSummary with overall assessment
        """
        responses_text = ""
        for i, resp in enumerate(responses, 1):
            transcript_preview = resp.get('transcript', '')[:500]
            score = resp.get('score', 'N/A')
            responses_text += f"""
Question {i}: {resp.get('question', 'Unknown')}
Response: {transcript_preview}{'...' if len(resp.get('transcript', '')) > 500 else ''}
Score: {score}
---"""

        requirements_text = "\n".join(f"- {req}" for req in job_requirements) if job_requirements else "No specific requirements"

        user_prompt = f"""Provide an overall assessment of this interview:

JOB: {job_title}
VERTICAL: {vertical or 'General'}
ROLE TYPE: {role_type or 'General'}

JOB REQUIREMENTS:
{requirements_text}

INTERVIEW RESPONSES:
{responses_text}

Generate a comprehensive summary in JSON format:
{{
    "total_score": <0-100>,
    "summary": "<3-4 sentence overall assessment in {'Chinese' if language == 'zh' else 'English'}>",
    "overall_strengths": ["<key strength 1>", "<key strength 2>", "<key strength 3>"],
    "overall_concerns": ["<concern 1>", "<concern 2>"],
    "recommendation": "<one of: advance, maybe, reject>"
}}

Recommendation guide:
- advance: Good candidate, recommend proceeding to next round
- maybe: Mixed performance, needs further evaluation
- reject: Not a good fit for this role"""

        result = await self._call_llm([
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])

        try:
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            return InterviewSummary(
                total_score=parsed["total_score"] / 10,  # Convert to 0-10 scale
                summary=parsed["summary"],
                overall_strengths=parsed.get("overall_strengths", []),
                overall_concerns=parsed.get("overall_concerns", []),
                recommendation=parsed["recommendation"],
                raw_response=parsed
            )
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse AI summary response: {e}")

    def calculate_overall_score(self, responses: list[ScoreResult]) -> float:
        """
        Calculate the overall interview score from individual responses.

        Args:
            responses: List of ScoreResult objects

        Returns:
            Overall weighted score (0-10 scale)
        """
        if not responses:
            return 0.0

        total = sum(r.overall for r in responses)
        return round(total / len(responses), 2)

    async def get_immediate_feedback(
        self,
        question: str,
        transcript: str,
        job_title: str = "General",
        job_requirements: list[str] = None,
        language: str = "en"
    ) -> dict:
        """
        Get immediate feedback for practice mode (synchronous scoring).

        Returns score + improvement tips + optional sample answer.
        """
        if job_requirements is None:
            job_requirements = []

        requirements_text = "\n".join(f"- {req}" for req in job_requirements) if job_requirements else "General interview preparation"

        user_prompt = f"""JOB: {job_title}

JOB REQUIREMENTS:
{requirements_text}

INTERVIEW QUESTION: {question}

CANDIDATE'S RESPONSE (transcript):
{transcript}

Evaluate this practice response and provide detailed feedback.

Respond in JSON format:
{{
    "scores": {{
        "communication": <0-100>,
        "problem_solving": <0-100>,
        "domain_knowledge": <0-100>,
        "motivation": <0-100>,
        "culture_fit": <0-100>
    }},
    "overall_score": <0-100>,
    "analysis": "<2-3 sentence analysis in {'Chinese' if language == 'zh' else 'English'}>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "concerns": ["<area to improve 1>", "<area to improve 2>"],
    "tips": [
        "<specific actionable tip 1>",
        "<specific actionable tip 2>",
        "<specific actionable tip 3>"
    ],
    "sample_answer": "<A brief example of a strong answer to this question (2-3 sentences, in {'Chinese' if language == 'zh' else 'English'})>"
}}"""

        result = await self._call_llm([
            {"role": "system", "content": self.SYSTEM_PROMPT + "\n\nFor practice mode, also provide actionable improvement tips and a brief sample answer."},
            {"role": "user", "content": user_prompt}
        ])

        try:
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            scores = parsed["scores"]

            # Calculate weighted overall score (convert from 0-100 to 0-10 scale)
            overall = sum(
                (scores[dim] / 10) * weight
                for dim, weight in self.SCORING_WEIGHTS.items()
            )

            return {
                "score_result": ScoreResult(
                    communication=scores["communication"] / 10,
                    problem_solving=scores["problem_solving"] / 10,
                    domain_knowledge=scores["domain_knowledge"] / 10,
                    motivation=scores["motivation"] / 10,
                    culture_fit=scores["culture_fit"] / 10,
                    overall=round(overall, 2),
                    analysis=parsed["analysis"],
                    strengths=parsed.get("strengths", []),
                    concerns=parsed.get("concerns", []),
                    highlight_quotes=[],
                    raw_response=parsed
                ),
                "tips": parsed.get("tips", []),
                "sample_answer": parsed.get("sample_answer")
            }
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse AI feedback response: {e}")


    async def analyze_and_generate_followups(
        self,
        question: str,
        transcript: str,
        job_title: str,
        job_requirements: list[str],
        language: str = "en"
    ) -> tuple[ScoreResult, list[str]]:
        """
        Analyze a response AND generate follow-up questions.
        Used for real (non-practice) interviews to enable conversational follow-ups.

        Returns:
            Tuple of (ScoreResult, list of follow-up questions)
        """
        if job_requirements is None:
            job_requirements = []

        requirements_text = "\n".join(f"- {req}" for req in job_requirements) if job_requirements else "General position"

        user_prompt = f"""JOB: {job_title}

JOB REQUIREMENTS:
{requirements_text}

INTERVIEW QUESTION: {question}

CANDIDATE'S RESPONSE (transcript):
{transcript}

Analyze this response and generate follow-up questions to probe deeper.

Follow-up questions should:
1. Clarify vague or incomplete parts of the answer
2. Ask for specific examples if the candidate spoke generally
3. Explore technical depth if the answer was surface-level
4. NOT be repetitive of the original question
5. Be natural and conversational

Generate 1-2 follow-up questions only if they add value.
If the answer was comprehensive and clear, generate 0 follow-up questions.

Respond in JSON format:
{{
    "scores": {{
        "communication": <0-100>,
        "problem_solving": <0-100>,
        "domain_knowledge": <0-100>,
        "motivation": <0-100>,
        "culture_fit": <0-100>
    }},
    "overall_score": <0-100>,
    "analysis": "<2-3 sentence analysis in {'Chinese' if language == 'zh' else 'English'}>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "concerns": ["<concern 1>", "<concern 2>"],
    "highlight_quotes": ["<notable quote>"],
    "followup_questions": [
        "<follow-up question 1 in {'Chinese' if language == 'zh' else 'English'}>",
        "<follow-up question 2 if needed>"
    ]
}}

Note: followup_questions array can be empty if the response was complete."""

        result = await self._call_llm([
            {"role": "system", "content": self.SYSTEM_PROMPT + "\n\nYou are also responsible for generating intelligent follow-up questions to create a conversational interview experience."},
            {"role": "user", "content": user_prompt}
        ])

        try:
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            scores = parsed["scores"]

            # Calculate weighted overall score
            overall = sum(
                (scores[dim] / 10) * weight
                for dim, weight in self.SCORING_WEIGHTS.items()
            )

            score_result = ScoreResult(
                communication=scores["communication"] / 10,
                problem_solving=scores["problem_solving"] / 10,
                domain_knowledge=scores["domain_knowledge"] / 10,
                motivation=scores["motivation"] / 10,
                culture_fit=scores["culture_fit"] / 10,
                overall=round(overall, 2),
                analysis=parsed["analysis"],
                strengths=parsed.get("strengths", []),
                concerns=parsed.get("concerns", []),
                highlight_quotes=parsed.get("highlight_quotes", []),
                raw_response=parsed
            )

            followup_questions = parsed.get("followup_questions", [])
            # Limit to 2 follow-up questions max
            followup_questions = followup_questions[:2]

            return score_result, followup_questions

        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse AI response: {e}")


    # ==================== CODING CHALLENGE SCORING ====================

    CODING_SYSTEM_PROMPT = """You are an expert programming interviewer evaluating Python code solutions.
Analyze the code quality and provide scores and feedback.

SCORING RUBRIC (0-100 for each dimension):

1. Correctness
   - Does the code pass all test cases?
   - Handle edge cases properly?
   - Produce correct output?

2. Code Quality
   - Readable and well-structured
   - Good variable/function naming
   - Appropriate comments (not excessive)
   - Follows Python conventions (PEP 8)

3. Efficiency
   - Time complexity (Big O)
   - Space complexity
   - Avoids unnecessary operations

4. Problem Understanding
   - Correct interpretation of the problem
   - Appropriate approach selection
   - Handles requirements correctly

Be objective and fair. Focus on code quality, not personal style preferences.
Always respond in valid JSON format."""

    async def score_coding_response(
        self,
        problem_description: str,
        code: str,
        test_results: list[dict],
        language: str = "en"
    ) -> ScoreResult:
        """
        Score a coding response based on test results + code quality.

        Args:
            problem_description: The coding problem description
            code: The submitted Python code
            test_results: List of test result dicts with keys: name, passed, actual, expected
            language: Response language ("zh" for Chinese, "en" for English)

        Returns:
            ScoreResult with coding-specific scoring mapped to standard dimensions
        """
        # Calculate correctness from test results
        visible_tests = [t for t in test_results if not t.get("hidden", False)]
        all_tests = test_results
        passed = sum(1 for t in all_tests if t.get("passed", False))
        total = len(all_tests)
        correctness_pct = (passed / total * 100) if total > 0 else 0

        # Build test results summary for prompt
        test_summary = f"{passed}/{total} tests passed ({correctness_pct:.0f}%)"
        visible_results = []
        for t in visible_tests[:5]:  # Limit to first 5 visible tests
            status = "✓" if t.get("passed") else "✗"
            visible_results.append(
                f"  {status} {t.get('name', 'Test')}: expected={t.get('expected', '?')}, got={t.get('actual', '?')}"
            )

        lang_instruction = "Chinese" if language == "zh" else "English"

        user_prompt = f"""PROBLEM DESCRIPTION:
{problem_description}

SUBMITTED CODE:
```python
{code}
```

TEST RESULTS: {test_summary}
{chr(10).join(visible_results)}

Evaluate this Python solution. Consider:
1. The correctness is already measured: {correctness_pct:.0f}% of tests pass
2. Analyze code quality, efficiency, and problem understanding

Respond in JSON format:
{{
    "scores": {{
        "correctness": {correctness_pct:.0f},
        "code_quality": <0-100>,
        "efficiency": <0-100>,
        "problem_understanding": <0-100>
    }},
    "overall_score": <0-100 weighted average>,
    "analysis": "<2-3 sentence analysis in {lang_instruction}>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "concerns": ["<area to improve 1>", "<area to improve 2>"],
    "time_complexity": "<e.g., O(n), O(n^2), O(n log n)>",
    "space_complexity": "<e.g., O(1), O(n)>"
}}"""

        result = await self._call_llm([
            {"role": "system", "content": self.CODING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])

        try:
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            scores = parsed["scores"]

            # Map coding scores to standard 5-dimension model:
            # - correctness → problem_solving
            # - code_quality → communication (code is communication)
            # - efficiency → domain_knowledge (algorithmic knowledge)
            # - problem_understanding → motivation (engagement with the problem)
            # - culture_fit = neutral default for coding

            # Calculate weighted overall (coding-specific weights)
            coding_weights = {
                'correctness': 0.40,
                'code_quality': 0.20,
                'efficiency': 0.25,
                'problem_understanding': 0.15
            }

            overall = sum(
                (scores[dim] / 10) * weight
                for dim, weight in coding_weights.items()
            )

            return ScoreResult(
                # Map to standard dimensions
                problem_solving=scores["correctness"] / 10,  # 0-10 scale
                communication=scores["code_quality"] / 10,
                domain_knowledge=scores["efficiency"] / 10,
                motivation=scores["problem_understanding"] / 10,
                culture_fit=7.0,  # Neutral default for coding challenges
                overall=round(overall, 2),
                analysis=parsed["analysis"],
                strengths=parsed.get("strengths", []),
                concerns=parsed.get("concerns", []),
                highlight_quotes=[
                    f"Time: {parsed.get('time_complexity', 'N/A')}",
                    f"Space: {parsed.get('space_complexity', 'N/A')}"
                ],
                raw_response=parsed
            )
        except (KeyError, json.JSONDecodeError) as e:
            # Fallback scoring based on test results alone
            base_score = correctness_pct / 10  # Convert to 0-10
            return ScoreResult(
                problem_solving=base_score,
                communication=5.0,  # Neutral
                domain_knowledge=5.0,
                motivation=5.0,
                culture_fit=7.0,
                overall=base_score,
                analysis=f"Code passed {passed}/{total} test cases ({correctness_pct:.0f}%).",
                strengths=[],
                concerns=[f"Scoring parse error: {e}"],
                highlight_quotes=[],
                raw_response=None
            )

    async def get_coding_immediate_feedback(
        self,
        problem_description: str,
        code: str,
        test_results: list[dict],
        language: str = "en"
    ) -> dict:
        """
        Get immediate feedback for practice mode coding submissions.

        Returns score + improvement tips + suggested approach.
        """
        passed = sum(1 for t in test_results if t.get("passed", False))
        total = len(test_results)
        correctness_pct = (passed / total * 100) if total > 0 else 0

        lang_instruction = "Chinese" if language == "zh" else "English"

        user_prompt = f"""PROBLEM DESCRIPTION:
{problem_description}

SUBMITTED CODE:
```python
{code}
```

TEST RESULTS: {passed}/{total} tests passed ({correctness_pct:.0f}%)

Provide detailed feedback for this practice submission.

Respond in JSON format:
{{
    "scores": {{
        "correctness": {correctness_pct:.0f},
        "code_quality": <0-100>,
        "efficiency": <0-100>,
        "problem_understanding": <0-100>
    }},
    "overall_score": <0-100>,
    "analysis": "<2-3 sentence analysis in {lang_instruction}>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "concerns": ["<area to improve 1>", "<area to improve 2>"],
    "tips": [
        "<specific actionable tip 1 in {lang_instruction}>",
        "<specific actionable tip 2 in {lang_instruction}>",
        "<specific actionable tip 3 in {lang_instruction}>"
    ],
    "suggested_approach": "<Brief description of an optimal approach in {lang_instruction}>",
    "time_complexity": "<current solution's complexity>",
    "optimal_complexity": "<optimal solution's complexity>"
}}"""

        result = await self._call_llm([
            {"role": "system", "content": self.CODING_SYSTEM_PROMPT + f"\n\nFor practice mode, also provide actionable improvement tips and suggest an optimal approach. Respond in {lang_instruction}."},
            {"role": "user", "content": user_prompt}
        ])

        try:
            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            scores = parsed["scores"]

            # Calculate weighted overall
            coding_weights = {
                'correctness': 0.40,
                'code_quality': 0.20,
                'efficiency': 0.25,
                'problem_understanding': 0.15
            }

            overall = sum(
                (scores[dim] / 10) * weight
                for dim, weight in coding_weights.items()
            )

            score_result = ScoreResult(
                problem_solving=scores["correctness"] / 10,
                communication=scores["code_quality"] / 10,
                domain_knowledge=scores["efficiency"] / 10,
                motivation=scores["problem_understanding"] / 10,
                culture_fit=7.0,
                overall=round(overall, 2),
                analysis=parsed["analysis"],
                strengths=parsed.get("strengths", []),
                concerns=parsed.get("concerns", []),
                highlight_quotes=[
                    f"Time: {parsed.get('time_complexity', 'N/A')}",
                    f"Optimal: {parsed.get('optimal_complexity', 'N/A')}"
                ],
                raw_response=parsed
            )

            return {
                "score_result": score_result,
                "tips": parsed.get("tips", []),
                "suggested_approach": parsed.get("suggested_approach"),
                "time_complexity": parsed.get("time_complexity"),
                "optimal_complexity": parsed.get("optimal_complexity")
            }
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse AI coding feedback response: {e}")


    # ==================== PROFILE SCORING (Resume/GitHub) ====================

    async def score_profile(
        self,
        resume_data: Optional[dict] = None,
        github_data: Optional[dict] = None,
        education_data: Optional[dict] = None,
        vertical: Optional[str] = None,
    ) -> dict:
        """
        Score a candidate's profile based on resume, GitHub, and education data.
        This provides an initial score before they complete an interview.

        Args:
            resume_data: Parsed resume data (skills, experience, etc.)
            github_data: GitHub profile data (repos, languages, contributions)
            education_data: Education info (university, GPA, major, courses)
            vertical: Target vertical for role-specific scoring

        Returns:
            Dict with profile_score and breakdown by category
        """
        if not any([resume_data, github_data, education_data]):
            return {
                "profile_score": None,
                "breakdown": {},
                "completeness": 0,
                "algorithm_version": SCORING_ALGORITHM_VERSION,
            }

        # Build profile summary for AI scoring
        profile_parts = []

        if resume_data:
            skills = resume_data.get("skills", [])
            experience = resume_data.get("experience", [])
            education = resume_data.get("education", [])
            profile_parts.append(f"RESUME DATA:\n- Skills: {', '.join(skills[:15])}")
            if experience:
                exp_summary = "; ".join([
                    f"{e.get('title', 'Role')} at {e.get('company', 'Company')}"
                    for e in experience[:3]
                ])
                profile_parts.append(f"- Experience: {exp_summary}")
            if education:
                edu_summary = "; ".join([
                    f"{e.get('degree', 'Degree')} from {e.get('school', 'School')}"
                    for e in education[:2]
                ])
                profile_parts.append(f"- Education: {edu_summary}")

        if github_data:
            repos = github_data.get("repos", [])
            languages = github_data.get("languages", {})
            contributions = github_data.get("totalContributions", 0)
            profile_parts.append(f"\nGITHUB DATA:")
            profile_parts.append(f"- Repositories: {len(repos)}")
            profile_parts.append(f"- Languages: {', '.join(list(languages.keys())[:5])}")
            profile_parts.append(f"- Total Contributions: {contributions}")
            if repos:
                top_repos = sorted(repos, key=lambda r: r.get("stars", 0), reverse=True)[:3]
                repo_summary = "; ".join([f"{r.get('name', 'repo')} ({r.get('stars', 0)} stars)" for r in top_repos])
                profile_parts.append(f"- Top Repos: {repo_summary}")

        if education_data:
            profile_parts.append(f"\nEDUCATION:")
            if education_data.get("university"):
                profile_parts.append(f"- University: {education_data['university']}")
            if education_data.get("major"):
                profile_parts.append(f"- Major: {education_data['major']}")
            if education_data.get("gpa"):
                profile_parts.append(f"- GPA: {education_data['gpa']}")
            if education_data.get("graduation_year"):
                profile_parts.append(f"- Graduation Year: {education_data['graduation_year']}")
            if education_data.get("courses"):
                courses = education_data.get("courses", [])
                if isinstance(courses, list):
                    profile_parts.append(f"- Courses: {', '.join(courses[:5])}")

        profile_text = "\n".join(profile_parts)

        # Calculate completeness score (0-100)
        completeness = 0
        if resume_data:
            completeness += 40
            if resume_data.get("skills"):
                completeness += 10
            if resume_data.get("experience"):
                completeness += 10
        if github_data:
            completeness += 25
            if github_data.get("repos"):
                completeness += 5
        if education_data:
            if education_data.get("university"):
                completeness += 5
            if education_data.get("gpa"):
                completeness += 5

        user_prompt = f"""Evaluate this college student's profile for {vertical or 'general'} roles.

{profile_text}

Score this profile on a 0-10 scale across these dimensions.
Consider this is for entry-level/intern positions - weight potential over experience.

Respond in JSON format:
{{
    "scores": {{
        "technical_skills": <0-10, based on relevant skills and projects>,
        "experience_quality": <0-10, internships, projects, contributions>,
        "education": <0-10, school, GPA, relevant coursework>,
        "github_activity": <0-10, repos, contributions, code quality signals>,
        "overall_potential": <0-10, overall assessment>
    }},
    "profile_score": <0-10, weighted average>,
    "strengths": ["<strength 1>", "<strength 2>"],
    "gaps": ["<missing element 1>", "<area to improve>"],
    "summary": "<1-2 sentence assessment>"
}}"""

        try:
            result = await self._call_llm([
                {"role": "system", "content": "You are an expert recruiter evaluating college student profiles for entry-level tech positions. Score fairly based on potential, not just current experience. Respond in JSON."},
                {"role": "user", "content": user_prompt}
            ])

            content = result["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            return {
                "profile_score": parsed.get("profile_score", 5.0),
                "breakdown": parsed.get("scores", {}),
                "strengths": parsed.get("strengths", []),
                "gaps": parsed.get("gaps", []),
                "summary": parsed.get("summary", ""),
                "completeness": completeness,
                "algorithm_version": SCORING_ALGORITHM_VERSION,
            }

        except Exception as e:
            logger.error(f"Profile scoring error: {e}")
            # Return basic heuristic score
            base_score = 5.0
            if resume_data and resume_data.get("skills"):
                base_score += min(len(resume_data["skills"]) / 10, 1.5)
            if github_data and github_data.get("repos"):
                base_score += min(len(github_data["repos"]) / 5, 1.0)
            if education_data and education_data.get("gpa"):
                gpa = education_data.get("gpa", 3.0)
                base_score += (gpa - 3.0) * 0.5

            return {
                "profile_score": min(round(base_score, 2), 10.0),
                "breakdown": {
                    "technical_skills": 5.0,
                    "experience_quality": 5.0,
                    "education": 5.0,
                    "github_activity": 5.0,
                    "overall_potential": base_score,
                },
                "strengths": [],
                "gaps": [],
                "summary": "Profile score based on available data.",
                "completeness": completeness,
                "algorithm_version": SCORING_ALGORITHM_VERSION,
            }


    # ==========================================
    # MULTI-RATER SIMULATION
    # ==========================================

    # Different interviewer personas for multi-rater simulation
    INTERVIEWER_PERSONAS = {
        "technical": {
            "name": "Technical Interviewer",
            "focus": "technical depth, problem-solving approach, coding ability",
            "weight_adjustments": {
                "domain_knowledge": 0.10,
                "problem_solving": 0.05,
                "communication": -0.05,
                "motivation": -0.05,
                "culture_fit": -0.05,
            },
            "system_prompt": """You are a senior technical interviewer (Staff Engineer level).
You focus heavily on technical accuracy, problem-solving methodology, and depth of understanding.
You care less about polish and more about substance.
Be critical of hand-waving or surface-level answers.""",
        },
        "hiring_manager": {
            "name": "Hiring Manager",
            "focus": "communication, team fit, potential for growth",
            "weight_adjustments": {
                "communication": 0.10,
                "culture_fit": 0.05,
                "motivation": 0.05,
                "domain_knowledge": -0.10,
                "problem_solving": -0.10,
            },
            "system_prompt": """You are a hiring manager evaluating candidate fit.
You focus on communication clarity, cultural alignment, and growth potential.
Technical depth is less important than demonstrating learning ability and collaboration.""",
        },
        "peer": {
            "name": "Peer Engineer",
            "focus": "collaboration potential, practical skills, day-to-day fit",
            "weight_adjustments": {
                "culture_fit": 0.05,
                "communication": 0.05,
                "problem_solving": 0.00,
                "domain_knowledge": -0.05,
                "motivation": -0.05,
            },
            "system_prompt": """You are a peer engineer who would work alongside this candidate.
You focus on whether they'd be a good collaborator and teammate.
You value practical skills and the ability to communicate and work together.""",
        },
    }

    async def analyze_response_multi_rater(
        self,
        question: str,
        transcript: str,
        job_title: str,
        job_requirements: list[str],
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        language: str = "en"
    ) -> dict:
        """
        Analyze a response using multiple AI interviewer personas.

        Returns:
            - consensus_score: Weighted average across raters
            - score_variance: How much raters disagreed
            - individual_scores: Each rater's assessment
            - confidence: Overall confidence (inverse of variance)
            - needs_human_review: True if high disagreement
        """
        import asyncio

        # Run all three personas in parallel
        tasks = [
            self._score_as_persona(
                persona_name, persona_config,
                question, transcript, job_title, job_requirements,
                vertical, role_type, language
            )
            for persona_name, persona_config in self.INTERVIEWER_PERSONAS.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        valid_results = []
        for persona_name, result in zip(self.INTERVIEWER_PERSONAS.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Persona {persona_name} failed: {result}")
                continue
            valid_results.append({"persona": persona_name, "result": result})

        if not valid_results:
            # Fallback to single scoring
            single_result = await self.analyze_response(
                question, transcript, job_title, job_requirements,
                vertical, role_type, language
            )
            return {
                "consensus_score": single_result.overall,
                "score_variance": 0,
                "individual_scores": [{"persona": "default", "overall": single_result.overall}],
                "confidence": 0.5,
                "needs_human_review": False,
                "primary_result": single_result,
            }

        # Calculate consensus
        overall_scores = [r["result"].overall for r in valid_results]
        consensus_score = sum(overall_scores) / len(overall_scores)

        # Calculate variance
        variance = sum((s - consensus_score) ** 2 for s in overall_scores) / len(overall_scores)
        std_dev = variance ** 0.5

        # Confidence inversely proportional to variance
        # Low variance = high confidence
        confidence = max(0.3, 1.0 - (std_dev / 20))  # Normalize: std_dev of 20 = 0.3 confidence

        # Need human review if high disagreement
        needs_human_review = std_dev > 15 or any(
            abs(s - consensus_score) > 20 for s in overall_scores
        )

        # Get the most complete result as primary
        primary_result = valid_results[0]["result"]

        return {
            "consensus_score": round(consensus_score, 1),
            "score_variance": round(variance, 2),
            "score_std_dev": round(std_dev, 2),
            "individual_scores": [
                {
                    "persona": r["persona"],
                    "overall": r["result"].overall,
                    "communication": r["result"].communication,
                    "problem_solving": r["result"].problem_solving,
                    "domain_knowledge": r["result"].domain_knowledge,
                    "analysis": r["result"].analysis[:200],  # Truncate
                }
                for r in valid_results
            ],
            "confidence": round(confidence, 2),
            "needs_human_review": needs_human_review,
            "primary_result": primary_result,
            "algorithm_version": SCORING_ALGORITHM_VERSION + "-multi",
        }

    async def _score_as_persona(
        self,
        persona_name: str,
        persona_config: dict,
        question: str,
        transcript: str,
        job_title: str,
        job_requirements: list[str],
        vertical: Optional[str],
        role_type: Optional[str],
        language: str
    ) -> ScoreResult:
        """Score a response as a specific interviewer persona."""
        # Get base config
        base_weights, rubric = self._get_vertical_config(vertical)

        # Apply persona weight adjustments
        adjusted_weights = base_weights.copy()
        for dim, adjustment in persona_config["weight_adjustments"].items():
            if dim in adjusted_weights:
                adjusted_weights[dim] = max(0.05, adjusted_weights[dim] + adjustment)

        # Normalize weights to sum to 1
        total_weight = sum(adjusted_weights.values())
        adjusted_weights = {k: v / total_weight for k, v in adjusted_weights.items()}

        requirements_text = "\n".join(f"- {req}" for req in job_requirements) if job_requirements else "No specific requirements"

        system_prompt = persona_config["system_prompt"] + f"\n\n{rubric}" if rubric else persona_config["system_prompt"]

        user_prompt = f"""You are evaluating from the perspective of: {persona_config['name']}
Your focus areas: {persona_config['focus']}

JOB: {job_title}
VERTICAL: {vertical or 'General'}

REQUIREMENTS:
{requirements_text}

QUESTION: {question}

RESPONSE:
{transcript}

Score this response. Focus on your perspective's priorities.
Respond in JSON:
{{
    "scores": {{
        "communication": <0-100>,
        "problem_solving": <0-100>,
        "domain_knowledge": <0-100>,
        "motivation": <0-100>,
        "culture_fit": <0-100>
    }},
    "overall_score": <0-100 weighted by your focus>,
    "analysis": "<2 sentence analysis from your perspective>",
    "strengths": ["<strength>"],
    "concerns": ["<concern>"]
}}"""

        result = await self._call_llm([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        scores = parsed.get("scores", {})

        # Calculate weighted overall with persona's adjusted weights
        overall = sum(
            scores.get(dim, 50) * weight
            for dim, weight in adjusted_weights.items()
        )

        return ScoreResult(
            communication=scores.get("communication", 50) / 10,
            problem_solving=scores.get("problem_solving", 50) / 10,
            domain_knowledge=scores.get("domain_knowledge", 50) / 10,
            motivation=scores.get("motivation", 50) / 10,
            culture_fit=scores.get("culture_fit", 50) / 10,
            overall=overall / 10,
            analysis=parsed.get("analysis", ""),
            strengths=parsed.get("strengths", []),
            concerns=parsed.get("concerns", []),
            highlight_quotes=[],
            vertical=vertical,
            algorithm_version=f"{SCORING_ALGORITHM_VERSION}-{persona_name}",
        )

    # ==========================================
    # OUTCOME-BASED CALIBRATION
    # ==========================================

    async def calibrate_score(
        self,
        raw_score: float,
        vertical: str,
        role_type: str,
        calibration_data: Optional[dict] = None
    ) -> dict:
        """
        Calibrate a score based on historical outcomes.

        Args:
            raw_score: The raw AI-generated score (0-10)
            vertical: Industry vertical
            role_type: Specific role
            calibration_data: Historical data mapping scores to outcomes

        Returns:
            calibrated_score: Adjusted score
            hire_probability: Estimated probability of hire at this score
            percentile: Where this score ranks
        """
        # Default calibration curves (would be learned from data)
        # These represent: at score X, Y% of candidates got hired
        DEFAULT_CALIBRATION = {
            # Score ranges and their historical hire rates
            (0, 4): {"hire_rate": 0.05, "percentile_range": (0, 20)},
            (4, 5): {"hire_rate": 0.10, "percentile_range": (20, 35)},
            (5, 6): {"hire_rate": 0.20, "percentile_range": (35, 50)},
            (6, 7): {"hire_rate": 0.35, "percentile_range": (50, 70)},
            (7, 8): {"hire_rate": 0.55, "percentile_range": (70, 85)},
            (8, 9): {"hire_rate": 0.75, "percentile_range": (85, 95)},
            (9, 10): {"hire_rate": 0.90, "percentile_range": (95, 100)},
        }

        calibration = calibration_data or DEFAULT_CALIBRATION

        # Find the matching range
        hire_rate = 0.5
        percentile = 50

        for (low, high), data in calibration.items():
            if low <= raw_score < high:
                hire_rate = data["hire_rate"]
                pct_low, pct_high = data["percentile_range"]
                # Interpolate within range
                ratio = (raw_score - low) / (high - low)
                percentile = pct_low + ratio * (pct_high - pct_low)
                break

        # Calibrated score (slight adjustment based on hire rate)
        # If hire rate is low for this score, adjust down slightly
        calibration_factor = 0.9 + (hire_rate * 0.2)  # Range: 0.9 to 1.1
        calibrated_score = raw_score * calibration_factor

        return {
            "raw_score": raw_score,
            "calibrated_score": round(min(10, calibrated_score), 2),
            "calibration_factor": round(calibration_factor, 3),
            "hire_probability": round(hire_rate, 2),
            "percentile": round(percentile, 1),
            "vertical": vertical,
            "role_type": role_type,
            "interpretation": self._get_score_interpretation(calibrated_score, hire_rate),
        }

    def _get_score_interpretation(self, score: float, hire_rate: float) -> str:
        """Get human-readable interpretation of calibrated score."""
        if score >= 8.5 and hire_rate >= 0.7:
            return "Exceptional candidate - strong hire recommendation"
        elif score >= 7.5 and hire_rate >= 0.5:
            return "Strong candidate - likely to receive offers"
        elif score >= 6.5 and hire_rate >= 0.3:
            return "Good candidate - competitive for entry-level roles"
        elif score >= 5.5 and hire_rate >= 0.15:
            return "Average candidate - may need more preparation"
        else:
            return "Below average - significant improvement needed"

    # ==========================================
    # BEHAVIORAL SIGNAL EXTRACTION
    # ==========================================

    def extract_behavioral_signals(self, transcript: str, duration_seconds: int = 0) -> dict:
        """
        Extract behavioral signals from transcript.
        These can be used as additional features for scoring.
        """
        import re

        words = transcript.split()
        word_count = len(words)

        # Filler words
        filler_words = ["um", "uh", "like", "you know", "basically", "actually", "literally", "honestly"]
        filler_count = sum(
            len(re.findall(rf'\b{fw}\b', transcript.lower()))
            for fw in filler_words
        )
        filler_ratio = filler_count / max(word_count, 1)

        # Speaking rate (if duration available)
        speaking_rate = (word_count / (duration_seconds / 60)) if duration_seconds > 0 else None

        # Hedging phrases (low confidence indicators)
        hedging_phrases = ["i think", "maybe", "probably", "i guess", "kind of", "sort of", "not sure"]
        hedging_count = sum(
            len(re.findall(pattern, transcript.lower()))
            for pattern in hedging_phrases
        )

        # Confidence indicators
        confidence_phrases = ["definitely", "absolutely", "clearly", "i know", "in my experience", "i've done"]
        confidence_count = sum(
            len(re.findall(pattern, transcript.lower()))
            for pattern in confidence_phrases
        )

        # STAR format detection
        has_situation = any(kw in transcript.lower() for kw in ["situation", "context", "background", "when i was"])
        has_task = any(kw in transcript.lower() for kw in ["task", "goal", "objective", "my role was"])
        has_action = any(kw in transcript.lower() for kw in ["i did", "i took", "i decided", "i implemented"])
        has_result = any(kw in transcript.lower() for kw in ["result", "outcome", "impact", "led to", "achieved"])
        star_completeness = sum([has_situation, has_task, has_action, has_result]) / 4

        # Specificity (numbers, proper nouns, technical terms)
        numbers = len(re.findall(r'\b\d+\b', transcript))
        has_quantified_results = numbers > 0

        return {
            "word_count": word_count,
            "filler_word_count": filler_count,
            "filler_ratio": round(filler_ratio, 3),
            "speaking_rate_wpm": round(speaking_rate, 1) if speaking_rate else None,
            "hedging_count": hedging_count,
            "confidence_count": confidence_count,
            "confidence_ratio": round(confidence_count / max(hedging_count, 1), 2),
            "star_format": {
                "has_situation": has_situation,
                "has_task": has_task,
                "has_action": has_action,
                "has_result": has_result,
                "completeness": round(star_completeness, 2),
            },
            "has_quantified_results": has_quantified_results,
            "numbers_mentioned": numbers,
            "signals_quality": self._assess_signal_quality(
                filler_ratio, star_completeness, confidence_count, hedging_count
            ),
        }

    def _assess_signal_quality(
        self,
        filler_ratio: float,
        star_completeness: float,
        confidence_count: int,
        hedging_count: int
    ) -> str:
        """Assess overall quality of behavioral signals."""
        quality_score = 0

        # Low filler ratio is good
        if filler_ratio < 0.02:
            quality_score += 2
        elif filler_ratio < 0.05:
            quality_score += 1
        elif filler_ratio > 0.10:
            quality_score -= 1

        # STAR format is good
        if star_completeness >= 0.75:
            quality_score += 2
        elif star_completeness >= 0.50:
            quality_score += 1

        # More confidence than hedging is good
        if confidence_count > hedging_count:
            quality_score += 1
        elif hedging_count > confidence_count * 2:
            quality_score -= 1

        if quality_score >= 4:
            return "excellent"
        elif quality_score >= 2:
            return "good"
        elif quality_score >= 0:
            return "average"
        else:
            return "needs_improvement"


# Global instance
scoring_service = ScoringService()
