import os
import requests
import time
import logging
from typing import Dict, Optional

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class NobitexAPI:
    """Client for interacting with Nobitex exchange API"""
    
    def __init__(self):
        self.base_url = os.getenv("NOBITEX_BASE_URL")
        self.rate_limit = int(os.getenv("NOBITEX_RATE_LIMIT"))
        self.last_request_time = 0
        self.request_count = 0
        self.minute_start = time.time()
    
    def _rate_limit_check(self):
        """Ensure we don't exceed the rate limit of 60 requests per minute"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.minute_start >= 60:
            self.request_count = 0
            self.minute_start = current_time
        print(self.rate_limit)
        # If we've hit the limit, wait until the next minute
        if self.request_count >= self.rate_limit:
            wait_time = 60 - (current_time - self.minute_start)
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                self.request_count = 0
                self.minute_start = time.time()
        
        # Ensure minimum time between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1:  # Minimum 1 second between requests
            time.sleep(1 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_trades(self, symbol: str) -> Optional[Dict]:
        """
        Get latest trades for a given symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCIRT')
            
        Returns:
            Dictionary containing trades data or None if error
        """
        self._rate_limit_check()
        
        url = f"{self.base_url}/v2/trades/{symbol}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "ok":
                return data
            else:
                logger.error(f"Nobitex API error for {symbol}: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {symbol}: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON decode error for {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol from the most recent trade
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Latest price as float or None if error
        """
        trades_data = self.get_trades(symbol)
        
        if not trades_data or not trades_data.get("trades"):
            return None
        
        trades = trades_data["trades"]
        if not trades:
            return None
        
        # Get the most recent trade (first in the list)
        latest_trade = trades[0]
        try:
            return float(latest_trade["price"])
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing price for {symbol}: {e}")
            return None
    
    def get_buy_sell_prices(self, symbol: str) -> Dict[str, Optional[float]]:
        """
        Get separate buy and sell prices from recent trades
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary with 'buy' and 'sell' prices
        """
        trades_data = self.get_trades(symbol)
        
        if not trades_data or not trades_data.get("trades"):
            return {"buy": None, "sell": None}
        
        trades = trades_data["trades"]
        buy_prices = []
        sell_prices = []
        
        # Collect recent buy and sell prices
        for trade in trades[:10]:  # Look at last 10 trades
            try:
                price = float(trade["price"])
                if trade["type"] == "buy":
                    buy_prices.append(price)
                elif trade["type"] == "sell":
                    sell_prices.append(price)
            except (ValueError, KeyError):
                continue
        
        return {
            "buy": max(buy_prices) if buy_prices else None,
            "sell": min(sell_prices) if sell_prices else None
        }

