from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import timedelta
from app.models.user import User
from app.models.log import OperationLog
from app.models.achievement import Achievement
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut
from app.schemas.user import UserStatsResponse, OperationLogOut, AchievementOut
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


class AuthService:
    async def register(self, db: AsyncSession, data: UserRegister) -> UserOut:
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
        )
        db.add(user)
        await db.flush()
        achievement = Achievement(
            user_id=user.id,
            badge="First Login",
            description="Joined the Cryptography Learning Sandbox!",
        )
        db.add(achievement)
        await db.commit()
        await db.refresh(user)
        return UserOut.model_validate(user)

    async def login(self, db: AsyncSession, data: UserLogin) -> TokenResponse:
        result = await db.execute(select(User).where(User.username == data.username))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        access_token = create_access_token({"sub": str(user.id), "username": user.username})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def get_current_user(self, db: AsyncSession, token: str) -> User:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    async def get_user_stats(self, db: AsyncSession, user_id: int) -> UserStatsResponse:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        logs_result = await db.execute(
            select(OperationLog).where(OperationLog.user_id == user_id).order_by(OperationLog.created_at.desc()).limit(20)
        )
        logs = logs_result.scalars().all()
        ach_result = await db.execute(select(Achievement).where(Achievement.user_id == user_id))
        achievements = ach_result.scalars().all()

        ops_by_module: dict[str, int] = {}
        for log in logs:
            ops_by_module[log.module] = ops_by_module.get(log.module, 0) + 1

        all_logs_result = await db.execute(select(OperationLog).where(OperationLog.user_id == user_id))
        all_logs = all_logs_result.scalars().all()
        for log in all_logs:
            ops_by_module[log.module] = ops_by_module.get(log.module, 0)

        return UserStatsResponse(
            total_operations=len(all_logs),
            operations_by_module=ops_by_module,
            recent_logs=[OperationLogOut.model_validate(l) for l in logs],
            achievements=[AchievementOut.model_validate(a) for a in achievements],
            member_since=user.created_at if user else None,
        )

    async def log_operation(self, db: AsyncSession, user_id: int, operation: str, module: str, input_preview: str = ""):
        log = OperationLog(user_id=user_id, operation=operation, module=module, input_preview=input_preview[:200])
        db.add(log)
        # Check for achievement unlocks
        all_logs_result = await db.execute(select(OperationLog).where(OperationLog.user_id == user_id))
        count = len(all_logs_result.scalars().all())
        if count == 10:
            db.add(Achievement(user_id=user_id, badge="Crypto Explorer", description="Performed 10 cryptographic operations"))
        elif count == 50:
            db.add(Achievement(user_id=user_id, badge="Cipher Master", description="Performed 50 cryptographic operations"))
        await db.commit()


auth_service = AuthService()
