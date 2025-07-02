from pydantic import BaseModel, Field
from typing import Optional

class ResumeFields(BaseModel):
    name: Optional[str] = Field(None, description="First name of the candidate")
    surname: Optional[str] = Field(None, description="Surname of the candidate")
    current_profession: Optional[str] = Field(None, description="Current profession or job title")
    profile_category: Optional[str] = Field(None, description='"commercial" or "technical"')
    years_experience: Optional[float] = Field(None, description="Number of years of experience")
    # Add more fields as needed for extensibility 