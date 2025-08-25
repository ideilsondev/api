from fastapi import APIRouter, Depends, Request  # Adicione Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user, limiter
from app.core.security import generate_api_key, hash_password
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyOut
from app.models.user import User

router = APIRouter(prefix="/api-keys")

@router.post("/", response_model=APIKeyOut)
@limiter.limit("5/minute")
async def create_api_key(request: Request, key_data: APIKeyCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    raw_key = generate_api_key()
    hashed_key = hash_password(raw_key)
    db_key = APIKey(hashed_key=hashed_key, tenant_id=key_data.tenant_id, description=key_data.description)
    db.add(db_key)
    await db.commit()
    return APIKeyOut(key=raw_key, description=key_data.description)