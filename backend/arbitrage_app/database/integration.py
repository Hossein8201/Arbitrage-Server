"""
Database integration service for storing arbitrage data
"""

import logging
from typing import List, Optional
from datetime import datetime
from arbitrage_app.database.models import db_manager, ArbitrageOpportunityTable, PriceDataTable
from arbitrage_app.scraper.detector.arbitrage_detector import ArbitrageOpportunity

logger = logging.getLogger(__name__)

class DatabaseIntegrationService:
    """Service for integrating database storage with arbitrage detection"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def store_arbitrage_opportunity(self, opportunity: ArbitrageOpportunity) -> bool:
        """Store an arbitrage opportunity in the database"""
        try:
            opportunity_data = {
                'symbol': opportunity.symbol,
                'nobitex_price': opportunity.nobitex_price,
                'wallex_price': opportunity.wallex_price,
                'profit_percentage': opportunity.profit_percentage,
                'profit_amount': opportunity.profit_amount,
                'buy_exchange': opportunity.buy_exchange,
                'sell_exchange': opportunity.sell_exchange,
                'timestamp': opportunity.timestamp
            }
            
            success = self.db_manager.store_arbitrage_opportunity(opportunity_data)
            if success:
                logger.info(f"💾 Stored arbitrage opportunity for {opportunity.symbol} in database")
            return success
            
        except Exception as e:
            logger.error(f"Error storing arbitrage opportunity: {e}")
            return False
    
    def store_price_data(self, symbol: str, nobitex_price: Optional[float], wallex_price: Optional[float], timestamp: datetime) -> bool:
        """Store price data from both exchanges"""
        success = True
        
        if nobitex_price is not None:
            if not self.db_manager.store_price_data(symbol, 'nobitex', nobitex_price, timestamp):
                success = False
        
        if wallex_price is not None:
            if not self.db_manager.store_price_data(symbol, 'wallex', wallex_price, timestamp):
                success = False
        logger.info(f"💾 Stored price data for {symbol} in database")
        return success
    
    def get_recent_opportunities(self, limit: int = 100) -> List[ArbitrageOpportunityTable]:
        """Get recent arbitrage opportunities from database"""
        return self.db_manager.get_recent_opportunities(limit)
    
    def get_opportunities_by_symbol(self, symbol: str, limit: int = 50) -> List[ArbitrageOpportunityTable]:
        """Get arbitrage opportunities for a specific symbol"""
        return self.db_manager.get_opportunities_by_symbol(symbol, limit)
    
    def get_price_history(self, symbol: str, exchange: str, limit: int = 100) -> List[PriceDataTable]:
        """Get price history for a symbol and exchange"""
        return self.db_manager.get_price_history(symbol, exchange, limit)
 