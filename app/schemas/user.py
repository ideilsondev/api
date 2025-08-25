from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Dict, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str
    accept_terms: bool = Field(default=False)
    extra_fields: Optional[Dict] = Field(default_factory=dict)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    accept_terms: bool
    extra_fields: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 