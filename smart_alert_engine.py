import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json

from services.ai_service import AIService
from services.crypto_service import CryptoService
from services.notification_service import NotificationService
from database.db import Database

logger = logging.getLogger(__name__)

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertCategory(Enum):
    PRICE = "price"
    VOLUME = "volume"
    PATTERN = "pattern"
    SENTIMENT = "sentiment"
    WHALE = "whale"
    ARBITRAGE = "arbitrage"
    DEFI = "defi"

@dataclass
class SmartAlert:
    id: str
    symbol: str
    category: AlertCategory
    priority: AlertPriority
    condition: str
    threshold: float
    current_value: float
    confidence: float
    message: str
    context: Dict
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True

class SmartAlertEngine:
    def __init__(self):
        self.ai_service = AIService()
        self.crypto_service = CryptoService()
        self.notification_service = NotificationService()
        self.db = Database()
        
        # Alert thresholds and configurations
        self.config = {
            "price_movement_threshold": 0.05,  # 5% price change
            "volume_spike_threshold": 2.0,     # 2x normal volume
            "sentiment_change_threshold": 20,   # 20 point sentiment change
            "pattern_confidence_threshold": 0.7, # 70% confidence
            "whale_transaction_threshold": 1000000,  # $1M transaction
            "arbitrage_opportunity_threshold": 0.02  # 2% price difference
        }
        
        # Active smart alerts
        self.active_alerts: Dict[str, SmartAlert] = {}
        
        # Market context cache
        self.market_context = {
            "fear_greed_index": 50,
            "overall_sentiment": "neutral",
            "market_trend": "sideways",
            "volatility_level": "normal"
        }
    
    async def start_engine(self):
        """Start the smart alert engine"""
        logger.info("Starting Smart Alert Engine...")
        
        # Start background tasks
        await asyncio.gather(
            self.sentiment_monitor(),
            self.whale_tracker(),
            self.arbitrage_scanner(),
            self.defi_monitor(),
            self.pattern_analyzer(),
            self.market_context_updater()
        )
    
    async def create_smart_alert(self, symbol: str, alert_type: str, parameters: Dict) -> str:
        """Create a new smart alert with AI-enhanced conditions"""
        try:
            # Get current market context
            context = await self.get_market_context(symbol)
            
            # Generate smart conditions based on AI analysis
            smart_conditions = await self.generate_smart_conditions(symbol, alert_type, parameters, context)
            
            # Create enhanced alert
            alert = SmartAlert(
                id=f"smart_{datetime.now().timestamp()}",
                symbol=symbol,
                category=AlertCategory(alert_type),
                priority=smart_conditions["priority"],
                condition=smart_conditions["condition"],
                threshold=smart_conditions["threshold"],
                current_value=smart_conditions["current_value"],
                confidence=smart_conditions["confidence"],
                message=smart_conditions["message"],
                context=context,
                created_at=datetime.now(),
                expires_at=smart_conditions.get("expires_at")
            )
            
            # Store alert
            self.active_alerts[alert.id] = alert
            await self.db.save_smart_alert(alert)
            
            logger.info(f"Created smart alert {alert.id} for {symbol}")
            return alert.id
            
        except Exception as e:
            logger.error(f"Error creating smart alert: {e}")
            raise
    
    async def generate_smart_conditions(self, symbol: str, alert_type: str, parameters: Dict, context: Dict) -> Dict:
        """Generate intelligent alert conditions using AI"""
        
        if alert_type == "price":
            return await self.generate_price_conditions(symbol, parameters, context)
        elif alert_type == "volume":
            return await self.generate_volume_conditions(symbol, parameters, context)
        elif alert_type == "sentiment":
            return await self.generate_sentiment_conditions(symbol, parameters, context)
        elif alert_type == "pattern":
            return await self.generate_pattern_conditions(symbol, parameters, context)
        else:
            # Default conditions
            return {
                "condition": parameters.get("condition", "above"),
                "threshold": parameters.get("threshold", 0),
                "current_value": 0,
                "confidence": 0.5,
                "priority": AlertPriority.MEDIUM,
                "message": f"Smart alert for {symbol}"
            }
    
    async def generate_price_conditions(self, symbol: str, parameters: Dict, context: Dict) -> Dict:
        """Generate smart price alert conditions"""
        # Get current price and predictions
        current_price_data = await self.crypto_service.get_current_price(symbol)
        predictions = await self.ai_service.get_price_predictions(symbol)
        
        current_price = current_price_data["current_price"]
        target_price = parameters.get("target_price", current_price)
        
        # Adjust conditions based on market context and predictions
        confidence = 0.6
        priority = AlertPriority.MEDIUM
        
        # Increase confidence if predictions align
        if predictions:
            short_term = predictions.get("predictions", {}).get("short_term", {})
            if short_term:
                pred_direction = short_term.get("direction")
                condition = parameters.get("condition", "above")
                
                if (condition == "above" and pred_direction == "up") or \
                   (condition == "below" and pred_direction == "down"):
                    confidence = min(0.9, confidence + short_term.get("confidence", 0))
                    priority = AlertPriority.HIGH
        
        # Adjust based on market sentiment
        sentiment_score = context.get("sentiment_score", 50)
        if sentiment_score > 70:  # Very bullish
            if parameters.get("condition") == "above":
                confidence += 0.1
                priority = AlertPriority.HIGH
        elif sentiment_score < 30:  # Very bearish
            if parameters.get("condition") == "below":
                confidence += 0.1
                priority = AlertPriority.HIGH
        
        # Adjust based on volatility
        volatility = context.get("volatility", "normal")
        if volatility == "high":
            priority = AlertPriority.HIGH
        
        return {
            "condition": parameters.get("condition", "above"),
            "threshold": target_price,
            "current_value": current_price,
            "confidence": min(0.95, confidence),
            "priority": priority,
            "message": f"Smart price alert: {symbol} {parameters.get('condition', 'above')} ${target_price:.4f} (AI confidence: {confidence:.0%})"
        }
    
    async def generate_volume_conditions(self, symbol: str, parameters: Dict, context: Dict) -> Dict:
        """Generate smart volume alert conditions"""
        # Get historical volume data
        chart_data = await self.crypto_service.get_chart_data(symbol, days=7)
        
        if chart_data and "volumes" in chart_data:
            volumes = [v["volume"] for v in chart_data["volumes"]]
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            current_volume = volumes[-1] if volumes else 0
            
            # Smart threshold based on historical patterns
            threshold_multiplier = parameters.get("multiplier", 2.0)
            
            # Adjust based on market conditions
            if context.get("market_trend") == "volatile":
                threshold_multiplier *= 0.8  # Lower threshold in volatile markets
            
            threshold = avg_volume * threshold_multiplier
            confidence = 0.7 if current_volume > threshold * 0.8 else 0.5
            
            return {
                "condition": "spike",
                "threshold": threshold,
                "current_value": current_volume,
                "confidence": confidence,
                "priority": AlertPriority.MEDIUM if confidence > 0.6 else AlertPriority.LOW,
                "message": f"Smart volume alert: {symbol} volume spike above {threshold_multiplier}x average"
            }
        
        return {
            "condition": "spike",
            "threshold": 0,
            "current_value": 0,
            "confidence": 0.3,
            "priority": AlertPriority.LOW,
            "message": f"Volume alert for {symbol} (insufficient data)"
        }
    
    async def generate_sentiment_conditions(self, symbol: str, parameters: Dict, context: Dict) -> Dict:
        """Generate smart sentiment alert conditions"""
        current_sentiment = context.get("sentiment_score", 50)
        target_sentiment = parameters.get("target_sentiment", 70)
        
        # Calculate confidence based on sentiment momentum
        sentiment_history = context.get("sentiment_history", [current_sentiment])
        if len(sentiment_history) >= 3:
            momentum = sentiment_history[-1] - sentiment_history[-3]
            confidence = 0.6 + min(0.3, abs(momentum) / 50)
        else:
            confidence = 0.5
        
        # Determine priority based on sentiment extremes
        if target_sentiment > 80 or target_sentiment < 20:
            priority = AlertPriority.HIGH
        else:
            priority = AlertPriority.MEDIUM
        
        return {
            "condition": "above" if target_sentiment > current_sentiment else "below",
            "threshold": target_sentiment,
            "current_value": current_sentiment,
            "confidence": confidence,
            "priority": priority,
            "message": f"Smart sentiment alert: {symbol} sentiment {'above' if target_sentiment > current_sentiment else 'below'} {target_sentiment}"
        }
    
    async def generate_pattern_conditions(self, symbol: str, parameters: Dict, context: Dict) -> Dict:
        """Generate smart pattern alert conditions"""
        pattern_type = parameters.get("pattern_type", "any")
        min_confidence = parameters.get("min_confidence", 0.7)
        
        # Get current technical analysis
        chart_data = await self.crypto_service.get_chart_data(symbol, days=30)
        patterns = await self.ai_service.detect_patterns(chart_data.get("prices", []))
        
        current_patterns = patterns.get("patterns", [])
        max_confidence = max([p.get("confidence", 0) for p in current_patterns], default=0)
        
        return {
            "condition": "detected",
            "threshold": min_confidence,
            "current_value": max_confidence,
            "confidence": max_confidence,
            "priority": AlertPriority.HIGH if max_confidence > 0.8 else AlertPriority.MEDIUM,
            "message": f"Smart pattern alert: {symbol} {pattern_type} pattern with {min_confidence:.0%}+ confidence"
        }
    
    async def sentiment_monitor(self):
        """Monitor market sentiment changes"""
        while True:
            try:
                # Get overall market sentiment
                sentiment = await self.ai_service.get_market_sentiment()
                current_score = sentiment.get("overall_score", 50)
                
                # Check for significant sentiment changes
                previous_score = self.market_context.get("sentiment_score", 50)
                change = abs(current_score - previous_score)
                
                if change >= self.config["sentiment_change_threshold"]:
                    await self.trigger_sentiment_alerts(current_score, previous_score)
                
                # Update market context
                self.market_context.update({
                    "sentiment_score": current_score,
                    "sentiment_classification": sentiment.get("sentiment", "neutral"),
                    "sentiment_change": current_score - previous_score
                })
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in sentiment monitor: {e}")
                await asyncio.sleep(3600)
    
    async def whale_tracker(self):
        """Track whale movements and large transactions"""
        while True:
            try:
                # In a real implementation, you'd connect to blockchain APIs
                # For demo, we'll simulate whale detection
                
                # Simulate whale transaction detection
                import random
                if random.random() < 0.1:  # 10% chance of whale activity
                    symbol = random.choice(["bitcoin", "ethereum", "cardano"])
                    amount = random.uniform(1000000, 50000000)  # $1M - $50M
                    
                    await self.handle_whale_activity(symbol, amount)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in whale tracker: {e}")
                await asyncio.sleep(600)
    
    async def arbitrage_scanner(self):
        """Scan for arbitrage opportunities across exchanges"""
        while True:
            try:
                # In a real implementation, you'd check multiple exchanges
                # For demo, we'll simulate arbitrage opportunities
                
                symbols = ["bitcoin", "ethereum", "cardano", "solana"]
                
                for symbol in symbols:
                    # Simulate price differences between exchanges
                    import random
                    price_diff = random.uniform(-0.05, 0.05)  # -5% to +5%
                    
                    if abs(price_diff) >= self.config["arbitrage_opportunity_threshold"]:
                        await self.handle_arbitrage_opportunity(symbol, price_diff)
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in arbitrage scanner: {e}")
                await asyncio.sleep(1200)
    
    async def defi_monitor(self):
        """Monitor DeFi protocols for yield farming opportunities"""
        while True:
            try:
                # In a real implementation, you'd connect to DeFi protocols
                # For demo, we'll simulate DeFi monitoring
                
                protocols = ["Uniswap", "Compound", "Aave", "Curve"]
                
                for protocol in protocols:
                    # Simulate APY changes
                    import random
                    apy_change = random.uniform(-10, 10)  # -10% to +10% APY change
                    
                    if abs(apy_change) >= 5:  # 5% APY change threshold
                        await self.handle_defi_opportunity(protocol, apy_change)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in DeFi monitor: {e}")
                await asyncio.sleep(7200)
    
    async def pattern_analyzer(self):
        """Analyze technical patterns across monitored symbols"""
        while True:
            try:
                # Get all monitored symbols
                symbols = list(self.active_alerts.keys())
                
                for alert_id, alert in self.active_alerts.items():
                    if alert.category == AlertCategory.PATTERN and alert.is_active:
                        # Get latest chart data
                        chart_data = await self.crypto_service.get_chart_data(alert.symbol, days=7)
                        
                        if chart_data:
                            patterns = await self.ai_service.detect_patterns(chart_data.get("prices", []))
                            
                            # Check if pattern conditions are met
                            for pattern in patterns.get("patterns", []):
                                if pattern.get("confidence", 0) >= alert.threshold:
                                    await self.trigger_pattern_alert(alert, pattern)
                
                await asyncio.sleep(900)  # Check every 15 minutes
                
            except Exception as e:
                logger.error(f"Error in pattern analyzer: {e}")
                await asyncio.sleep(1800)
    
    async def market_context_updater(self):
        """Update market context regularly"""
        while True:
            try:
                # Update Fear & Greed Index
                fear_greed = await self.crypto_service.get_fear_greed_index()
                if fear_greed:
                    self.market_context["fear_greed_index"] = fear_greed.get("value", 50)
                
                # Update overall market trend
                # In a real implementation, you'd analyze major cryptocurrencies
                btc_data = await self.crypto_service.get_current_price("bitcoin")
                if btc_data:
                    change_24h = btc_data.get("price_change_24h", 0)
                    if change_24h > 5:
                        self.market_context["market_trend"] = "bullish"
                    elif change_24h < -5:
                        self.market_context["market_trend"] = "bearish"
                    else:
                        self.market_context["market_trend"] = "sideways"
                    
                    # Determine volatility level
                    if abs(change_24h) > 10:
                        self.market_context["volatility_level"] = "high"
                    elif abs(change_24h) > 5:
                        self.market_context["volatility_level"] = "medium"
                    else:
                        self.market_context["volatility_level"] = "low"
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Error updating market context: {e}")
                await asyncio.sleep(7200)
    
    async def get_market_context(self, symbol: str) -> Dict:
        """Get current market context for a symbol"""
        try:
            # Get symbol-specific data
            price_data = await self.crypto_service.get_current_price(symbol)
            chart_data = await self.crypto_service.get_chart_data(symbol, days=7)
            
            # Calculate volatility
            if chart_data and "prices" in chart_data:
                prices = [p["price"] for p in chart_data["prices"]]
                if len(prices) > 1:
                    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                    volatility = np.std(returns) * np.sqrt(24)  # Annualized volatility
                else:
                    volatility = 0
            else:
                volatility = 0
            
            context = {
                **self.market_context,
                "symbol": symbol,
                "current_price": price_data.get("current_price", 0) if price_data else 0,
                "price_change_24h": price_data.get("price_change_24h", 0) if price_data else 0,
                "volatility": volatility,
                "timestamp": datetime.now().isoformat()
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting market context for {symbol}: {e}")
            return {**self.market_context, "symbol": symbol}
    
    async def trigger_sentiment_alerts(self, current_score: float, previous_score: float):
        """Trigger alerts for significant sentiment changes"""
        change = current_score - previous_score
        direction = "increased" if change > 0 else "decreased"
        
        alert_data = {
            "type": "sentiment_change",
            "current_score": current_score,
            "previous_score": previous_score,
            "change": change,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "message": f"Market sentiment {direction} by {abs(change):.1f} points to {current_score:.1f}"
        }
        
        await self.notification_service.send_alert_notification(alert_data)
        logger.info(f"Sentiment alert triggered: {direction} by {abs(change):.1f} points")
    
    async def handle_whale_activity(self, symbol: str, amount: float):
        """Handle detected whale activity"""
        alert_data = {
            "type": "whale_activity",
            "symbol": symbol,
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "message": f"Whale activity detected: ${amount:,.0f} transaction in {symbol.upper()}"
        }
        
        await self.notification_service.send_alert_notification(alert_data)
        logger.info(f"Whale activity detected: {symbol} - ${amount:,.0f}")
    
    async def handle_arbitrage_opportunity(self, symbol: str, price_diff: float):
        """Handle arbitrage opportunity"""
        direction = "higher" if price_diff > 0 else "lower"
        
        alert_data = {
            "type": "arbitrage_opportunity",
            "symbol": symbol,
            "price_difference": price_diff,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "message": f"Arbitrage opportunity: {symbol.upper()} is {abs(price_diff):.2%} {direction} on one exchange"
        }
        
        await self.notification_service.send_alert_notification(alert_data)
        logger.info(f"Arbitrage opportunity: {symbol} - {abs(price_diff):.2%} difference")
    
    async def handle_defi_opportunity(self, protocol: str, apy_change: float):
        """Handle DeFi yield farming opportunity"""
        direction = "increased" if apy_change > 0 else "decreased"
        
        alert_data = {
            "type": "defi_opportunity",
            "protocol": protocol,
            "apy_change": apy_change,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "message": f"DeFi opportunity: {protocol} APY {direction} by {abs(apy_change):.1f}%"
        }
        
        await self.notification_service.send_alert_notification(alert_data)
        logger.info(f"DeFi opportunity: {protocol} - APY {direction} by {abs(apy_change):.1f}%")
    
    async def trigger_pattern_alert(self, alert: SmartAlert, pattern: Dict):
        """Trigger pattern detection alert"""
        alert_data = {
            "type": "pattern_detection",
            "symbol": alert.symbol,
            "pattern": pattern,
            "alert_id": alert.id,
            "timestamp": datetime.now().isoformat(),
            "message": f"Pattern detected: {alert.symbol.upper()} - {pattern.get('pattern', 'Unknown')} ({pattern.get('confidence', 0):.0%} confidence)"
        }
        
        await self.notification_service.send_alert_notification(alert_data)
        
        # Mark alert as triggered
        alert.is_active = False
        await self.db.update_smart_alert(alert)
        
        logger.info(f"Pattern alert triggered: {alert.symbol} - {pattern.get('pattern', 'Unknown')}")
    
    async def get_active_alerts(self) -> List[Dict]:
        """Get all active smart alerts"""
        return [
            {
                "id": alert.id,
                "symbol": alert.symbol,
                "category": alert.category.value,
                "priority": alert.priority.value,
                "condition": alert.condition,
                "threshold": alert.threshold,
                "current_value": alert.current_value,
                "confidence": alert.confidence,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
                "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
            }
            for alert in self.active_alerts.values()
            if alert.is_active
        ]
    
    async def delete_smart_alert(self, alert_id: str):
        """Delete a smart alert"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            await self.db.delete_smart_alert(alert_id)
            logger.info(f"Deleted smart alert {alert_id}")
    
    def get_engine_status(self) -> Dict:
        """Get smart alert engine status"""
        return {
            "active_alerts": len([a for a in self.active_alerts.values() if a.is_active]),
            "total_alerts": len(self.active_alerts),
            "market_context": self.market_context,
            "config": self.config,
            "last_updated": datetime.now().isoformat()
        }
