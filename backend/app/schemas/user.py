from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OperationLogOut(BaseModel):
    id: int
    operation: str
    module: str
    input_preview: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AchievementOut(BaseModel):
    id: int
    badge: str
    description: str
    earned_at: datetime

    model_config = {"from_attributes": True}


class UserStatsResponse(BaseModel):
    total_operations: int
    operations_by_module: dict[str, int]
    recent_logs: list[OperationLogOut]
    achievements: list[AchievementOut]
    member_since: datetime
