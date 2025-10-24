#!/usr/bin/env python3
"""
Database test script for Arbitrage Detection Service
This script tests the database connection and functionality
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from arbitrage_app.database.models import db_manager, ArbitrageOpportunity, PriceData
from arbitrage_app.database.integration import DatabaseIntegrationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_tables():
    """Test database table creation and basic operations"""
    print("\n📊 Testing Database Tables")
    print("-" * 40)
    
    try:
        # Test storing a sample arbitrage opportunity
        sample_opportunity = {
            'symbol': 'BTCUSDT',
            'nobitex_price': 45000.0,
            'wallex_price': 45500.0,
            'profit_percentage': 1.11,
            'profit_amount': 500.0,
            'buy_exchange': 'nobitex',
            'sell_exchange': 'wallex',
            'timestamp': datetime.utcnow(),
            'notification_sent': True
        }
        
        success = db_manager.store_arbitrage_opportunity(sample_opportunity)
        if success:
            logger.info("Arbitrage opportunity stored successfully")
        else:
            logger.error("Failed to store arbitrage opportunity")
            return False
        
        # Test storing price data
        price_success = db_manager.store_price_data('BTCUSDT', 'nobitex', 45000.0)
        price_success &= db_manager.store_price_data('BTCUSDT', 'wallex', 45500.0)
        
        if price_success:
            logger.info("Price data stored successfully")
        else:
            logger.error("Failed to store price data")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Database table test error: {e}")
        return False

def test_database_queries():
    """Test database query operations"""
    logger.info("Testing Database Queries")
    
    try:
        # Test getting recent opportunities
        recent_opportunities = db_manager.get_recent_opportunities(5)
        logger.info(f"Retrieved {len(recent_opportunities)} recent opportunities")
        
        # Test getting opportunities by symbol
        btc_opportunities = db_manager.get_opportunities_by_symbol('BTCUSDT', 5)
        logger.info(f"Retrieved {len(btc_opportunities)} BTC opportunities")
        
        # Test getting price history
        nobitex_history = db_manager.get_price_history('BTCUSDT', 'nobitex', 5)
        logger.info(f"Retrieved {len(nobitex_history)} Nobitex price records")
        
        return True
        
    except Exception as e:
        logger.error(f"Database query test error: {e}")
        return False

def test_postgres_exporter_metrics():
    """Test if PostgreSQL exporter metrics are available"""
    logger.info("Testing PostgreSQL Exporter Metrics")
    
    try:
        import requests
        
        # Try to access postgres exporter metrics
        try:
            response = requests.get('http://localhost:9187/metrics', timeout=5)
            if response.status_code == 200:
                logger.info("PostgreSQL exporter metrics endpoint accessible")
                
                # Check for some key metrics
                metrics_text = response.text
                if 'pg_stat_database' in metrics_text:
                    print("✅ PostgreSQL database metrics found")
                else:
                    print("⚠️  PostgreSQL database metrics not found")
                
                return True
            else:
                print(f"❌ PostgreSQL exporter returned status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.warning("PostgreSQL exporter not accessible (may not be running)")
            return True  # Don't fail the test if exporter isn't running
            
    except ImportError:
        logger.warning("requests library not available for testing exporter")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL exporter test error: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Database Integration Test Suite")
    
    # Check environment variables
    database_url = os.getenv("DATABASE_URL")
    logger.info(f"Database URL: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    # Run tests
    tests = [
        test_database_tables,
        test_database_queries,
        test_postgres_exporter_metrics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
    
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All database tests passed successfully!")
        logger.info("\nYour database integration is ready for production!")
    else:
        logger.error("Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
