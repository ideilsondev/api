from fastapi import FastAPI, Request, Depends, HTTPException, status
from contextvars import ContextVar
from app.core.deps import get_db, limiter
from app.core.security import verify_token
from app.routers import auth, api_keys, protected, ws
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

# ContextVar para claims decodificados do JWT
jwt_claims_var = ContextVar("jwt_claims", default=None)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --------------------------------------------------------------------
# CORS
# --------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🚨 restrinja para domínios confiáveis em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# Middleware: valida token e guarda claims
# --------------------------------------------------------------------
PUBLIC_ROUTES = [
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
    "/docs",
    "/openapi.json"
]

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Se a rota estiver na lista pública → pula auth
    if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
        return await call_next(request)

    # Caso contrário, exige token
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token ausente")

    try:
        verify_token(token.replace("Bearer ", ""))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    return await call_next(request)

# --------------------------------------------------------------------
# Dependency: retorna usuário do banco (opcional ou obrigatório)
# --------------------------------------------------------------------
async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    claims = jwt_claims_var.get()
    if not claims or "sub" not in claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = await db.get(User, claims["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


# Rotas
app.include_router(auth.router)
app.include_router(api_keys.router)
app.include_router(protected.router)
app.include_router(ws.router)
