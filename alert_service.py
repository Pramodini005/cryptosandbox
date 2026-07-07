import uuid
from typing import List, Dict
from datetime import datetime
import logging
from models.models import Alert
from database.db import Database

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.db = Database()
        self.active_alerts: Dict[str, Alert] = {}
    
    async def create_alert(self, alert: Alert) -> str:
        """Create a new price alert"""
        alert_id = str(uuid.uuid4())
        alert.id = alert_id
        alert.created_at = datetime.now()
        alert.is_active = True
        
        # Store in database
        await self.db.save_alert(alert)
        
        # Keep in memory for fast access
        self.active_alerts[alert_id] = alert
        
        logger.info(f"Created alert {alert_id} for {alert.symbol} {alert.condition} ${alert.target_price}")
        return alert_id
    
    async def get_all_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        alerts = await self.db.get_all_alerts()
        return [alert for alert in alerts if alert.is_active]
    
    async def delete_alert(self, alert_id: str):
        """Delete an alert"""
        await self.db.delete_alert(alert_id)
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
        logger.info(f"Deleted alert {alert_id}")
    
    async def trigger_alert(self, alert: Alert, current_price: float):
        """Trigger an alert when conditions are met"""
        try:
            # Mark alert as triggered
            alert.is_active = False
            alert.triggered_at = datetime.now()
            alert.triggered_price = current_price
            
            # Update in database
            await self.db.update_alert(alert)
            
            # Remove from active alerts
            if alert.id in self.active_alerts:
                del self.active_alerts[alert.id]
            
            # Send notification (implement your preferred notification method)
            await self.send_notification(alert, current_price)
            
            logger.info(f"Triggered alert {alert.id}: {alert.symbol} reached ${current_price}")
            
        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {e}")
    
    async def send_notification(self, alert: Alert, current_price: float):
        """Send notification when alert is triggered"""
        # This is where you'd implement various notification methods
        # For now, we'll just log it
        
        message = f"🚨 CRYPTO ALERT: {alert.symbol} has {alert.condition} ${alert.target_price}! Current price: ${current_price:.4f}"
        
        # You can implement:
        # - Email notifications
        # - Push notifications
        # - Telegram bot messages
        # - Discord webhooks
        # - SMS via Twilio
        
        logger.info(f"Notification sent: {message}")
        
        # Store notification history
        await self.db.save_notification({
            "alert_id": alert.id,
            "message": message,
            "sent_at": datetime.now(),
            "type": "price_alert"
        })
