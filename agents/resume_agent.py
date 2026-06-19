from pydantic_ai import Agent
from config.groq_setup import MODEL
from schemas.resume_schema import ResumeProfile
import re

resume_agent = Agent(
    model=MODEL,
    output_type=ResumeProfile,
    system_prompt="""
You are an expert resume analyzer.

Extract:
- candidate_name
-email
- skills
- education
- experience
- projects
- certifications

Rules:
- Extract candidate email accurately.
- If email is missing return empty string.
- Return only structured output.
"""
)

def extract_email(text: str):

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if match:
        return match.group()

    return ""
