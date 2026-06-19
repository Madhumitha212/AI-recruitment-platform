from pydantic import BaseModel
from typing import List, Optional

class ResumeProfile(BaseModel):
    candidate_name: Optional[str] = ""
    email: Optional[str] = ""
    skills: Optional[List[str]] = []
    education: Optional[List[str]] = []
    experience: Optional[List[str]] = []
    projects: Optional[List[str]] = []
    certifications: Optional[List[str]] = []