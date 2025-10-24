import os
import logging
import requests
from typing import Optional
from datetime import datetime
from arbitrage_app.scraper.detector.arbitrage_detector import ArbitrageOpportunity
from arbitrage_app.sample_trading import TRADING_PAIRS, ARBITRAGE_THRESHOLD

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class BaleNotifier:
    """Bale bot client for sending arbitrage notifications"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://tapi.bale.ai/bot{bot_token}"
        
    def send_message(self, message: str) -> bool:
        """
        Send a message to the configured Bale chat
        
        Args:
            message: The message text to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Bale message sent successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Bale message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Bale message: {e}")
            return False
    
    def format_arbitrage_message(self, opportunity: ArbitrageOpportunity) -> str:
        """
        Format arbitrage opportunity data into a Bale message
        
        Args:
            opportunity: ArbitrageOpportunity object
            
        Returns:
            Formatted message string
        """
        # Format discovery time
        discovery_time = datetime.fromtimestamp(opportunity.timestamp)
        time_str = discovery_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format prices with proper formatting
        nobitex_price_str = f"{opportunity.nobitex_price:,.6f}"
        wallex_price_str = f"{opportunity.wallex_price:,.6f}"
        
        # Format profit information
        profit_percentage_str = f"{opportunity.profit_percentage:.6f}%"
        profit_amount_str = f"{opportunity.profit_amount:,.6f}"
        
        # Create the message
        message = f"""
🚨 * ARBITRAGE OPPORTUNITY DETECTED! * 🚨

📊 * Currency Pair: * {opportunity.symbol}
⏰ * Discovery Time: * {time_str}

💰 * Price Information: *
• * Nobitex Price: * {nobitex_price_str} USDT
• * Wallex Price: * {wallex_price_str} USDT

📈 * Arbitrage Details: *
• * Buy Exchange: * {opportunity.buy_exchange.upper()}
• * Sell Exchange: * {opportunity.sell_exchange.upper()}
• * Profit Percentage: * {profit_percentage_str}
• * Profit Amount: * {profit_amount_str} USDT

⚡ _ Act quickly! Arbitrage opportunities may disappear fast. _
        """.strip()
        
        return message
    
    def send_arbitrage_alert(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Send an arbitrage opportunity alert to Bale
        
        Args:
            opportunity: ArbitrageOpportunity object
            
        Returns:
            True if alert sent successfully, False otherwise
        """
        message = self.format_arbitrage_message(opportunity)
        return self.send_message(message)
    
    def send_test_message(self) -> bool:
        """
        Send a test message to verify bot configuration
        
        Returns:
            True if test message sent successfully, False otherwise
        """
        test_message = """
🤖 * Arbitrage Detection Bot *

✅ Bot is working correctly!
⏰ Test time: {time}

_ This is a test message to verify the Bale bot configuration. _
        """.format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")).strip()
        
        return self.send_message(test_message)
    
    def send_startup_notification(self) -> bool:
        """
        Send a startup notification when the service starts
        
        Returns:
            True if notification sent successfully, False otherwise
        """
        startup_message = """
🚀 * Arbitrage Detection Service Started *

⏰ Start time: {time}
📊 Monitoring: {pairs} trading pairs
🎯 Threshold: {threshold}%

_ The service is now actively monitoring for arbitrage opportunities. _
        """.format(
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pairs=len(TRADING_PAIRS),
            threshold=ARBITRAGE_THRESHOLD
        ).strip()
        
        return self.send_message(startup_message)
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Send an error notification to Bale
        
        Args:
            error_message: Description of the error
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        error_notification = f"""
❌ * Arbitrage Detection Service Error *

⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🚨 Error: {error_message}

_ Please check the service logs for more details. _
        """.strip()
        
        return self.send_message(error_notification)

def create_bale_notifier() -> Optional[BaleNotifier]:
    """
    Create a BaleNotifier instance from environment variables
    
    Returns:
        BaleNotifier instance or None if configuration is missing
    """
    bot_token = os.getenv("BALE_BOT_TOKEN")
    chat_id = os.getenv("BALE_CHAT_ID")
    
    if not bot_token or not chat_id:
        logger.warning("Bale configuration missing. Set BALE_BOT_TOKEN and BALE_CHAT_ID environment variables.")
        return None
    
    if bot_token == "your_bot_token_here" or chat_id == "your_chat_id_here":
        logger.warning("Bale configuration not properly set. Please update environment variables.")
        return None
    
    return BaleNotifier(bot_token, chat_id)
