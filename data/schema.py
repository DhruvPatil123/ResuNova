from pydantic import BaseModel, Field
from typing import List, Optional

class Experience(BaseModel):
    company: str = ""
    role: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: List[str] = []  # List of bullet points

class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: Optional[str] = None

class Project(BaseModel):
    name: str = ""
    link: str = ""
    description: List[str] = []
    tech_stack: List[str] = []

class ResumeData(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    summary: str = ""
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[str] = []
    projects: List[Project] = []
    certifications: List[str] = []
