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
    """Service for AI-powered interview scoring using OpenAI GPT-4o."""

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
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com"

    async def _call_openai(self, messages: list[dict], temperature: float = 0.3) -> dict:
        """Make a call to OpenAI API."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
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

        result = await self._call_openai([
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

        result = await self._call_openai([
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


# Global instance
scoring_service = ScoringService()
