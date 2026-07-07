import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_supported_coins(self) -> List[Dict]:
        """Get list of supported cryptocurrencies from CoinGecko"""
        try:
            session = await self.get_session()
            url = f"{self.coingecko_base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": False
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "id": coin["id"],
                            "symbol": coin["symbol"].upper(),
                            "name": coin["name"],
                            "image": coin["image"],
                            "market_cap_rank": coin["market_cap_rank"]
                        }
                        for coin in data
                    ]
                else:
                    logger.error(f"Failed to fetch supported coins: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching supported coins: {e}")
            return []
    
    async def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current price data for a single cryptocurrency"""
        try:
            session = await self.get_session()
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd",
                "include_24hr_change": True,
                "include_24hr_vol": True,
                "include_market_cap": True
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if symbol.lower() in data:
                        coin_data = data[symbol.lower()]
                        return {
                            "symbol": symbol.upper(),
                            "current_price": coin_data.get("usd", 0),
                            "price_change_24h": coin_data.get("usd_24h_change", 0),
                            "volume_24h": coin_data.get("usd_24h_vol", 0),
                            "market_cap": coin_data.get("usd_market_cap", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict:
        """Get current prices for multiple cryptocurrencies"""
        try:
            session = await self.get_session()
            ids = ",".join([symbol.lower() for symbol in symbols])
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                "ids": ids,
                "vs_currencies": "usd",
                "include_24hr_change": True,
                "include_24hr_vol": True,
                "include_market_cap": True
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {}
                    for symbol in symbols:
                        if symbol.lower() in data:
                            coin_data = data[symbol.lower()]
                            result[symbol.upper()] = {
                                "current_price": coin_data.get("usd", 0),
                                "price_change_24h": coin_data.get("usd_24h_change", 0),
                                "volume_24h": coin_data.get("usd_24h_vol", 0),
                                "market_cap": coin_data.get("usd_market_cap", 0),
                                "timestamp": datetime.now().isoformat()
                            }
                    return result
                return {}
        except Exception as e:
            logger.error(f"Error fetching multiple prices: {e}")
            return {}
    
    async def get_chart_data(self, symbol: str, days: int = 7) -> Dict:
        """Get historical chart data for a cryptocurrency"""
        try:
            session = await self.get_session()
            url = f"{self.coingecko_base_url}/coins/{symbol.lower()}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "hourly" if days <= 7 else "daily"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Format data for charts
                    prices = []
                    volumes = []
                    
                    for price_point in data.get("prices", []):
                        prices.append({
                            "timestamp": price_point[0],
                            "price": price_point[1],
                            "date": datetime.fromtimestamp(price_point[0] / 1000).isoformat()
                        })
                    
                    for volume_point in data.get("total_volumes", []):
                        volumes.append({
                            "timestamp": volume_point[0],
                            "volume": volume_point[1],
                            "date": datetime.fromtimestamp(volume_point[0] / 1000).isoformat()
                        })
                    
                    return {
                        "symbol": symbol.upper(),
                        "prices": prices,
                        "volumes": volumes,
                        "days": days
                    }
                return {}
        except Exception as e:
            logger.error(f"Error fetching chart data for {symbol}: {e}")
            return {}
    
    async def get_fear_greed_index(self) -> Dict:
        """Get Fear & Greed Index data"""
        try:
            session = await self.get_session()
            url = "https://api.alternative.me/fng/"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data"):
                        latest = data["data"][0]
                        return {
                            "value": int(latest["value"]),
                            "classification": latest["value_classification"],
                            "timestamp": latest["timestamp"],
                            "time_until_update": latest.get("time_until_update")
                        }
                return {}
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return {}
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
