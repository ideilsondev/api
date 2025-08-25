from sqlalchemy import BigInteger, Column, Integer, String
from app.models.base import Base

from sqlalchemy import Column, String, ForeignKey
from .base import BaseModel

class Tenant(BaseModel):
    __tablename__ = 'tenants'
    name = Column(String, nullable=True)
    status = Column(String, default='pending')
    owner_id = Column(BigInteger, ForeignKey('users.id'), nullable=True) 
    # server_id = Column(BigInteger, ForeignKey('servers.id'), nullable=True)
    # database_id = Column(BigInteger, ForeignKey('databases.id'), nullable=True)