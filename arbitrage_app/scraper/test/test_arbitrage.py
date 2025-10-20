"""
Test script for the arbitrage detection system
This script tests the API integrations and arbitrage detection logic
"""

import logging
import time
from detector.arbitrage_detector import ArbitrageDetector
from sample_trading import TRADING_PAIRS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_api_connections():
    """Test API connections to both exchanges"""
    print("Testing API connections...")
    
    detector = ArbitrageDetector()
    
    # Test a few symbols
    test_symbols = ["BTCUSDT", "ETHUSDT", "USDTUSDT"]
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")
        
        # Test Nobitex
        nobitex_price = detector.nobitex_api.get_latest_price(symbol)
        print(f"  Nobitex price: {nobitex_price}")
        
        # Test Wallex
        wallex_price = detector.wallex_api.get_latest_price(symbol)
        print(f"  Wallex price: {wallex_price}")
        
        if nobitex_price and wallex_price:
            # Calculate potential arbitrage
            arbitrage_result = detector.calculate_arbitrage(nobitex_price, wallex_price)
            if arbitrage_result:
                profit, buy_ex, sell_ex = arbitrage_result
                print(f"  🎯 Arbitrage opportunity: {profit:.2f}% (Buy {buy_ex}, Sell {sell_ex})")
            else:
                print(f"  No arbitrage opportunity")
        else:
            print(f"  ⚠️  Missing price data")

def test_arbitrage_detection():
    """Test the arbitrage detection for all trading pairs"""
    print("\n" + "="*50)
    print("Testing arbitrage detection for all trading pairs...")
    print("="*50)
    
    detector = ArbitrageDetector()
    
    # Get market summary
    summary = detector.get_market_summary()
    
    print(f"\nMarket Summary for {len(TRADING_PAIRS)} trading pairs:")
    print("-" * 80)
    print(f"{'Symbol':<10} {'Nobitex':<15} {'Wallex':<15} {'Diff':<15} {'Arbitrage':<10}")
    print("-" * 80)
    
    arbitrage_count = 0
    
    for symbol, data in summary.items():
        if "error" in data:
            print(f"{symbol:<10} ERROR: {data['error']}")
            continue
            
        nobitex_price = data.get("nobitex_price", "N/A")
        wallex_price = data.get("wallex_price", "N/A")
        price_diff = data.get("price_difference", "N/A")
        has_arbitrage = data.get("arbitrage_opportunity", False)
        
        if has_arbitrage:
            arbitrage_count += 1
            arbitrage_indicator = "🎯 YES"
        else:
            arbitrage_indicator = "❌ NO"
        
        print(f"{symbol:<10} {str(nobitex_price):<15} {str(wallex_price):<15} {str(price_diff):<15} {arbitrage_indicator:<10}")
    
    print("-" * 80)
    print(f"Total arbitrage opportunities found: {arbitrage_count}")

def test_full_scan():
    """Test the full arbitrage scanning functionality"""
    print("\n" + "="*50)
    print("Running full arbitrage scan...")
    print("="*50)
    
    detector = ArbitrageDetector()
    
    start_time = time.time()
    opportunities = detector.scan_all_pairs()
    end_time = time.time()
    
    print(f"\nScan completed in {end_time - start_time:.2f} seconds")
    print(f"Found {len(opportunities)} arbitrage opportunities:")
    
    if opportunities:
        print("\nArbitrage Opportunities:")
        print("-" * 100)
        print(f"{'Symbol':<10} {'Nobitex':<15} {'Wallex':<15} {'Profit %':<10} {'Buy':<10} {'Sell':<10}")
        print("-" * 100)
        
        for opp in opportunities:
            print(f"{opp.symbol:<10} {opp.nobitex_price:<15.2f} {opp.wallex_price:<15.2f} "
                  f"{opp.profit_percentage:<10.2f} {opp.buy_exchange:<10} {opp.sell_exchange:<10}")
    else:
        print("No arbitrage opportunities found at this time.")

if __name__ == "__main__":
    print("🚀 Starting Arbitrage Detection System Test")
    print("=" * 60)
    
    try:
        # Test API connections
        test_api_connections()
        
        # Test arbitrage detection
        test_arbitrage_detection()
        
        # Test full scan
        test_full_scan()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.exception("Test failed")
