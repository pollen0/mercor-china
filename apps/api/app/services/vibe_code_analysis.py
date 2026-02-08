"""
Vibe Code Analysis Service.

Analyzes AI coding session logs (Cursor, Claude Code, Copilot) using Claude
to assess how a student uses AI tools. Produces a "Builder Score" that
reveals whether the student leads with intent or lets AI drive.

Uses Claude Sonnet/Opus exclusively - OpenAI is only used for Whisper STT.
"""
import hashlib
import httpx
import json
import logging
import re
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from ..config import settings

logger = logging.getLogger("pathway.vibe_code_analysis")

# Algorithm version - increment when scoring logic changes
VIBE_SCORING_VERSION = "1.0.0"


@dataclass
class VibeScoreResult:
    """Result of analyzing an AI coding session."""
    # Dimension scores (0-10)
    direction: float
    design_thinking: float
    iteration_quality: float
    product_sense: float
    ai_leadership: float
    # Overall
    builder_score: float
    # Qualitative
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    notable_patterns: list[str]
    builder_archetype: str  # architect, iterative_builder, experimenter, ai_dependent, copy_paster
    # Details
    details: dict
    # Metadata
    scoring_model: str
    scoring_version: str = VIBE_SCORING_VERSION
    scored_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# SECRET REDACTION
# ============================================================================

# Patterns to redact from uploaded session logs
REDACTION_PATTERNS = [
    (r'(?:sk-|pk-|rk-)[a-zA-Z0-9]{20,}', '[REDACTED_API_KEY]'),
    (r'(?:ghp_|gho_|ghu_|ghs_|ghr_)[a-zA-Z0-9]{36,}', '[REDACTED_GITHUB_TOKEN]'),
    (r'(?:xox[bpars]-)[a-zA-Z0-9\-]{10,}', '[REDACTED_SLACK_TOKEN]'),
    (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),
    (r'(?:password|passwd|pwd|secret|token|api_key|apikey|auth)\s*[=:]\s*["\']?[^\s"\']{8,}', '[REDACTED_SECRET]'),
    (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----[\s\S]*?-----END', '[REDACTED_PRIVATE_KEY]'),
    (r'(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis)://[^\s"\']+', '[REDACTED_DB_URL]'),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]'),
]


def redact_secrets(content: str) -> str:
    """Remove API keys, tokens, passwords, and PII from session content."""
    redacted = content
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
    return redacted


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content for dedup."""
    return hashlib.sha256(content.encode()).hexdigest()


def count_messages(content: str) -> int:
    """Estimate the number of user<->AI exchanges in a session log."""
    # Common patterns for user messages in different tools
    patterns = [
        r'(?:^|\n)\s*(?:User|Human|You|>)\s*:',  # "User:", "Human:", "> prompt"
        r'(?:^|\n)\s*\[user\]',  # [user] tags
        r'(?:^|\n)#{1,3}\s*(?:User|Prompt|Input)',  # Markdown headers
        r'"role"\s*:\s*"user"',  # JSON format (Claude Code exports)
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, content, re.IGNORECASE))
    return max(count, 1)  # At least 1 if content exists


# ============================================================================
# SESSION PARSERS - Normalize different tool formats
# ============================================================================

def detect_source(content: str) -> str:
    """Auto-detect which AI tool generated this session log."""
    lower = content.lower()

    if 'cursor' in lower and ('composer' in lower or 'chat' in lower):
        return 'cursor'
    if 'claude code' in lower or 'claude-code' in lower or '"type": "human"' in lower:
        return 'claude_code'
    if 'copilot' in lower and ('github' in lower or 'suggestion' in lower):
        return 'copilot'
    if 'chatgpt' in lower or 'openai' in lower:
        return 'chatgpt'

    # Try JSON format detection
    try:
        data = json.loads(content)
        if isinstance(data, list) and len(data) > 0:
            first = data[0]
            if 'role' in first and 'content' in first:
                return 'claude_code'  # Standard message format
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return 'other'


def normalize_session(content: str, source: str) -> str:
    """
    Normalize session content into a standard format for analysis.
    Returns a clean text representation of the conversation.
    """
    # Try to parse as JSON first (Claude Code, structured exports)
    try:
        data = json.loads(content)
        if isinstance(data, list):
            lines = []
            for msg in data:
                role = msg.get('role', 'unknown').upper()
                text = msg.get('content', '')
                if isinstance(text, list):
                    # Handle content blocks (Claude format)
                    text = ' '.join(
                        block.get('text', '') if isinstance(block, dict) else str(block)
                        for block in text
                    )
                lines.append(f"[{role}]: {text}")
            return '\n\n'.join(lines)
        elif isinstance(data, dict):
            # Single session object with messages array
            messages = data.get('messages', data.get('conversation', []))
            if messages:
                lines = []
                for msg in messages:
                    role = msg.get('role', 'unknown').upper()
                    text = msg.get('content', '')
                    lines.append(f"[{role}]: {text}")
                return '\n\n'.join(lines)
    except (json.JSONDecodeError, TypeError):
        pass

    # Already in text format - return as-is
    return content


# ============================================================================
# CLAUDE-POWERED ANALYSIS
# ============================================================================

ANALYSIS_SYSTEM_PROMPT = """You are an expert engineering hiring evaluator analyzing AI coding session logs.

Your task: Assess how a college student uses AI coding tools (Cursor, Claude Code, Copilot, etc.).
You are NOT evaluating the code output - you are evaluating the BUILDER'S THINKING PROCESS.

## What Great Builders Do:
- Give clear, specific instructions with context ("Build a REST API for user auth with JWT, using Express and Postgres")
- Discuss architecture and tradeoffs BEFORE jumping into code
- Question AI suggestions when they seem wrong or suboptimal
- Catch and fix bugs themselves, using AI as an assistant
- Think about users, edge cases, error handling, and security
- Iterate on design, not just accept first output
- Break complex tasks into smaller, manageable pieces

## What Weak Builders Do:
- Give vague prompts ("make a website", "fix this")
- Accept every AI suggestion without questioning
- Paste error messages without trying to understand them
- Never discuss design, architecture, or tradeoffs
- Skip error handling, testing, edge cases
- Let AI make all decisions about structure and approach
- Try to build everything in one massive prompt

## Scoring Dimensions (0-100 scale each):

1. **Direction & Intent** (weight: 25%)
   - Does the student give clear, specific instructions?
   - Do they set context and requirements upfront?
   - Do they have a clear goal, not just "build me something"?

2. **Design Thinking** (weight: 25%)
   - Do they discuss architecture before implementation?
   - Do they consider tradeoffs (performance, simplicity, maintainability)?
   - Do they plan data models, API structure, component hierarchy?

3. **Iteration Quality** (weight: 20%)
   - When something breaks, do they debug thoughtfully?
   - Do they understand error messages or just paste them?
   - Do they refine and improve iteratively?

4. **Product Sense & Empathy** (weight: 15%)
   - Do they mention users, UX, accessibility?
   - Do they think about edge cases and error states?
   - Do they care about the end-user experience?

5. **AI Leadership** (weight: 15%)
   - Are they clearly the driver, or is AI driving them?
   - Do they push back on bad AI suggestions?
   - Do they use AI as a tool, not a crutch?

## Builder Archetypes:
- **architect**: Plans thoroughly, designs before building, questions AI decisions
- **iterative_builder**: Builds incrementally, tests often, refines through cycles
- **experimenter**: Tries many approaches, curious, explores alternatives
- **ai_dependent**: Relies heavily on AI for decisions, accepts output uncritically
- **copy_paster**: Minimal effort, just pastes errors back, no original thinking

Always respond in valid JSON."""

ANALYSIS_USER_PROMPT_TEMPLATE = """Analyze this AI coding session log.

SESSION SOURCE: {source}
SESSION TITLE: {title}
SESSION DESCRIPTION: {description}

--- BEGIN SESSION LOG ---
{session_content}
--- END SESSION LOG ---

Evaluate the student's builder quality based on their interaction patterns.

Respond in JSON format:
{{
    "scores": {{
        "direction": <0-100, clarity and specificity of instructions>,
        "design_thinking": <0-100, architecture discussion, tradeoff analysis>,
        "iteration_quality": <0-100, debugging approach, refinement quality>,
        "product_sense": <0-100, user empathy, edge cases, error handling>,
        "ai_leadership": <0-100, student drives vs AI drives>
    }},
    "builder_score": <0-100, weighted overall score>,
    "summary": "<2-3 sentence assessment of this student as a builder>",
    "strengths": ["<specific strength with evidence from session>", "<strength 2>"],
    "weaknesses": ["<specific weakness with evidence>", "<weakness 2>"],
    "notable_patterns": ["<interesting pattern observed>", "<pattern 2>"],
    "builder_archetype": "<one of: architect, iterative_builder, experimenter, ai_dependent, copy_paster>",
    "evidence": {{
        "best_moment": "<quote or description of the student's best moment in the session>",
        "worst_moment": "<quote or description of a weak moment>",
        "direction_examples": ["<example of clear/unclear instruction>"],
        "design_examples": ["<example of design thinking or lack thereof>"],
        "iteration_examples": ["<example of debugging approach>"],
        "product_examples": ["<example of user empathy or oversight>"],
        "leadership_examples": ["<example of leading or deferring to AI>"]
    }}
}}"""


def _clamp_score(score: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """Clamp a score to valid bounds."""
    if score is None:
        return min_val
    try:
        score = float(score)
    except (TypeError, ValueError):
        return min_val
    return max(min_val, min(max_val, score))


class VibeCodeAnalysisService:
    """
    Service for analyzing AI coding session logs using Claude.

    Uses Claude Sonnet for standard analysis, Claude Opus for deeper reasoning.
    OpenAI is NOT used here - only for Whisper STT elsewhere.
    """

    # Scoring weights for computing overall builder_score
    DIMENSION_WEIGHTS = {
        'direction': 0.25,
        'design_thinking': 0.25,
        'iteration_quality': 0.20,
        'product_sense': 0.15,
        'ai_leadership': 0.15,
    }

    def __init__(self):
        self.anthropic_api_key = settings.anthropic_api_key
        # Use Opus for deep analysis of builder quality
        self.analysis_model = settings.claude_thinking_model  # Claude Opus
        # Fallback to Sonnet if needed
        self.fallback_model = settings.claude_model  # Claude Sonnet
        self.anthropic_base_url = "https://api.anthropic.com/v1"

        if not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set - vibe code analysis will not work")

    async def _call_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 4000
    ) -> dict:
        """Call Claude API for analysis. Uses Opus by default for thorough evaluation."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        use_model = model or self.analysis_model

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.anthropic_base_url}/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": use_model,
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

            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())

    async def analyze_session(
        self,
        session_content: str,
        source: str = "other",
        title: str = "",
        description: str = "",
    ) -> VibeScoreResult:
        """
        Analyze an AI coding session and produce a builder score.

        Args:
            session_content: The normalized session log text
            source: Which tool (cursor, claude_code, copilot, etc.)
            title: Student-provided title for the session
            description: Student-provided description

        Returns:
            VibeScoreResult with scores, summary, and detailed analysis
        """
        # Truncate very long sessions to stay within context limits
        # Keep first and last portions for best signal
        max_chars = 80000
        if len(session_content) > max_chars:
            half = max_chars // 2
            session_content = (
                session_content[:half]
                + "\n\n[... middle of session truncated for analysis ...]\n\n"
                + session_content[-half:]
            )

        user_prompt = ANALYSIS_USER_PROMPT_TEMPLATE.format(
            source=source,
            title=title or "Untitled Session",
            description=description or "No description provided",
            session_content=session_content,
        )

        try:
            parsed = await self._call_claude(
                system_prompt=ANALYSIS_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            model_used = self.analysis_model
        except Exception as e:
            logger.warning(f"Opus analysis failed, falling back to Sonnet: {e}")
            try:
                parsed = await self._call_claude(
                    system_prompt=ANALYSIS_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    model=self.fallback_model,
                )
                model_used = self.fallback_model
            except Exception as fallback_error:
                logger.error(f"Both Claude models failed: {fallback_error}")
                raise

        scores = parsed.get("scores", {})

        # Convert 0-100 scores to 0-10 scale
        dimension_scores = {}
        for dim in self.DIMENSION_WEIGHTS:
            raw = scores.get(dim, 50)
            dimension_scores[dim] = _clamp_score(float(raw) / 10.0, 0.0, 10.0)

        # Calculate weighted overall score
        overall = sum(
            dimension_scores[dim] * weight
            for dim, weight in self.DIMENSION_WEIGHTS.items()
        )
        overall = _clamp_score(round(overall, 2), 0.0, 10.0)

        return VibeScoreResult(
            direction=round(dimension_scores['direction'], 2),
            design_thinking=round(dimension_scores['design_thinking'], 2),
            iteration_quality=round(dimension_scores['iteration_quality'], 2),
            product_sense=round(dimension_scores['product_sense'], 2),
            ai_leadership=round(dimension_scores['ai_leadership'], 2),
            builder_score=overall,
            summary=parsed.get("summary", ""),
            strengths=parsed.get("strengths", []),
            weaknesses=parsed.get("weaknesses", []),
            notable_patterns=parsed.get("notable_patterns", []),
            builder_archetype=parsed.get("builder_archetype", "unknown"),
            details=parsed.get("evidence", {}),
            scoring_model=model_used,
            scoring_version=VIBE_SCORING_VERSION,
        )

    def preprocess_upload(self, raw_content: str) -> dict:
        """
        Preprocess an uploaded session log:
        1. Redact secrets/PII
        2. Detect source tool
        3. Normalize format
        4. Compute metadata

        Returns dict with processed data ready for storage and analysis.
        """
        # Step 1: Redact secrets
        redacted = redact_secrets(raw_content)

        # Step 2: Detect source
        source = detect_source(raw_content)

        # Step 3: Normalize
        normalized = normalize_session(redacted, source)

        # Step 4: Metadata
        content_hash = compute_content_hash(normalized)
        msg_count = count_messages(normalized)
        word_count = len(normalized.split())

        return {
            "session_content": normalized,
            "source": source,
            "content_hash": content_hash,
            "message_count": msg_count,
            "word_count": word_count,
        }


# Global instance
vibe_code_service = VibeCodeAnalysisService()
