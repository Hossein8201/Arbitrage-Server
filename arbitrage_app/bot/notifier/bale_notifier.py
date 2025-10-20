import os
import logging
import requests
from typing import Optional
from datetime import datetime
from scraper.detector.arbitrage_detector import ArbitrageOpportunity
from scraper.sample_trading import TRADING_PAIRS

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class BaleNotifier:
    """Bale bot client for sending arbitrage notifications"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://web.bale.ai/bot{bot_token}"
        
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
        nobitex_price_str = f"{opportunity.nobitex_price:,.2f}"
        wallex_price_str = f"{opportunity.wallex_price:,.2f}"
        
        # Format profit information
        profit_percentage_str = f"{opportunity.profit_percentage:.2f}%"
        profit_amount_str = f"{opportunity.profit_amount:,.2f}"
        
        # Create the message
        message = f"""
🚨 <b>ARBITRAGE OPPORTUNITY DETECTED!</b> 🚨

📊 <b>Currency Pair:</b> {opportunity.symbol}
⏰ <b>Discovery Time:</b> {time_str}

💰 <b>Price Information:</b>
• <b>Nobitex Price:</b> {nobitex_price_str} IRT
• <b>Wallex Price:</b> {wallex_price_str} USDT

📈 <b>Arbitrage Details:</b>
• <b>Buy Exchange:</b> {opportunity.buy_exchange.upper()}
• <b>Sell Exchange:</b> {opportunity.sell_exchange.upper()}
• <b>Profit Percentage:</b> {profit_percentage_str}
• <b>Profit Amount:</b> {profit_amount_str} IRT

⚡ <i>Act quickly! Arbitrage opportunities may disappear fast.</i>
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
🤖 <b>Arbitrage Detection Bot</b>

✅ Bot is working correctly!
⏰ Test time: {time}

<i>This is a test message to verify the Bale bot configuration.</i>
        """.format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")).strip()
        
        return self.send_message(test_message)
    
    def send_startup_notification(self) -> bool:
        """
        Send a startup notification when the service starts
        
        Returns:
            True if notification sent successfully, False otherwise
        """
        startup_message = """
🚀 <b>Arbitrage Detection Service Started</b>

⏰ Start time: {time}
📊 Monitoring: {pairs} trading pairs
🎯 Threshold: {threshold}%

<i>The service is now actively monitoring for arbitrage opportunities.</i>
        """.format(
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pairs=len(TRADING_PAIRS),
            threshold=os.getenv("ARBITRAGE_THRESHOLD")
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
❌ <b>Arbitrage Detection Service Error</b>

⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🚨 Error: {error_message}

<i>Please check the service logs for more details.</i>
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
