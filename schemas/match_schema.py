from pydantic import BaseModel
from typing import List

class MatchResult(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float