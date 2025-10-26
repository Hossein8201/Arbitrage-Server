"""
Database models and connection for Arbitrage Detection Service
"""

import os
import logging
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ArbitrageOpportunity(Base):
    """Database model for storing arbitrage opportunities"""
    __tablename__ = "arbitrage_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    nobitex_price = Column(Float, nullable=False)
    wallex_price = Column(Float, nullable=False)
    profit_percentage = Column(Float, nullable=False)
    profit_amount = Column(Float, nullable=False)
    buy_exchange = Column(String(20), nullable=False)
    sell_exchange = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PriceData(Base):
    """Database model for storing price data from exchanges"""
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database manager for arbitrage service"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def store_arbitrage_opportunity(self, opportunity_data: dict) -> bool:
        """Store an arbitrage opportunity in the database"""
        try:
            with self.get_session() as session:
                opportunity = ArbitrageOpportunity(**opportunity_data)
                session.add(opportunity)
                session.commit()
                logger.info(f"Stored arbitrage opportunity for {opportunity_data['symbol']}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error storing arbitrage opportunity: {e}")
            return False
    
    def store_price_data(self, symbol: str, exchange: str, price: float) -> bool:
        """Store price data in the database"""
        try:
            with self.get_session() as session:
                price_record = PriceData(
                    symbol=symbol,
                    exchange=exchange,
                    price=price
                )
                session.add(price_record)
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error storing price data: {e}")
            return False
    
    def get_recent_opportunities(self, limit: int = 100) -> List[ArbitrageOpportunity]:
        """Get recent arbitrage opportunities"""
        try:
            with self.get_session() as session:
                return session.query(ArbitrageOpportunity)\
                    .order_by(ArbitrageOpportunity.timestamp.desc())\
                    .limit(limit)\
                    .all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent opportunities: {e}")
            return []
    
    def get_opportunities_by_symbol(self, symbol: str, limit: int = 50) -> List[ArbitrageOpportunity]:
        """Get arbitrage opportunities for a specific symbol"""
        try:
            with self.get_session() as session:
                return session.query(ArbitrageOpportunity)\
                    .filter(ArbitrageOpportunity.symbol == symbol)\
                    .order_by(ArbitrageOpportunity.timestamp.desc())\
                    .limit(limit)\
                    .all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting opportunities for {symbol}: {e}")
            return []
    
    def get_price_history(self, symbol: str, exchange: str, limit: int = 100) -> List[PriceData]:
        """Get price history for a symbol and exchange"""
        try:
            with self.get_session() as session:
                return session.query(PriceData)\
                    .filter(PriceData.symbol == symbol, PriceData.exchange == exchange)\
                    .order_by(PriceData.timestamp.desc())\
                    .limit(limit)\
                    .all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting price history for {symbol} on {exchange}: {e}")
            return []

# Global database manager instance
db_manager = DatabaseManager()
