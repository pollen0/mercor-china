"""
Resume parsing service for extracting and analyzing candidate resumes.
Uses pdfplumber for PDFs, python-docx for Word documents, and DeepSeek for intelligent parsing.
"""

import io
import json
import logging
import httpx
from typing import Optional
from ..config import settings
from ..schemas.candidate import ParsedResume, ExperienceItem, EducationItem, ProjectItem, PersonalizedQuestion

logger = logging.getLogger("zhimian.resume")


class ResumeService:
    """Service for parsing resumes and generating personalized questions."""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url

    async def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Extract raw text from a resume file (PDF or Word).

        Args:
            file_bytes: Raw file bytes
            filename: Original filename (used to determine file type)

        Returns:
            Extracted text content
        """
        filename_lower = filename.lower()

        if filename_lower.endswith('.pdf'):
            return self._extract_from_pdf(file_bytes)
        elif filename_lower.endswith('.docx'):
            return self._extract_from_docx(file_bytes)
        elif filename_lower.endswith('.doc'):
            raise ValueError("Old .doc format not supported. Please use .docx or PDF.")
        else:
            raise ValueError(f"Unsupported file format: {filename}. Please upload PDF or DOCX.")

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n\n".join(text_parts)

    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from Word document using python-docx."""
        try:
            from docx import Document
        except ImportError:
            raise RuntimeError("python-docx not installed. Run: pip install python-docx")

        doc = Document(io.BytesIO(file_bytes))
        text_parts = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)

        return "\n".join(text_parts)

    async def parse_resume(self, raw_text: str) -> ParsedResume:
        """
        Parse raw resume text into structured data using DeepSeek LLM.

        Args:
            raw_text: Extracted text from resume

        Returns:
            ParsedResume with structured data
        """
        if not self.api_key:
            # Return empty parsed resume if no API key
            return ParsedResume()

        system_prompt = """You are an expert resume parser. Extract structured information from the resume text provided.
Be accurate and only include information that is clearly stated in the resume.
If a field is not found, leave it empty/null.
For dates, use formats like "2020-01", "2020", or "Present" for current positions.
For skills, extract both technical skills and soft skills.
Respond in valid JSON format only."""

        user_prompt = f"""Parse this resume and extract structured information:

RESUME TEXT:
{raw_text[:8000]}  # Limit to avoid token limits

Respond with JSON in this exact format:
{{
    "name": "Full Name or null",
    "email": "email@example.com or null",
    "phone": "phone number or null",
    "location": "City, Country or null",
    "summary": "Professional summary or null",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "company": "Company Name",
            "title": "Job Title",
            "start_date": "2020-01",
            "end_date": "Present or 2023-06",
            "description": "Brief description",
            "highlights": ["achievement 1", "achievement 2"]
        }}
    ],
    "education": [
        {{
            "institution": "University Name",
            "degree": "Bachelor's/Master's/etc",
            "field_of_study": "Computer Science or null",
            "start_date": "2016",
            "end_date": "2020",
            "gpa": "3.8/4.0 or null"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["Python", "React"],
            "highlights": ["outcome 1"]
        }}
    ],
    "languages": ["English", "Mandarin"],
    "certifications": ["AWS Certified", "PMP"]
}}"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,  # Low temperature for accuracy
                        "max_tokens": 3000,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return ParsedResume(
                    name=parsed.get("name"),
                    email=parsed.get("email"),
                    phone=parsed.get("phone"),
                    location=parsed.get("location"),
                    summary=parsed.get("summary"),
                    skills=parsed.get("skills", []),
                    experience=[
                        ExperienceItem(**exp) for exp in parsed.get("experience", [])
                    ],
                    education=[
                        EducationItem(**edu) for edu in parsed.get("education", [])
                    ],
                    projects=[
                        ProjectItem(**proj) for proj in parsed.get("projects", [])
                    ],
                    languages=parsed.get("languages", []),
                    certifications=parsed.get("certifications", [])
                )

        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            # Return empty parsed resume on error
            return ParsedResume()

    async def generate_personalized_questions(
        self,
        parsed_resume: ParsedResume,
        job_title: Optional[str] = None,
        job_requirements: Optional[list[str]] = None,
        num_questions: int = 3
    ) -> list[PersonalizedQuestion]:
        """
        Generate personalized interview questions based on resume content.

        Args:
            parsed_resume: Structured resume data
            job_title: Target job title
            job_requirements: List of job requirements
            num_questions: Number of questions to generate

        Returns:
            List of PersonalizedQuestion objects
        """
        if not self.api_key:
            return []

        # Build context from resume
        resume_context = []
        if parsed_resume.experience:
            recent_exp = parsed_resume.experience[0]
            resume_context.append(f"Recent role: {recent_exp.title} at {recent_exp.company}")
        if parsed_resume.skills:
            resume_context.append(f"Skills: {', '.join(parsed_resume.skills[:10])}")
        if parsed_resume.projects:
            resume_context.append(f"Notable project: {parsed_resume.projects[0].name}")
        if parsed_resume.education:
            edu = parsed_resume.education[0]
            resume_context.append(f"Education: {edu.degree} from {edu.institution}")

        job_context = job_title or "General"
        requirements_text = "\n".join(f"- {req}" for req in (job_requirements or []))

        system_prompt = """You are an expert interviewer. Generate personalized interview questions based on the candidate's resume.
Questions should:
1. Be specific to the candidate's experience
2. Probe deeper into their accomplishments
3. Assess fit for the target role
4. Mix behavioral and technical questions

Respond in valid JSON format only."""

        user_prompt = f"""Generate {num_questions} personalized interview questions for this candidate:

CANDIDATE PROFILE:
{chr(10).join(resume_context)}

TARGET JOB: {job_context}
{f"REQUIREMENTS:{chr(10)}{requirements_text}" if requirements_text else ""}

Respond with JSON in this format:
{{
    "questions": [
        {{
            "text": "English question text",
            "text_zh": "Chinese translation of the question",
            "category": "behavioral/technical/experience",
            "based_on": "What resume element this references"
        }}
    ]
}}"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return [
                    PersonalizedQuestion(**q)
                    for q in parsed.get("questions", [])
                ]

        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return []


# Global instance
resume_service = ResumeService()
