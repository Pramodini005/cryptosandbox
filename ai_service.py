import asyncio
import aiohttp
from typing import Dict, List
import logging
from datetime import datetime, timedelta
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_market_sentiment(self) -> Dict:
        """Get AI-powered market sentiment analysis"""
        try:
            # Combine multiple sentiment sources
            fear_greed = await self.get_fear_greed_sentiment()
            social_sentiment = await self.get_social_sentiment()
            news_sentiment = await self.get_news_sentiment()
            
            # Calculate overall sentiment score
            overall_score = (
                fear_greed.get("score", 50) * 0.4 +
                social_sentiment.get("score", 50) * 0.3 +
                news_sentiment.get("score", 50) * 0.3
            )
            
            sentiment_label = self.get_sentiment_label(overall_score)
            
            return {
                "overall_score": round(overall_score, 2),
                "sentiment": sentiment_label,
                "components": {
                    "fear_greed": fear_greed,
                    "social": social_sentiment,
                    "news": news_sentiment
                },
                "recommendation": self.get_sentiment_recommendation(overall_score),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {
                "overall_score": 50,
                "sentiment": "Neutral",
                "error": str(e)
            }
    
    async def get_fear_greed_sentiment(self) -> Dict:
        """Get Fear & Greed Index sentiment"""
        try:
            session = await self.get_session()
            url = "https://api.alternative.me/fng/"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data"):
                        latest = data["data"][0]
                        value = int(latest["value"])
                        return {
                            "score": value,
                            "classification": latest["value_classification"],
                            "source": "Fear & Greed Index"
                        }
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
        
        return {"score": 50, "classification": "Neutral", "source": "Fear & Greed Index"}
    
    async def get_social_sentiment(self) -> Dict:
        """Analyze social media sentiment (simplified version)"""
        # In a real implementation, you'd connect to Twitter API, Reddit API, etc.
        # For demo purposes, we'll simulate social sentiment
        
        # Simulate social sentiment based on recent market movements
        import random
        score = random.randint(20, 80)
        
        return {
            "score": score,
            "classification": self.get_sentiment_label(score),
            "source": "Social Media Analysis",
            "mentions": random.randint(1000, 10000),
            "positive_ratio": score / 100
        }
    
    async def get_news_sentiment(self) -> Dict:
        """Analyze crypto news sentiment"""
        # In a real implementation, you'd use news APIs and NLP
        # For demo purposes, we'll simulate news sentiment
        
        import random
        score = random.randint(30, 70)
        
        return {
            "score": score,
            "classification": self.get_sentiment_label(score),
            "source": "News Analysis",
            "articles_analyzed": random.randint(50, 200)
        }
    
    def get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 75:
            return "Extremely Bullish"
        elif score >= 60:
            return "Bullish"
        elif score >= 40:
            return "Neutral"
        elif score >= 25:
            return "Bearish"
        else:
            return "Extremely Bearish"
    
    def get_sentiment_recommendation(self, score: float) -> str:
        """Get trading recommendation based on sentiment"""
        if score >= 75:
            return "Strong buy signal - Market is very optimistic"
        elif score >= 60:
            return "Buy signal - Positive market sentiment"
        elif score >= 40:
            return "Hold - Neutral market conditions"
        elif score >= 25:
            return "Caution - Negative market sentiment"
        else:
            return "Strong caution - Very bearish market"
    
    async def get_price_predictions(self, symbol: str) -> Dict:
        """Get AI price predictions for a cryptocurrency"""
        try:
            # In a real implementation, you'd use machine learning models
            # For demo purposes, we'll create realistic-looking predictions
            
            import random
            
            # Simulate different prediction models
            predictions = {
                "short_term": {  # 24 hours
                    "direction": random.choice(["up", "down"]),
                    "confidence": random.uniform(0.6, 0.9),
                    "price_change": random.uniform(-0.15, 0.15),
                    "timeframe": "24 hours"
                },
                "medium_term": {  # 7 days
                    "direction": random.choice(["up", "down"]),
                    "confidence": random.uniform(0.5, 0.8),
                    "price_change": random.uniform(-0.3, 0.3),
                    "timeframe": "7 days"
                },
                "long_term": {  # 30 days
                    "direction": random.choice(["up", "down"]),
                    "confidence": random.uniform(0.4, 0.7),
                    "price_change": random.uniform(-0.5, 0.5),
                    "timeframe": "30 days"
                }
            }
            
            # Add technical indicators
            technical_analysis = {
                "rsi": random.uniform(20, 80),
                "macd_signal": random.choice(["bullish", "bearish", "neutral"]),
                "support_level": random.uniform(0.8, 0.95),
                "resistance_level": random.uniform(1.05, 1.2),
                "trend": random.choice(["uptrend", "downtrend", "sideways"])
            }
            
            return {
                "symbol": symbol.upper(),
                "predictions": predictions,
                "technical_analysis": technical_analysis,
                "model_accuracy": random.uniform(0.65, 0.85),
                "last_updated": datetime.now().isoformat(),
                "disclaimer": "Predictions are for educational purposes only. Not financial advice."
            }
            
        except Exception as e:
            logger.error(f"Error getting predictions for {symbol}: {e}")
            return {"error": str(e)}
    
    async def detect_patterns(self, price_data: List[Dict]) -> Dict:
        """Detect technical analysis patterns in price data"""
        try:
            if len(price_data) < 20:
                return {"patterns": [], "message": "Insufficient data for pattern detection"}
            
            prices = [float(point["price"]) for point in price_data]
            patterns = []
            
            # Simple pattern detection (in reality, you'd use more sophisticated algorithms)
            
            # Detect trend
            if prices[-1] > prices[-10]:
                if prices[-10] > prices[-20]:
                    patterns.append({
                        "pattern": "Strong Uptrend",
                        "confidence": 0.8,
                        "description": "Price showing consistent upward movement"
                    })
                else:
                    patterns.append({
                        "pattern": "Uptrend",
                        "confidence": 0.6,
                        "description": "Recent upward price movement"
                    })
            elif prices[-1] < prices[-10]:
                if prices[-10] < prices[-20]:
                    patterns.append({
                        "pattern": "Strong Downtrend",
                        "confidence": 0.8,
                        "description": "Price showing consistent downward movement"
                    })
                else:
                    patterns.append({
                        "pattern": "Downtrend",
                        "confidence": 0.6,
                        "description": "Recent downward price movement"
                    })
            
            # Detect volatility
            price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            avg_volatility = sum(price_changes) / len(price_changes)
            
            if avg_volatility > 0.05:
                patterns.append({
                    "pattern": "High Volatility",
                    "confidence": 0.9,
                    "description": f"Average price change: {avg_volatility:.2%}"
                })
            
            return {
                "patterns": patterns,
                "analysis_period": f"{len(price_data)} data points",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {"error": str(e)}
