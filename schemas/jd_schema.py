from pydantic import BaseModel
from typing import List, Optional

class JDProfile(BaseModel):
    role_name: Optional[str] = ""
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    experience_required: Optional[str] = ""
    education_required: Optional[str] = ""
