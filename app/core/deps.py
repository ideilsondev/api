from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.security import hash_password, verify_password, verify_token
from app.models.api_key import APIKey
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
limiter = Limiter(key_func=get_remote_address)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    # Decodificar o token e extrair o payload
    payload = verify_token(token)
    user_id = payload.get("sub")
    print('usuario',user_id)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

    # Converter user_id de string para int
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuário inválido no token."
        )

    # Buscar usuário no banco
    user = await db.get(User, user_id_int)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")

    return user

async def get_api_key(api_key: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key requerida.")

    # Alternativa com ORM (opcional, substitui a query direta)
    stmt = select(APIKey).where(APIKey.hashed_key == hash_password(api_key))
    db_key = (await db.execute(stmt)).scalar_one_or_none()

    if not db_key or not verify_password(api_key, db_key.hashed_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida.")

    return db_key