from pydantic import BaseModel

class BiasReport(BaseModel):
    bias_detected: bool
    bias_reason: str
    compliance_status: str