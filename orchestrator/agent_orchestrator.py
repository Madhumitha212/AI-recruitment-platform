from agents.resume_agent import resume_agent
from agents.jd_agent import jd_agent
from matching.skill_matcher import SkillMatcher
from recommendation.recommendation_engine import RecommendationEngine
from agents.bias_detector_agent import bias_detector_agent
from rag.rag_service import RAGService
from notification.email_service import EmailService


class AgentOrchestrator:

    async def analyze_resume(self, resume_text: str):

        result = await resume_agent.run(resume_text)

        print("Resume Result:", result)

        return result.output


    async def analyze_jd(self, jd_text: str):

        result = await jd_agent.run(jd_text)

        print("JD Result:", result)

        return result.output
    
    async def detect_bias(
            self,
            resume_profile,
            jd_profile,
            match_report,
            recommendation,
            knowledge_base
        ):

            prompt = f"""
        Candidate Profile:

        {resume_profile}

        Job Description:

        {jd_profile}

        Match Report:

        {match_report}

        Recommendation:

        {recommendation}

        Knowledge Base:

        {knowledge_base}

        Check whether this recommendation contains hiring bias.
        """

            result = await bias_detector_agent.run(prompt)

            return result.output
    
    async def evaluate_candidate(
        self,
        resume_text: str,
        jd_text: str
    ):

        resume_profile = await self.analyze_resume(
            resume_text
        )

        knowledge_base = RAGService.retrieve_context(
            jd_text
        )

        enhanced_jd = f"""
        Knowledge Base Context:

        {knowledge_base}

        Job Description:

        {jd_text}
        """

        jd_profile = await self.analyze_jd(
            enhanced_jd
        )

        match_report = await SkillMatcher.calculate_match(
            resume_profile.skills,
            jd_profile.required_skills
        )

        recommendation = (
            RecommendationEngine.get_recommendation(
                match_report["match_percentage"],
                match_report["missing_skills"],
                knowledge_base
            )
        )

        if (
            recommendation["decision"]
            == "SHORTLIST"
            and resume_profile.email
        ):
            EmailService.send_shortlist_email(
                candidate_email=resume_profile.email,
                candidate_name=resume_profile.candidate_name,
                match_percentage=
                match_report["match_percentage"]
            )

        bias_report = await self.detect_bias(
            resume_profile,
            jd_profile,
            match_report,
            recommendation,
            knowledge_base
        )

        return {

            "candidate_name":
                resume_profile.candidate_name,

            "email":
                resume_profile.email,

            "skills":
                resume_profile.skills,

            "required_skills":
                jd_profile.required_skills,

            "match_report":
                match_report,

            "recommendation":
                recommendation,

            "bias_report":
                bias_report.model_dump()
        }

