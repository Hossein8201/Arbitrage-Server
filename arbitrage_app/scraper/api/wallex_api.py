import os
import requests
import time
import logging
from typing import Dict, Optional
from arbitrage_app.sample_trading import WALLEX_BASE_URL, WALLEX_RATE_LIMIT

logger = logging.getLogger(__name__)

class WallexAPI:
    """Client for interacting with Wallex exchange API"""
    
    def __init__(self):
        self.base_url = WALLEX_BASE_URL
        self.rate_limit = WALLEX_RATE_LIMIT
        self.last_request_time = 0
        self.request_count = 0
        self.minute_start = time.time()
    
    def _rate_limit_check(self):
        """Ensure we don't exceed the rate limit"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.minute_start >= 60:
            self.request_count = 0
            self.minute_start = current_time
        
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
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return headers
    
    def get_trades(self, symbol: str) -> Optional[Dict]:
        """
        Get latest trades for a given symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary containing trades data or None if error
        """
        self._rate_limit_check()
        
        url = f"{self.base_url}/v1/trades"
        params = {"symbol": symbol}
        headers = self._get_headers()
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success") == True:
                return data
            else:
                logger.error(f"Wallex API error for {symbol}: {data}")
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
        
        if not trades_data or not trades_data.get("result", {}).get("latestTrades"):
            return None
        
        trades = trades_data["result"]["latestTrades"]
        if not trades:
            return None
        
        # Get the most recent trade (first in the list)
        latest_trade = trades[0]
        try:
            return float(latest_trade["price"])
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing price for {symbol}: {e}")
            return None
