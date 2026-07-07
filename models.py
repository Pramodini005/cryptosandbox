from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class AlertCondition(str, Enum):
    ABOVE = "above"
    BELOW = "below"

class Alert(BaseModel):
    id: Optional[str] = None
    symbol: str
    target_price: float
    condition: AlertCondition
    is_active: bool = True
    created_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    triggered_price: Optional[float] = None
    user_id: Optional[str] = "default"  # For multi-user support later
    
    class Config:
        use_enum_values = True

class PriceData(BaseModel):
    symbol: str
    current_price: float
    price_change_24h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime

class Portfolio(BaseModel):
    holdings: List[Dict] = []  # [{"symbol": "BTC", "amount": 0.5, "avg_buy_price": 45000}]
    total_value: float = 0.0
    total_pnl: float = 0.0
    last_updated: Optional[datetime] = None

class Notification(BaseModel):
    id: Optional[str] = None
    alert_id: str
    message: str
    sent_at: datetime
    type: str = "price_alert"
    read: bool = False

class MarketSentiment(BaseModel):
    overall_score: float
    sentiment: str
    components: Dict
    recommendation: str
    timestamp: datetime
