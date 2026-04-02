from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum
from typing import Optional
import uuid


class CandidateStatus(str, Enum):
    applied = "applied"
    interview = "interview"
    selected = "selected"
    rejected = "rejected"


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    skill: str
    status: CandidateStatus = CandidateStatus.applied

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be empty")
        return v

    @field_validator("skill")
    @classmethod
    def skill_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Skill must not be empty")
        return v


class StatusUpdate(BaseModel):
    status: CandidateStatus


class CandidateResponse(BaseModel):
    id: str
    name: str
    email: str
    skill: str
    status: CandidateStatus

    model_config = {"from_attributes": True}
