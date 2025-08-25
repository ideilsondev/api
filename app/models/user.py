from sqlalchemy import Column, BigInteger, Boolean, JSON, DateTime, String, func
from app.models.base import Base
import time

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, default=lambda: int(time.time() * 1000))
    is_active = Column(Boolean, default=True, nullable=True)
    accept_terms = Column(Boolean, default=False, nullable=True)
    extra_fields = Column(JSON, default=dict, nullable=False)
    email = Column(String, unique=True, index=True)
    name = Column(String, )
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())