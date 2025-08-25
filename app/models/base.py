from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Boolean, JSON, DateTime, func, ForeignKey, event
from sqlalchemy.orm import mapped_column
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import contextvars
from datetime import datetime

metadata = MetaData()
Base = declarative_base(metadata=metadata)

current_user_var = contextvars.ContextVar("current_user")

class BaseModel(Base):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, default=lambda: int(func.now() * 1000))
    is_active = Column(Boolean, default=True, nullable=True)
    extra_fields = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    updated_by = Column(BigInteger, ForeignKey('users.id'), nullable=True)

    def get(self, key_path: str, default: Any = None) -> Any:
        """Acessa chaves aninhadas dentro de extra_fields."""
        if not key_path or not isinstance(self.extra_fields, dict):
            return default
        keys = key_path.split('.')
        value = self.extra_fields
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any, db: Optional[AsyncSession] = None) -> None:
        """Define chaves aninhadas dentro de extra_fields sem commit automático."""
        if not key_path:
            return
        if not isinstance(self.extra_fields, dict):
            self.extra_fields = {}
        keys = key_path.split('.')
        current = self.extra_fields
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        if db:
            db.add(self)  # Adiciona ao session, commit fica a cargo do chamador

    async def async_save(self, db: AsyncSession) -> None:
        """Método assíncrono para salvar as alterações no banco."""
        db.add(self)
        await db.commit()


# Event listeners para preencher created_by e updated_by
@event.listens_for(BaseModel, "before_insert")
def set_created_by(mapper, connection, target):
    current_user = current_user_var.get()
    if current_user is not None:
        target.created_by = current_user

@event.listens_for(BaseModel, "before_update")
def set_updated_by(mapper, connection, target):
    current_user = current_user_var.get()
    if current_user is not None:
        target.updated_by = current_user