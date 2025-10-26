import logging
import time
from typing import List
from arbitrage_app.scraper.detector.arbitrage_detector import ArbitrageDetector, ArbitrageOpportunity
from arbitrage_app.bot.notifier.bale_notifier import create_bale_notifier


logger = logging.getLogger(__name__)

class ArbitrageNotificationService:
    """Service that monitors for arbitrage opportunities and sends notifications"""
    
    def __init__(self, metrics_collector=None, db_manager=None):
        self.detector = ArbitrageDetector(metrics_collector, db_manager)
        self.bale_notifier = create_bale_notifier()
        self.last_notifications = {}  # Track last notification time per symbol
        self.notification_cooldown = 300  # 5 minutes cooldown between notifications for same symbol
        self.metrics = metrics_collector
        
    def should_send_notification(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Check if we should send a notification for this opportunity
        Implements cooldown to avoid spam
        
        Args:
            opportunity: ArbitrageOpportunity object
            
        Returns:
            True if notification should be sent, False otherwise
        """
        current_time = time.time()
        last_notification_time = self.last_notifications.get(opportunity.symbol, 0)
        
        # Check if enough time has passed since last notification for this symbol
        if current_time - last_notification_time < self.notification_cooldown:
            logger.info(f"Notification cooldown active for {opportunity.symbol}. Skipping notification.")
            return False
        
        return True
    
    def send_arbitrage_notification(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Send arbitrage notification if conditions are met
        
        Args:
            opportunity: ArbitrageOpportunity object
            
        Returns:
            True if notification was sent, False otherwise
        """
        if not self.bale_notifier:
            logger.warning("Bale notifier not configured. Skipping notification.")
            return False
        
        if not self.should_send_notification(opportunity):
            return False
        
        try:
            success = self.bale_notifier.send_arbitrage_alert(opportunity)
            
            if success:
                # Update last notification time
                self.last_notifications[opportunity.symbol] = time.time()
                logger.info(f"Arbitrage notification sent for {opportunity.symbol}")
                return True
            else:
                logger.error(f"Failed to send arbitrage notification for {opportunity.symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending arbitrage notification for {opportunity.symbol}: {e}")
            return False
    
    def scan_and_notify(self) -> List[ArbitrageOpportunity]:
        """
        Scan for arbitrage opportunities and send notifications
        
        Returns:
            List of arbitrage opportunities found
        """
        try:
            # Scan for opportunities
            opportunities = self.detector.scan_all_pairs()
            
            # Send notifications for each opportunity
            notifications_sent = 0
            for opportunity in opportunities:
                if self.send_arbitrage_notification(opportunity):
                    notifications_sent += 1
            
            logger.info(f"Scan completed. Found {len(opportunities)} opportunities, sent {notifications_sent} notifications.")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error during arbitrage scan: {e}")
            
            # Send error notification
            if self.bale_notifier:
                self.bale_notifier.send_error_notification(str(e))
            
            return []
    
    def send_startup_notification(self) -> bool:
        """
        Send startup notification when service starts
        
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.bale_notifier:
            logger.warning("Bale notifier not configured. Skipping startup notification.")
            return False
        
        try:
            return self.bale_notifier.send_startup_notification()
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
            return False
    
    def send_test_notification(self) -> bool:
        """
        Send test notification to verify bot configuration
        
        Returns:
            True if test notification sent successfully, False otherwise
        """
        if not self.bale_notifier:
            logger.warning("Bale notifier not configured. Cannot send test notification.")
            return False
        
        try:
            return self.bale_notifier.send_test_message()
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            return False
    
    def get_service_status(self) -> dict:
        """
        Get current service status information
        
        Returns:
            Dictionary with service status
        """
        return {
            "bale_configured": self.bale_notifier is not None,
            "trading_pairs_count": len(self.detector.trading_pairs),
            "arbitrage_threshold": self.detector.threshold,
            "notification_cooldown": self.notification_cooldown,
            "last_notifications": len(self.last_notifications),
            "service_uptime": time.time()
        }

def main():
    """Main function for testing the notification service"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting Arbitrage Notification Service Test")
    print("=" * 60)
    
    # Create notification service
    service = ArbitrageNotificationService()
    
    # Check service status
    status = service.get_service_status()
    print(f"\n📊 Service Status:")
    print(f"  Bale configured: {status['bale_configured']}")
    print(f"  Trading pairs: {status['trading_pairs_count']}")
    print(f"  Arbitrage threshold: {status['arbitrage_threshold']*100}%")
    
    if not status['bale_configured']:
        print("\n⚠️  Bale not configured. Set BALE_BOT_TOKEN and BALE_CHAT_ID environment variables.")
        print("   You can still test arbitrage detection without notifications.")
    
    # Test Telegram bot if configured
    if status['bale_configured']:
        print("\n🤖 Testing Bale bot...")
        if service.send_test_notification():
            print("✅ Test notification sent successfully!")
        else:
            print("❌ Failed to send test notification")
    
    # Run arbitrage scan
    print("\n🔍 Running arbitrage scan...")
    opportunities = service.scan_and_notify()
    
    if opportunities:
        print(f"\n🎯 Found {len(opportunities)} arbitrage opportunities:")
        for opp in opportunities:
            print(f"  • {opp.symbol}: {opp.profit_percentage:.6f}% profit")
    else:
        print("\n📊 No arbitrage opportunities found at this time.")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
