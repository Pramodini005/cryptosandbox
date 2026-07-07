from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserStatsResponse
from app.services.auth_service import auth_service
from app.api.v1.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's activity statistics and achievements."""
    return await auth_service.get_user_stats(db, current_user.id)
