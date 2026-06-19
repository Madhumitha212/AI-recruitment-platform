import re


class RecommendationEngine:

    @staticmethod
    def get_recommendation(
        match_percentage: float,
        missing_skills: list,
        knowledge_base: str
    ):

        shortlist_threshold = 80
        hold_threshold = 60

        shortlist_match = re.search(
            r"Score\s*>=\s*(\d+)",
            knowledge_base,
            re.IGNORECASE
        )

        if shortlist_match:
            shortlist_threshold = int(
                shortlist_match.group(1)
            )

        missing_count = len(
            missing_skills
        )

        if (
            match_percentage >= shortlist_threshold
            and missing_count <= 3
        ):

            return {
                "decision": "SHORTLIST",
                "reason": "Strong skill match"
            }

        elif match_percentage >= hold_threshold:

            return {
                "decision": "HOLD",
                "reason": "Moderate skill match"
            }

        return {
            "decision": "REJECT",
            "reason": "Insufficient skill match"
        }