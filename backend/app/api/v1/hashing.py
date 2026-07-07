from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.crypto import HashRequest, HashResponse, HashCompareRequest, HashCompareResponse
from app.services.hash_service import hash_service
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_optional_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/hash", tags=["Hashing"])


@router.post("/compute", response_model=HashResponse)
async def compute_hash(
    req: HashRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Compute hash of text using various algorithms."""
    result = hash_service.compute(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, f"{req.algorithm} Hash", "hashing", req.text[:50])
    return result


@router.post("/compare", response_model=HashCompareResponse)
async def compare_hashes(
    req: HashCompareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Compare multiple hash algorithms on the same text."""
    result = hash_service.compare(req)
    if current_user:
        await auth_service.log_operation(db, current_user.id, "Hash Compare", "hashing", req.text[:50])
    return result
