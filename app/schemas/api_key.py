from pydantic import BaseModel

class APIKeyCreate(BaseModel):
    description: str
    tenant_id: int

class APIKeyOut(BaseModel):
    key: str
    description: str