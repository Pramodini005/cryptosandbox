from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import (
    PasswordAnalyzeRequest, PasswordAnalyzeResponse,
    PasswordHashRequest, PasswordHashResponse,
    PasswordVerifyRequest, PasswordVerifyResponse,
    PasswordGenerateRequest, PasswordGenerateResponse,
)
from app.services.password_service import password_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/password", tags=["Password Security"])


@router.post("/analyze", response_model=PasswordAnalyzeResponse)
async def analyze_password(
    req: PasswordAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Analyze password strength, entropy, and crack time estimate."""
    result = password_service.analyze(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, "Password Analysis", "passwords")
    return result


@router.post("/hash", response_model=PasswordHashResponse)
async def hash_password(
    req: PasswordHashRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Hash a password using bcrypt, argon2, pbkdf2, or scrypt."""
    result = password_service.hash_password(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Hash", "passwords")
    return result


@router.post("/verify", response_model=PasswordVerifyResponse)
async def verify_password(
    req: PasswordVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Verify a password against a stored hash."""
    result = password_service.verify_password(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Verify", "passwords")
    return result


@router.post("/generate", response_model=PasswordGenerateResponse)
async def generate_password(
    req: PasswordGenerateRequest = PasswordGenerateRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Generate a secure password or passphrase."""
    return password_service.generate(req)
