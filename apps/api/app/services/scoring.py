import httpx
import json
from typing import Optional
from dataclasses import dataclass
from ..config import settings


@dataclass
class ScoreResult:
    """Result of AI scoring for a single response."""
    communication: float  # 沟通能力
    problem_solving: float  # 解决问题能力
    domain_knowledge: float  # 专业知识
    motivation: float  # 动机
    culture_fit: float  # 文化契合度
    overall: float
    analysis: str
    strengths: list[str]
    concerns: list[str]
    highlight_quotes: list[str]
    raw_response: Optional[dict] = None


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
    """Service for AI-powered interview scoring using DeepSeek."""

    SCORING_WEIGHTS = {
        'communication': 0.20,
        'problem_solving': 0.20,
        'domain_knowledge': 0.25,
        'motivation': 0.15,
        'culture_fit': 0.20
    }

    SYSTEM_PROMPT = """You are an expert HR interviewer evaluating candidate responses.
Analyze the transcript and provide scores and feedback.

SCORING RUBRIC (0-100 for each dimension):

1. Communication (沟通能力)
   - Clarity of expression
   - Structure of response
   - Language fluency (Mandarin/English)
   - Conciseness

2. Problem Solving (解决问题能力)
   - Logical reasoning
   - Analytical thinking
   - Creativity
   - Structured approach

3. Domain Knowledge (专业知识)
   - Technical accuracy
   - Depth of understanding
   - Practical application
   - Industry awareness

4. Motivation (动机)
   - Genuine interest
   - Career alignment
   - Company research
   - Long-term vision

5. Culture Fit (文化契合度)
   - Values alignment
   - Team orientation
   - Adaptability
   - Professionalism

Be objective, fair, and focus only on job-relevant factors.
Do NOT penalize for accent, appearance, or background.
Always respond in valid JSON format."""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url

    async def _call_llm(self, messages: list[dict], temperature: float = 0.3) -> dict:
        """Make a call to DeepSeek API (OpenAI-compatible)."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            return response.json()

    async def analyze_response(
        self,
        question: str,
        transcript: str,
        job_title: str,
        job_requirements: list[str],
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        language: str = "zh"
    ) -> ScoreResult:
        """
        Analyze a single interview response.

        Args:
            question: The interview question
            transcript: Transcribed response from candidate
            job_title: Title of the job
            job_requirements: List of job requirements
            vertical: Industry vertical (new_energy, sales)
            role_type: Specific role type
            language: Response language ("zh" for Chinese, "en" for English)

        Returns:
            ScoreResult with detailed scoring
        """
        requirements_text = "\n".join(f"- {req}" for req in job_requirements) if job_requirements else "No specific requirements provided"

        vertical_context = ""
        if vertical:
            if vertical == "new_energy":
                vertical_context = "This is for the New Energy/EV industry. Evaluate technical depth and industry knowledge accordingly."
            elif vertical == "sales":
                vertical_context = "This is for a Sales/BD role. Focus on persuasion skills, customer handling, and sales methodology."

        user_prompt = f"""JOB: {job_title}
VERTICAL: {vertical or 'General'}
ROLE TYPE: {role_type or 'General'}
{vertical_context}

JOB REQUIREMENTS:
{requirements_text}

INTERVIEW QUESTION: {question}

CANDIDATE'S RESPONSE (transcript):
{transcript}

Evaluate this candidate response. Score each dimension 0-100.

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
            {"role": "system", "content": self.SYSTEM_PROMPT},
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
                raw_response=parsed
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
        language: str = "zh"
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
        language: str = "zh"
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
        language: str = "zh"
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

1. Correctness (正确性)
   - Does the code pass all test cases?
   - Handle edge cases properly?
   - Produce correct output?

2. Code Quality (代码质量)
   - Readable and well-structured
   - Good variable/function naming
   - Appropriate comments (not excessive)
   - Follows Python conventions (PEP 8)

3. Efficiency (效率)
   - Time complexity (Big O)
   - Space complexity
   - Avoids unnecessary operations

4. Problem Understanding (问题理解)
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
        language: str = "zh"
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
                analysis=f"代码通过了 {passed}/{total} 个测试用例 ({correctness_pct:.0f}%)。" if language == "zh" else f"Code passed {passed}/{total} test cases ({correctness_pct:.0f}%).",
                strengths=[],
                concerns=[f"评分解析失败: {e}"],
                highlight_quotes=[],
                raw_response=None
            )

    async def get_coding_immediate_feedback(
        self,
        problem_description: str,
        code: str,
        test_results: list[dict],
        language: str = "zh"
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


# Global instance
scoring_service = ScoringService()
