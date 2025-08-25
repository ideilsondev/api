from sqlalchemy import BigInteger, Column, DateTime, Integer, ForeignKey, String, Table, func
from app.models.base import Base, BaseModel

class UserTenant(BaseModel):
    __tablename__ = 'user_tenants'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), primary_key=True)
    role = Column(String, default='viewer')
    invited_at = Column(DateTime, default=func.now(), nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    invited_by = Column(String, default='client', nullable=True)