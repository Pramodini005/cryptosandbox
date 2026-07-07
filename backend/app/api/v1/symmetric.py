from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import (
    SymmetricEncryptRequest, SymmetricEncryptResponse,
    SymmetricDecryptRequest, SymmetricDecryptResponse,
)
from app.services.symmetric_service import symmetric_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/symmetric", tags=["Symmetric Cryptography"])


@router.post("/encrypt", response_model=SymmetricEncryptResponse)
async def encrypt(
    req: SymmetricEncryptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Encrypt plaintext using symmetric algorithms (AES-GCM, AES-CBC, AES-CTR, ChaCha20, Fernet)."""
    result = symmetric_service.encrypt(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Encrypt", "symmetric", req.plaintext[:50])
    return result


@router.post("/decrypt", response_model=SymmetricDecryptResponse)
async def decrypt(
    req: SymmetricDecryptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Decrypt ciphertext using symmetric algorithms."""
    result = symmetric_service.decrypt(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Decrypt", "symmetric", "[decryption]")
    return result
