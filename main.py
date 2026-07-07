from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uvicorn

from services.crypto_service import CryptoService
from services.alert_service import AlertService
from services.ai_service import AIService
from services.smart_alert_engine import SmartAlertEngine
from services.price_monitor import PriceMonitor
from services.notification_service import NotificationService
from models.models import Alert, PriceData, Portfolio
from database.db import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Crypto Price Alert Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
crypto_service = CryptoService()
alert_service = AlertService()
ai_service = AIService()
smart_alert_engine = SmartAlertEngine()
price_monitor = PriceMonitor()
notification_service = NotificationService()
db = Database()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    await db.init_db()
    
    asyncio.create_task(smart_alert_engine.start_engine())
    asyncio.create_task(price_monitor.start_monitoring())
    
    logger.info("Crypto Alert Assistant with Smart AI Features started successfully!")

@app.get("/")
async def root():
    return {"message": "Crypto Price Alert Assistant API", "status": "running"}

@app.get("/api/coins")
async def get_supported_coins():
    """Get list of supported cryptocurrencies"""
    return await crypto_service.get_supported_coins()

@app.get("/api/price/{symbol}")
async def get_current_price(symbol: str):
    """Get current price for a cryptocurrency"""
    price_data = await crypto_service.get_current_price(symbol)
    return price_data

@app.get("/api/prices")
async def get_multiple_prices(symbols: str):
    """Get current prices for multiple cryptocurrencies"""
    symbol_list = symbols.split(",")
    prices = await crypto_service.get_multiple_prices(symbol_list)
    return prices

@app.get("/api/chart/{symbol}")
async def get_chart_data(symbol: str, days: int = 7):
    """Get historical chart data"""
    chart_data = await crypto_service.get_chart_data(symbol, days)
    return chart_data

@app.post("/api/alerts")
async def create_alert(alert: Alert):
    """Create a new price alert"""
    alert_id = await alert_service.create_alert(alert)
    return {"alert_id": alert_id, "message": "Alert created successfully"}

@app.get("/api/alerts")
async def get_alerts():
    """Get all active alerts"""
    alerts = await alert_service.get_all_alerts()
    return alerts

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert"""
    await alert_service.delete_alert(alert_id)
    return {"message": "Alert deleted successfully"}

@app.get("/api/market-sentiment")
async def get_market_sentiment():
    """Get AI-powered market sentiment analysis"""
    sentiment = await ai_service.get_market_sentiment()
    return sentiment

@app.get("/api/predictions/{symbol}")
async def get_price_predictions(symbol: str):
    """Get AI price predictions for a cryptocurrency"""
    predictions = await ai_service.get_price_predictions(symbol)
    return predictions

@app.get("/api/portfolio")
async def get_portfolio():
    """Get user portfolio"""
    portfolio = await db.get_portfolio()
    return portfolio

@app.post("/api/portfolio")
async def update_portfolio(portfolio: Portfolio):
    """Update user portfolio"""
    await db.update_portfolio(portfolio)
    return {"message": "Portfolio updated successfully"}

@app.post("/api/smart-alerts")
async def create_smart_alert(alert_data: dict):
    """Create a new smart alert with AI-enhanced conditions"""
    alert_id = await smart_alert_engine.create_smart_alert(
        symbol=alert_data["symbol"],
        alert_type=alert_data["type"],
        parameters=alert_data["parameters"]
    )
    return {"alert_id": alert_id, "message": "Smart alert created successfully"}

@app.get("/api/smart-alerts")
async def get_smart_alerts():
    """Get all active smart alerts"""
    alerts = await smart_alert_engine.get_active_alerts()
    return alerts

@app.delete("/api/smart-alerts/{alert_id}")
async def delete_smart_alert(alert_id: str):
    """Delete a smart alert"""
    await smart_alert_engine.delete_smart_alert(alert_id)
    return {"message": "Smart alert deleted successfully"}

@app.get("/api/engine-status")
async def get_engine_status():
    """Get smart alert engine status"""
    return smart_alert_engine.get_engine_status()

@app.get("/api/market-context/{symbol}")
async def get_market_context(symbol: str):
    """Get market context for a symbol"""
    context = await smart_alert_engine.get_market_context(symbol)
    return context

@app.post("/api/notifications/configure")
async def configure_notifications(config: dict):
    """Configure notification settings"""
    if "email" in config:
        email_config = config["email"]
        notification_service.configure_email(
            smtp_server=email_config.get("smtp_server", "smtp.gmail.com"),
            smtp_port=email_config.get("smtp_port", 587),
            username=email_config["username"],
            password=email_config["password"],
            from_email=email_config["from_email"]
        )
    
    if "webhooks" in config:
        for webhook_type, url in config["webhooks"].items():
            notification_service.configure_webhook(webhook_type, url)
    
    return {"message": "Notification configuration updated"}

@app.get("/api/notifications/status")
async def get_notification_status():
    """Get notification system status"""
    return notification_service.get_notification_status()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    price_monitor.add_websocket_client(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        price_monitor.remove_websocket_client(websocket)

async def price_monitoring_task():
    """Background task to monitor prices and trigger alerts"""
    while True:
        try:
            # Get all active alerts
            alerts = await alert_service.get_all_alerts()
            
            # Get current prices for all monitored coins
            symbols = list(set([alert.symbol for alert in alerts]))
            if symbols:
                prices = await crypto_service.get_multiple_prices(symbols)
                
                # Check each alert
                for alert in alerts:
                    if alert.symbol in prices:
                        current_price = prices[alert.symbol]['current_price']
                        
                        # Check if alert should trigger
                        should_trigger = False
                        if alert.condition == "above" and current_price >= alert.target_price:
                            should_trigger = True
                        elif alert.condition == "below" and current_price <= alert.target_price:
                            should_trigger = True
                        
                        if should_trigger:
                            # Trigger alert
                            await alert_service.trigger_alert(alert, current_price)
                            
                            # Broadcast to WebSocket clients
                            await manager.broadcast({
                                "type": "alert_triggered",
                                "alert": alert.dict(),
                                "current_price": current_price,
                                "timestamp": datetime.now().isoformat()
                            })
                
                # Broadcast current prices
                await manager.broadcast({
                    "type": "price_update",
                    "prices": prices,
                    "timestamp": datetime.now().isoformat()
                })
            
            await asyncio.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in price monitoring task: {e}")
            await asyncio.sleep(30)  # Wait longer on error

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
