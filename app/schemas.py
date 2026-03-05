from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class Role(str, Enum):
    applicant = "applicant"
    approver = "approver"


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator("password")
    def password_strength(cls, v):
        if any(c.isdigit() for c in v) and any(c.isalpha() for c in v):
            return v
        raise ValueError("Password must contain letters and numbers")


class UserInDB(UserBase):
    id: int
    hashed_password: str
    role: Role

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class DocumentBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    status: DocumentStatus = DocumentStatus.draft

    @validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v


class DocumentCreate(DocumentBase):
    applicant_id: int

    class Config:
        orm_mode = True


class DocumentOut(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    applicant_id: int

    class Config:
        orm_mode = True


class ApprovalDecision(str, Enum):
    approve = "approve"
    reject = "reject"


class ApprovalRequestBase(BaseModel):
    document_id: int
    approver_id: int
    decision: Optional[ApprovalDecision] = None
    comments: Optional[str] = Field(None, max_length=500)

    @validator("comments")
    def comments_not_too_long(cls, v):
        if v and len(v) > 500:
            raise ValueError("Comments cannot exceed 500 characters")
        return v


class ApprovalRequestCreate(ApprovalRequestBase):
    class Config:
        orm_mode = True


class ApprovalRequestOut(ApprovalRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PaginatedResponse(BaseModel):
    items: List[DocumentOut]
    total: int
    page: int
    size: int

    @validator("total", always=True)
    def set_total(cls, v, values):
        return values.get("items") and len(values["items"]) or 0


class ErrorResponse(BaseModel):
    detail: str

    class Config:
        schema_extra = {"example": {"detail": "An unexpected error occurred"}}