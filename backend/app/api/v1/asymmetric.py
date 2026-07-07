from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import (
    AsymmetricKeyGenRequest, AsymmetricKeyGenResponse,
    AsymmetricEncryptRequest, AsymmetricEncryptResponse,
    AsymmetricDecryptRequest, AsymmetricDecryptResponse,
    SignRequest, SignResponse, VerifyRequest, VerifyResponse,
)
from app.services.asymmetric_service import asymmetric_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/asymmetric", tags=["Asymmetric Cryptography"])


@router.post("/generate-keys", response_model=AsymmetricKeyGenResponse)
async def generate_keys(
    req: AsymmetricKeyGenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Generate public/private key pairs (RSA, ECC, Ed25519)."""
    result = asymmetric_service.generate_keys(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Key Generation", "asymmetric")
    return result


@router.post("/encrypt", response_model=AsymmetricEncryptResponse)
async def encrypt(
    req: AsymmetricEncryptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Encrypt a message using a public key (RSA OAEP)."""
    result = asymmetric_service.encrypt(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, "RSA Encrypt", "asymmetric", req.plaintext[:50])
    return result


@router.post("/decrypt", response_model=AsymmetricDecryptResponse)
async def decrypt(
    req: AsymmetricDecryptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Decrypt a message using a private key (RSA OAEP)."""
    result = asymmetric_service.decrypt(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, "RSA Decrypt", "asymmetric")
    return result


@router.post("/sign", response_model=SignResponse)
async def sign(
    req: SignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Sign a message with a private key."""
    result = asymmetric_service.sign(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Sign", "signatures", req.message[:50])
    return result


@router.post("/verify", response_model=VerifyResponse)
async def verify(
    req: VerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Verify a digital signature."""
    result = asymmetric_service.verify(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Verify", "signatures")
    return result
