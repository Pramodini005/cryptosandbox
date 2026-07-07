from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import DHKeyExchangeRequest, DHKeyExchangeResponse
from app.services.key_exchange_service import key_exchange_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/key-exchange", tags=["Key Exchange"])


@router.post("/diffie-hellman", response_model=DHKeyExchangeResponse)
async def diffie_hellman(
    req: DHKeyExchangeRequest = DHKeyExchangeRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Simulate Diffie-Hellman key exchange between Alice and Bob."""
    result = key_exchange_service.diffie_hellman(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, "Diffie-Hellman Simulation", "key-exchange")
    return result
