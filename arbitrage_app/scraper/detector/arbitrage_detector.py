import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from arbitrage_app.scraper.api.nobitex_api import NobitexAPI
from arbitrage_app.scraper.api.wallex_api import WallexAPI
from arbitrage_app.sample_trading import TRADING_PAIRS, ARBITRAGE_THRESHOLD

logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    """Data class to represent an arbitrage opportunity"""
    symbol: str
    nobitex_price: float
    wallex_price: float
    profit_percentage: float
    profit_amount: float
    buy_exchange: str
    sell_exchange: str
    timestamp: float

class ArbitrageDetector:
    """Main class for detecting arbitrage opportunities between Nobitex and Wallex"""
    
    def __init__(self):
        self.nobitex_api = NobitexAPI()
        self.wallex_api = WallexAPI()
        self.trading_pairs = TRADING_PAIRS
        self.threshold = ARBITRAGE_THRESHOLD
        
    def get_price_data(self, symbol: str) -> Dict[str, Optional[float]]:
        """
        Get price data from both exchanges for a given symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary with prices from both exchanges
        """
        # Get Nobitex price
        nobitex_price = self.nobitex_api.get_latest_price(symbol)
        
        # Get Wallex price
        wallex_price = self.wallex_api.get_latest_price(symbol)
        
        return {
            "nobitex": nobitex_price,
            "wallex": wallex_price
        }
    
    def calculate_arbitrage(self, nobitex_price: float, wallex_price: float) -> Optional[Tuple[float, str, str]]:
        """
        Calculate arbitrage opportunity between two prices
        
        Args:
            nobitex_price: Price from Nobitex
            wallex_price: Price from Wallex
            
        Returns:
            Tuple of (profit_percentage, buy_exchange, sell_exchange) or None if no opportunity
        """
        if not nobitex_price or not wallex_price:
            return None
        
        # Calculate profit percentage for both directions
        # Direction 1: Buy on Wallex, Sell on Nobitex
        profit_1 = ((nobitex_price - wallex_price) / wallex_price) * 100
        
        # Direction 2: Buy on Nobitex, Sell on Wallex  
        profit_2 = ((wallex_price - nobitex_price) / nobitex_price) * 100
        
        # Check if either direction meets the threshold
        if profit_1 >= self.threshold * 100:
            return profit_1, "wallex", "nobitex"
        elif profit_2 >= self.threshold * 100:
            return profit_2, "nobitex", "wallex"
        
        return None
    
    def detect_arbitrage_opportunity(self, symbol: str) -> Optional[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunity for a specific symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            ArbitrageOpportunity object or None if no opportunity found
        """
        price_data = self.get_price_data(symbol)
        
        nobitex_price = price_data["nobitex"]
        wallex_price = price_data["wallex"]
        
        if not nobitex_price or not wallex_price:
            logger.warning(f"Missing price data for {symbol}: Nobitex={nobitex_price}, Wallex={wallex_price}")
            return None
        
        arbitrage_result = self.calculate_arbitrage(nobitex_price, wallex_price)
        
        if not arbitrage_result:
            return None
        
        profit_percentage, buy_exchange, sell_exchange = arbitrage_result
        
        # Calculate profit amount (assuming 1 unit trade)
        if buy_exchange == "nobitex":
            profit_amount = wallex_price - nobitex_price
        else:
            profit_amount = nobitex_price - wallex_price
        
        return ArbitrageOpportunity(
            symbol=symbol,
            nobitex_price=nobitex_price,
            wallex_price=wallex_price,
            profit_percentage=profit_percentage,
            profit_amount=profit_amount,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            timestamp=time.time()
        )
    
    def scan_all_pairs(self) -> List[ArbitrageOpportunity]:
        """
        Scan all trading pairs for arbitrage opportunities
        
        Returns:
            List of ArbitrageOpportunity objects
        """
        opportunities = []
        
        logger.info(f"Scanning {len(self.trading_pairs)} trading pairs for arbitrage opportunities...")
        
        for symbol in self.trading_pairs:
            try:
                opportunity = self.detect_arbitrage_opportunity(symbol)
                if opportunity:
                    opportunities.append(opportunity)
                    logger.info(f"Arbitrage opportunity found for {symbol}: "
                              f"{opportunity.profit_percentage:.6f}% profit "
                              f"(Buy {opportunity.buy_exchange}, Sell {opportunity.sell_exchange})")
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        return opportunities
    
    def get_market_summary(self) -> Dict[str, Dict]:
        """
        Get a summary of current market prices for all trading pairs
        
        Returns:
            Dictionary with price summaries for all pairs
        """
        summary = {}
        
        for symbol in self.trading_pairs:
            try:
                price_data = self.get_price_data(symbol)
                summary[symbol] = {
                    "nobitex_price": price_data["nobitex"],
                    "wallex_price": price_data["wallex"],
                    "price_difference": None,
                    "arbitrage_opportunity": False
                }
                
                # Calculate price difference if both prices are available
                if price_data["nobitex"] and price_data["wallex"]:
                    diff = abs(price_data["nobitex"] - price_data["wallex"])
                    summary[symbol]["price_difference"] = diff
                    
                    # Check for arbitrage opportunity
                    arbitrage_result = self.calculate_arbitrage(
                        price_data["nobitex"], 
                        price_data["wallex"]
                    )
                    summary[symbol]["arbitrage_opportunity"] = arbitrage_result is not None
                    
            except Exception as e:
                logger.error(f"Error getting market summary for {symbol}: {e}")
                summary[symbol] = {"error": str(e)}
        
        return summary
