from pydantic_ai import Agent
from config.groq_setup import MODEL
from schemas.bias_schema import BiasReport

bias_detector_agent = Agent(
    model=MODEL,
    output_type=BiasReport,
    system_prompt="""
        You are a hiring bias detection agent.

        Check whether hiring recommendations are influenced by:

        - Gender
        - Religion
        - Age
        - Nationality
        - Race
        - Marital Status

        Return:
        - bias_detected
        - bias_reason
        - compliance_status
        """
        )