from pydantic_ai import Agent
from config.groq_setup import MODEL
from schemas.jd_schema import JDProfile

jd_agent = Agent(
    model=MODEL,
    output_type=JDProfile,
    system_prompt="""
        You are an expert Job Description Analyzer.

        Input contains:

        1. Knowledge Base Context
        2. Job Description

        Instructions:

        - Use Job Description as the primary source.
        - Use Knowledge Base Context to enrich missing skills,
        certifications, education requirements,
        experience requirements and technologies.
        - Do not invent unrelated skills.
        - Extract all required skills.
        - Extract all preferred skills.
        - Extract experience requirements.
        - Extract education requirements.

        Return only structured output..
        """
        )