import sqlite3
import aiosqlite
import json
from typing import List, Dict, Optional
from datetime import datetime
from models.models import Alert, Portfolio, Notification

class Database:
    def __init__(self, db_path: str = "crypto_alerts.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Alerts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    condition TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP,
                    triggered_price REAL,
                    user_id TEXT DEFAULT 'default'
                )
            """)
            
            # Portfolio table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    user_id TEXT PRIMARY KEY DEFAULT 'default',
                    holdings TEXT,  -- JSON string
                    total_value REAL DEFAULT 0.0,
                    total_pnl REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Notifications table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    alert_id TEXT,
                    message TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    type TEXT DEFAULT 'price_alert',
                    read BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Price history table (for caching and analysis)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume REAL,
                    market_cap REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    async def save_alert(self, alert: Alert):
        """Save an alert to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO alerts (id, symbol, target_price, condition, is_active, created_at, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.symbol,
                alert.target_price,
                alert.condition,
                alert.is_active,
                alert.created_at,
                alert.user_id
            ))
            await db.commit()
    
    async def get_all_alerts(self) -> List[Alert]:
        """Get all alerts from database"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM alerts WHERE is_active = TRUE") as cursor:
                rows = await cursor.fetchall()
                alerts = []
                for row in rows:
                    alert = Alert(
                        id=row[0],
                        symbol=row[1],
                        target_price=row[2],
                        condition=row[3],
                        is_active=bool(row[4]),
                        created_at=datetime.fromisoformat(row[5]) if row[5] else None,
                        triggered_at=datetime.fromisoformat(row[6]) if row[6] else None,
                        triggered_price=row[7],
                        user_id=row[8]
                    )
                    alerts.append(alert)
                return alerts
    
    async def update_alert(self, alert: Alert):
        """Update an alert in database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE alerts 
                SET is_active = ?, triggered_at = ?, triggered_price = ?
                WHERE id = ?
            """, (
                alert.is_active,
                alert.triggered_at,
                alert.triggered_price,
                alert.id
            ))
            await db.commit()
    
    async def delete_alert(self, alert_id: str):
        """Delete an alert from database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            await db.commit()
    
    async def save_notification(self, notification: Dict):
        """Save a notification to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO notifications (id, alert_id, message, sent_at, type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                notification.get("id", ""),
                notification.get("alert_id", ""),
                notification["message"],
                notification["sent_at"],
                notification.get("type", "price_alert")
            ))
            await db.commit()
    
    async def get_portfolio(self) -> Portfolio:
        """Get user portfolio"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM portfolio WHERE user_id = 'default'") as cursor:
                row = await cursor.fetchone()
                if row:
                    holdings = json.loads(row[1]) if row[1] else []
                    return Portfolio(
                        holdings=holdings,
                        total_value=row[2],
                        total_pnl=row[3],
                        last_updated=datetime.fromisoformat(row[4]) if row[4] else None
                    )
                else:
                    return Portfolio()
    
    async def update_portfolio(self, portfolio: Portfolio):
        """Update user portfolio"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO portfolio (user_id, holdings, total_value, total_pnl, last_updated)
                VALUES ('default', ?, ?, ?, ?)
            """, (
                json.dumps(portfolio.holdings),
                portfolio.total_value,
                portfolio.total_pnl,
                datetime.now()
            ))
            await db.commit()
    
    async def save_price_data(self, symbol: str, price: float, volume: float = None, market_cap: float = None):
        """Save price data for historical analysis"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO price_history (symbol, price, volume, market_cap)
                VALUES (?, ?, ?, ?)
            """, (symbol, price, volume, market_cap))
            await db.commit()
