#!/usr/bin/env python3
"""
Test script for Bale notifications
This script tests the Bale bot integration and notification system
"""

import os
import logging
import time
from arbitrage_app.bot.notifier.notification_service import ArbitrageNotificationService
from arbitrage_app.scraper.detector.arbitrage_detector import ArbitrageOpportunity

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_bale_configuration():
    """Test Bale bot configuration"""
    print("🤖 Testing Bale Bot Configuration")
    print("-" * 40)
    
    bot_token = os.getenv("BALE_BOT_TOKEN")
    chat_id = os.getenv("BALE_CHAT_ID")
    
    print(f"Bot Token: {'✅ Set' if bot_token and bot_token != 'your_bot_token_here' else '❌ Not set'}")
    print(f"Chat ID: {'✅ Set' if chat_id and chat_id != 'your_chat_id_here' else '❌ Not set'}")
    
    if not bot_token or not chat_id or bot_token == "your_bot_token_here" or chat_id == "your_chat_id_here":
        print("\n⚠️  To test Bale notifications, please:")
        print("1. Create a Bale bot using @BotFather")
        print("2. Get your chat ID (you can use @getmyidbot)")
        print("3. Set environment variables:")
        print("   export BALE_BOT_TOKEN='your_actual_bot_token'")
        print("   export BALE_CHAT_ID='your_actual_chat_id'")
        print("4. Or create a .env file with these values")
        return False
    
    return True

def test_notification_service():
    """Test the notification service"""
    print("\n🔔 Testing Notification Service")
    print("-" * 40)
    
    service = ArbitrageNotificationService()
    status = service.get_service_status()
    
    print(f"Bale configured: {'✅' if status['bale_configured'] else '❌'}")
    print(f"Trading pairs: {status['trading_pairs_count']}")
    print(f"Arbitrage threshold: {status['arbitrage_threshold']*100}%")
    print(f"Notification cooldown: {status['notification_cooldown']} seconds")
    
    return status['bale_configured']

def test_bale_bot():
    """Test Bale bot functionality"""
    print("\n📱 Testing Bale Bot")
    print("-" * 40)
    
    service = ArbitrageNotificationService()
    
    if not service.bale_notifier:
        print("❌ Bale notifier not configured")
        return False
    
    # Send test message
    print("Sending test message...")
    success = service.send_test_notification()
    
    if success:
        print("✅ Test message sent successfully!")
        print("Check your Bale chat for the test message.")
    else:
        print("❌ Failed to send test message")
        print("Check your Bale bot token and chat ID configuration.")
    
    return success

def test_startup_notification():
    """Test startup notification"""
    print("\n🚀 Testing Startup Notification")
    print("-" * 40)
    
    service = ArbitrageNotificationService()
    
    if not service.bale_notifier:
        print("❌ Bale notifier not configured")
        return False
    
    print("Sending startup notification...")
    success = service.send_startup_notification()
    
    if success:
        print("✅ Startup notification sent successfully!")
    else:
        print("❌ Failed to send startup notification")
    
    return success

def test_arbitrage_notification():
    """Test arbitrage opportunity notification with mock data"""
    print("\n🎯 Testing Arbitrage Notification")
    print("-" * 40)
    
    service = ArbitrageNotificationService()
    
    if not service.bale_notifier:
        print("❌ Bale notifier not configured")
        return False
    
    # Create a mock arbitrage opportunity for testing
    mock_opportunity = ArbitrageOpportunity(
        symbol="BTCUSDT",
        nobitex_price=56250.0,      # 56250 USDT
        wallex_price=45000.0,        # 45000 USDT
        profit_percentage=25,       # 25% profit
        profit_amount=11250.0,    # 11250 USDT profit
        buy_exchange="wallex",
        sell_exchange="nobitex",
        timestamp=time.time()
    )
    
    print(f"Sending mock arbitrage notification for {mock_opportunity.symbol}...")
    print(f"Profit: {mock_opportunity.profit_percentage}%")
    
    success = service.send_arbitrage_notification(mock_opportunity)
    
    if success:
        print("✅ Mock arbitrage notification sent successfully!")
        print("Check your Bale chat for the arbitrage alert.")
    else:
        print("❌ Failed to send arbitrage notification")
    
    return success

def test_real_arbitrage_scan():
    """Test real arbitrage scanning with notifications"""
    print("\n🔍 Testing Real Arbitrage Scan")
    print("-" * 40)
    
    service = ArbitrageNotificationService()
    
    print("Running arbitrage scan...")
    print("This may take a few minutes due to rate limiting...")
    
    start_time = time.time()
    opportunities = service.scan_and_notify()
    end_time = time.time()
    
    print(f"\nScan completed in {end_time - start_time:.2f} seconds")
    print(f"Found {len(opportunities)} arbitrage opportunities")
    
    if opportunities:
        print("\nArbitrage Opportunities Found:")
        for opp in opportunities:
            print(f"  • {opp.symbol}: {opp.profit_percentage:.6f}% profit")
            print(f"    Buy: {opp.buy_exchange}, Sell: {opp.sell_exchange}")
            print(f"    Nobitex: {opp.nobitex_price:,.6f} USDT")
            print(f"    Wallex: {opp.wallex_price:,.6f} USDT")
            print()
    else:
        print("No arbitrage opportunities found at this time.")
    
    return len(opportunities) > 0

def main():
    """Main test function"""
    print("🚀 Bale Notification System Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_bale_configuration()
    
    if not config_ok:
        print("\n⚠️  Skipping Bale tests due to missing configuration.")
        print("You can still test arbitrage detection without notifications.")
        
        # Test arbitrage detection only
        print("\n🔍 Testing Arbitrage Detection (No Notifications)")
        print("-" * 50)
        service = ArbitrageNotificationService()
        opportunities = service.scan_and_notify()
        
        if opportunities:
            print(f"Found {len(opportunities)} arbitrage opportunities:")
            for opp in opportunities:
                print(f"  • {opp.symbol}: {opp.profit_percentage:.6f}% profit")
        else:
            print("No arbitrage opportunities found.")
        
        return
    
    # Test notification service
    test_notification_service()
    
    # Test Telegram bot
    bot_ok = test_bale_bot()
    
    if not bot_ok:
        print("\n❌ Bale bot test failed. Check your configuration.")
        return
    
    # Test startup notification
    test_startup_notification()
    
    # Test arbitrage notification with mock data
    test_arbitrage_notification()
    
    # Ask user if they want to test real arbitrage scan
    print("\n" + "=" * 60)
    response = input("Do you want to run a real arbitrage scan? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        test_real_arbitrage_scan()
    else:
        print("Skipping real arbitrage scan.")
    
    print("\n✅ All Bale notification tests completed!")

if __name__ == "__main__":
    main()
