from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.core.deps import get_current_user, limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo usuário no sistema.
    """
    # Validação adicional: garantir que accept_terms seja True
    if not user.accept_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você deve aceitar os termos de uso para se registrar."
        )

    try:
        # Verificar se o email já existe
        stmt = select(User).where(User.email == user.email.lower().strip())
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail já registrado."
            )

        # Criar novo usuário com todos os campos do UserCreate
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email.lower().strip(),
            hashed_password=hashed_password,
            name=user.name,
            is_active=True,
            accept_terms=user.accept_terms,
            extra_fields=user.extra_fields or {},
        )

        # Adicionar ao banco, commit e refresh
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já registrado."
        )


# ---------- LOGIN ----------
@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Faz login no sistema e retorna tokens de acesso.
    """
    stmt = select(User).where(User.email == form_data.username.lower().strip())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Tentativa de login falhou para {form_data.username} em {datetime.now()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada."
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


# ---------- REFRESH ----------
@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh(request: Request, refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Gera novos tokens a partir de um refresh_token válido.
    """
    payload = verify_token(refresh_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de atualização inválido."
        )

    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


# ---------- ME (PROTEGIDA) ----------
@router.get("/me", response_model=UserOut)
async def get_me(request: Request, user: User = Depends(get_current_user)):
    """
    Retorna dados do usuário logado (precisa de token válido).
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada."
        )
    return user
