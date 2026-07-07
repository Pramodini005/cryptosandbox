from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import ClassicalEncryptRequest, ClassicalEncryptResponse, ClassicalDecryptRequest, ClassicalDecryptResponse
from app.services.classical_service import classical_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/classical", tags=["Classical Cryptography"])


@router.post("/encrypt", response_model=ClassicalEncryptResponse)
async def encrypt(
    req: ClassicalEncryptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Encrypt using classical ciphers (Caesar, Vigenere, Playfair, Rail Fence, OTP, Columnar)."""
    result = classical_service.encrypt(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Encrypt", "classical", req.plaintext[:50])
    return result


@router.post("/decrypt", response_model=ClassicalDecryptResponse)
async def decrypt(
    req: ClassicalDecryptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Decrypt using classical ciphers."""
    result = classical_service.decrypt(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Decrypt", "classical", req.ciphertext[:50])
    return result
