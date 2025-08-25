from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    hashed_key = Column(String, unique=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    description = Column(String)