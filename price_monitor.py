import asyncio
import logging
from typing import Dict, List, Set
from datetime import datetime, timedelta
import json
from services.crypto_service import CryptoService
from services.alert_service import AlertService
from database.db import Database

logger = logging.getLogger(__name__)

class PriceMonitor:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.alert_service = AlertService()
        self.db = Database()
        self.monitored_symbols: Set[str] = set()
        self.price_cache: Dict[str, Dict] = {}
        self.is_running = False
        self.websocket_clients = []
        
    async def start_monitoring(self):
        """Start the price monitoring system"""
        self.is_running = True
        logger.info("Starting price monitoring system...")
        
        # Start monitoring tasks
        await asyncio.gather(
            self.price_update_loop(),
            self.volume_spike_detector(),
            self.pattern_detector(),
            self.market_sentiment_updater()
        )
    
    async def stop_monitoring(self):
        """Stop the price monitoring system"""
        self.is_running = False
        logger.info("Stopping price monitoring system...")
    
    async def add_symbol(self, symbol: str):
        """Add a symbol to monitoring"""
        self.monitored_symbols.add(symbol.upper())
        logger.info(f"Added {symbol} to monitoring")
    
    async def remove_symbol(self, symbol: str):
        """Remove a symbol from monitoring"""
        self.monitored_symbols.discard(symbol.upper())
        if symbol.upper() in self.price_cache:
            del self.price_cache[symbol.upper()]
        logger.info(f"Removed {symbol} from monitoring")
    
    async def price_update_loop(self):
        """Main price monitoring loop"""
        while self.is_running:
            try:
                # Get all symbols that need monitoring
                alerts = await self.alert_service.get_all_alerts()
                symbols_from_alerts = {alert.symbol for alert in alerts}
                
                # Combine with manually added symbols
                all_symbols = symbols_from_alerts.union(self.monitored_symbols)
                
                if all_symbols:
                    # Fetch current prices
                    prices = await self.crypto_service.get_multiple_prices(list(all_symbols))
                    
                    # Update cache and detect changes
                    for symbol, price_data in prices.items():
                        await self.process_price_update(symbol, price_data)
                    
                    # Check alerts
                    await self.check_alerts(prices)
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_price_updates(prices)
                
                # Wait before next update (configurable interval)
                await asyncio.sleep(10)  # 10 seconds
                
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def process_price_update(self, symbol: str, price_data: Dict):
        """Process a price update for a symbol"""
        current_price = price_data['current_price']
        
        # Check if this is a significant price change
        if symbol in self.price_cache:
            previous_price = self.price_cache[symbol]['current_price']
            price_change_pct = ((current_price - previous_price) / previous_price) * 100
            
            # Detect significant price movements (>5% change)
            if abs(price_change_pct) >= 5:
                await self.handle_significant_price_movement(symbol, price_change_pct, current_price)
        
        # Update cache
        self.price_cache[symbol] = {
            **price_data,
            'last_updated': datetime.now(),
            'price_history': self.price_cache.get(symbol, {}).get('price_history', [])
        }
        
        # Add to price history (keep last 100 points)
        self.price_cache[symbol]['price_history'].append({
            'price': current_price,
            'timestamp': datetime.now().isoformat(),
            'volume': price_data.get('volume_24h', 0)
        })
        
        # Keep only last 100 data points
        if len(self.price_cache[symbol]['price_history']) > 100:
            self.price_cache[symbol]['price_history'] = self.price_cache[symbol]['price_history'][-100:]
        
        # Save to database for historical analysis
        await self.db.save_price_data(
            symbol=symbol,
            price=current_price,
            volume=price_data.get('volume_24h'),
            market_cap=price_data.get('market_cap')
        )
    
    async def handle_significant_price_movement(self, symbol: str, price_change_pct: float, current_price: float):
        """Handle significant price movements"""
        direction = "up" if price_change_pct > 0 else "down"
        
        # Create automatic alert for significant movements
        movement_alert = {
            "type": "price_movement",
            "symbol": symbol,
            "price_change": price_change_pct,
            "current_price": current_price,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "message": f"🚨 {symbol} moved {direction} {abs(price_change_pct):.2f}% to ${current_price:.4f}"
        }
        
        # Broadcast to clients
        await self.broadcast_alert(movement_alert)
        
        logger.info(f"Significant price movement: {symbol} {direction} {abs(price_change_pct):.2f}%")
    
    async def volume_spike_detector(self):
        """Detect volume spikes that might indicate price movements"""
        while self.is_running:
            try:
                for symbol, data in self.price_cache.items():
                    if 'price_history' in data and len(data['price_history']) >= 10:
                        recent_volumes = [point['volume'] for point in data['price_history'][-10:]]
                        avg_volume = sum(recent_volumes) / len(recent_volumes)
                        current_volume = recent_volumes[-1]
                        
                        # Detect volume spike (>200% of average)
                        if current_volume > avg_volume * 2:
                            await self.handle_volume_spike(symbol, current_volume, avg_volume)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in volume spike detector: {e}")
                await asyncio.sleep(120)
    
    async def handle_volume_spike(self, symbol: str, current_volume: float, avg_volume: float):
        """Handle volume spike detection"""
        spike_ratio = current_volume / avg_volume
        
        volume_alert = {
            "type": "volume_spike",
            "symbol": symbol,
            "current_volume": current_volume,
            "average_volume": avg_volume,
            "spike_ratio": spike_ratio,
            "timestamp": datetime.now().isoformat(),
            "message": f"📊 Volume spike detected for {symbol}: {spike_ratio:.1f}x normal volume"
        }
        
        await self.broadcast_alert(volume_alert)
        logger.info(f"Volume spike detected: {symbol} - {spike_ratio:.1f}x normal volume")
    
    async def pattern_detector(self):
        """Detect technical analysis patterns"""
        while self.is_running:
            try:
                for symbol, data in self.price_cache.items():
                    if 'price_history' in data and len(data['price_history']) >= 20:
                        patterns = await self.detect_technical_patterns(symbol, data['price_history'])
                        
                        for pattern in patterns:
                            await self.handle_pattern_detection(symbol, pattern)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in pattern detector: {e}")
                await asyncio.sleep(600)
    
    async def detect_technical_patterns(self, symbol: str, price_history: List[Dict]) -> List[Dict]:
        """Detect technical patterns in price data"""
        patterns = []
        prices = [float(point['price']) for point in price_history]
        
        # Simple moving average crossover
        if len(prices) >= 20:
            sma_5 = sum(prices[-5:]) / 5
            sma_20 = sum(prices[-20:]) / 20
            prev_sma_5 = sum(prices[-6:-1]) / 5
            prev_sma_20 = sum(prices[-21:-1]) / 20
            
            # Golden cross (bullish)
            if sma_5 > sma_20 and prev_sma_5 <= prev_sma_20:
                patterns.append({
                    "pattern": "Golden Cross",
                    "type": "bullish",
                    "confidence": 0.7,
                    "description": "5-day MA crossed above 20-day MA"
                })
            
            # Death cross (bearish)
            elif sma_5 < sma_20 and prev_sma_5 >= prev_sma_20:
                patterns.append({
                    "pattern": "Death Cross",
                    "type": "bearish",
                    "confidence": 0.7,
                    "description": "5-day MA crossed below 20-day MA"
                })
        
        # Support/Resistance levels
        if len(prices) >= 10:
            recent_high = max(prices[-10:])
            recent_low = min(prices[-10:])
            current_price = prices[-1]
            
            # Near resistance
            if current_price >= recent_high * 0.98:
                patterns.append({
                    "pattern": "Near Resistance",
                    "type": "neutral",
                    "confidence": 0.6,
                    "description": f"Price near resistance level at ${recent_high:.4f}"
                })
            
            # Near support
            elif current_price <= recent_low * 1.02:
                patterns.append({
                    "pattern": "Near Support",
                    "type": "neutral",
                    "confidence": 0.6,
                    "description": f"Price near support level at ${recent_low:.4f}"
                })
        
        return patterns
    
    async def handle_pattern_detection(self, symbol: str, pattern: Dict):
        """Handle technical pattern detection"""
        pattern_alert = {
            "type": "pattern_detection",
            "symbol": symbol,
            "pattern": pattern,
            "timestamp": datetime.now().isoformat(),
            "message": f"📈 Pattern detected for {symbol}: {pattern['pattern']} ({pattern['type']})"
        }
        
        await self.broadcast_alert(pattern_alert)
        logger.info(f"Pattern detected: {symbol} - {pattern['pattern']}")
    
    async def market_sentiment_updater(self):
        """Update market sentiment periodically"""
        while self.is_running:
            try:
                from services.ai_service import AIService
                ai_service = AIService()
                
                sentiment = await ai_service.get_market_sentiment()
                
                # Broadcast sentiment update
                sentiment_update = {
                    "type": "market_sentiment",
                    "sentiment": sentiment,
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.broadcast_update(sentiment_update)
                
                await asyncio.sleep(1800)  # Update every 30 minutes
                
            except Exception as e:
                logger.error(f"Error updating market sentiment: {e}")
                await asyncio.sleep(3600)  # Wait longer on error
    
    async def check_alerts(self, prices: Dict):
        """Check if any alerts should be triggered"""
        alerts = await self.alert_service.get_all_alerts()
        
        for alert in alerts:
            if alert.symbol in prices:
                current_price = prices[alert.symbol]['current_price']
                
                should_trigger = False
                if alert.condition == "above" and current_price >= alert.target_price:
                    should_trigger = True
                elif alert.condition == "below" and current_price <= alert.target_price:
                    should_trigger = True
                
                if should_trigger:
                    await self.alert_service.trigger_alert(alert, current_price)
                    
                    # Create enhanced alert with chart data
                    enhanced_alert = await self.create_enhanced_alert(alert, current_price)
                    await self.broadcast_alert(enhanced_alert)
    
    async def create_enhanced_alert(self, alert, current_price: float) -> Dict:
        """Create an enhanced alert with additional context"""
        symbol = alert.symbol
        
        # Get recent price history for mini chart
        chart_data = []
        if symbol in self.price_cache and 'price_history' in self.price_cache[symbol]:
            chart_data = self.price_cache[symbol]['price_history'][-20:]  # Last 20 points
        
        # Calculate additional metrics
        price_change_24h = 0
        if symbol in self.price_cache:
            price_change_24h = self.price_cache[symbol].get('price_change_24h', 0)
        
        return {
            "type": "price_alert",
            "alert_id": alert.id,
            "symbol": symbol,
            "condition": alert.condition,
            "target_price": alert.target_price,
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "chart_data": chart_data,
            "timestamp": datetime.now().isoformat(),
            "message": f"🎯 Alert triggered: {symbol} {alert.condition} ${alert.target_price}! Current: ${current_price:.4f}"
        }
    
    async def broadcast_price_updates(self, prices: Dict):
        """Broadcast price updates to WebSocket clients"""
        update = {
            "type": "price_update",
            "prices": prices,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_update(update)
    
    async def broadcast_alert(self, alert: Dict):
        """Broadcast alert to WebSocket clients"""
        await self.broadcast_update(alert)
    
    async def broadcast_update(self, update: Dict):
        """Broadcast update to all WebSocket clients"""
        if self.websocket_clients:
            message = json.dumps(update)
            for client in self.websocket_clients[:]:  # Copy list to avoid modification during iteration
                try:
                    await client.send_text(message)
                except:
                    # Remove disconnected clients
                    self.websocket_clients.remove(client)
    
    def add_websocket_client(self, websocket):
        """Add a WebSocket client"""
        self.websocket_clients.append(websocket)
    
    def remove_websocket_client(self, websocket):
        """Remove a WebSocket client"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
    
    async def get_price_summary(self) -> Dict:
        """Get summary of all monitored prices"""
        return {
            "monitored_symbols": list(self.monitored_symbols),
            "price_cache": self.price_cache,
            "last_updated": datetime.now().isoformat(),
            "total_symbols": len(self.price_cache)
        }
