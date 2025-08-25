from fastapi import APIRouter, Depends, Request
from app.core.deps import get_current_user, get_api_key, limiter
from app.models.user import User
from app.models.api_key import APIKey

router = APIRouter(prefix="/protected")

@router.get("/user")
@limiter.limit("20/minute")
async def get_protected_user(request: Request, current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.email} (JWT protected)"}

@router.get("/integration")
@limiter.limit("50/minute")
async def get_protected_integration(request: Request, api_key: APIKey = Depends(get_api_key)):
    return {"msg": f"Integrated via API key for tenant {api_key.tenant_id}"}