from pydantic_ai import Agent
from config.groq_setup import MODEL
from schemas.match_schema import MatchResult


matcher_agent = Agent(
    model=MODEL,
    output_type=MatchResult,
    system_prompt="""
You are an expert recruitment skill matcher.

Compare resume skills with job description skills.

Rules:

1. Consider synonyms.
2. Consider related technologies.
3. Consider broader categories.
4. Consider equivalent concepts.

Examples:

Core Java = Java

AWS Lambda = AWS Services

HTML + CSS = Frontend Technologies

REST API = RESTful API Design

Spring Framework = Spring

Return matched skills and missing skills.
"""
)


class SkillMatcher:

    @staticmethod
    async def calculate_match(
        resume_skills: list,
        jd_skills: list
    ):

        prompt = f"""
            Resume Skills:
            {resume_skills}

            JD Skills:
            {jd_skills}
            """

        result = await matcher_agent.run(prompt)

        match_data = result.output

        score = (
            len(match_data.matched_skills)
            / len(jd_skills)
        ) * 100 if jd_skills else 0

        return {
            "matched_skills":
                match_data.matched_skills,

            "missing_skills":
                match_data.missing_skills,

            "match_percentage":
                round(score, 2)
        }