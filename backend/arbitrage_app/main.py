"""
Arbitrage Detection Application
Main application that runs the arbitrage detection service continuously
"""

import sys
import time
import signal
import logging
from datetime import datetime

from arbitrage_app.bot.notifier.notification_service import ArbitrageNotificationService
from arbitrage_app.sample_trading import CHECK_INTERVAL_SECONDS
from arbitrage_app.prometheus_adapter.metrics import PrometheusMetrics, start_metrics_server
from arbitrage_app.database.models import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ArbitrageApp:
    """Main application class for continuous arbitrage detection"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = PrometheusMetrics(self.start_time)
        self.db_manager = db_manager
        self.service = ArbitrageNotificationService(self.metrics, self.db_manager)
        self.running = False
        self.scan_count = 0
        self.total_opportunities = 0
        self.last_scan_time = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.stop()
    
    def start(self):
        """Start the arbitrage detection service"""
        logger.info("🚀 Starting Arbitrage Detection Application")
        logger.info("=" * 60)
        
        self.running = True
        self.start_time = time.time()
        
        # Send startup notification
        try:
            self.service.send_startup_notification()
        except Exception as e:
            logger.warning(f"Failed to send startup notification: {e}")
        
        # Log service status
        status = self.service.get_service_status()
        logger.info(f"📊 Service Status:")
        logger.info(f"  Bale configured: {status['bale_configured']}")
        logger.info(f"  Trading pairs: {status['trading_pairs_count']}")
        logger.info(f"  Arbitrage threshold: {status['arbitrage_threshold']*100}%")
        logger.info(f"  Check interval: {CHECK_INTERVAL_SECONDS} seconds")        
        # Start Prometheus metrics server
        metrics_port = 8000
        start_metrics_server(metrics_port)
        
        logger.info(f"✅ Service started successfully!")
        logger.info(f"🔄 Monitoring {status['trading_pairs_count']} trading pairs every {CHECK_INTERVAL_SECONDS} seconds")
        logger.info(f"📊 Prometheus metrics available at http://localhost:{metrics_port}/metrics")
        logger.info("Press Ctrl+C to stop the service")
        logger.info("-" * 60)
        
        # Main loop
        try:
            while self.running:
                running_time = time.time()
                self._scan_cycle()
                elapsed_time = time.time() - running_time
                if elapsed_time < CHECK_INTERVAL_SECONDS:
                    time.sleep(CHECK_INTERVAL_SECONDS - elapsed_time)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the arbitrage detection service"""
        if not self.running:
            return
            
        self.running = False
        
        # Calculate uptime
        uptime = time.time() - self.start_time if self.start_time else 0
        uptime_str = self._format_uptime(uptime)
        
        logger.info("🛑 Stopping Arbitrage Detection Application")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"  Total uptime: {uptime_str}")
        logger.info(f"  Total scans: {self.scan_count}")
        logger.info(f"  Total opportunities found: {self.total_opportunities}")
        logger.info(f"  Last scan: {self.last_scan_time}")
        
        # Send shutdown notification if possible
        try:
            if self.service.bale_notifier:
                shutdown_message = f"""
🛑 * Arbitrage Detection Service Stopped *

⏰ Stop time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📊 Total uptime: {uptime_str}
🔍 Total scans: {self.scan_count}
🎯 Total opportunities: {self.total_opportunities}

_ Service has been stopped. _
                """.strip()
                
                self.service.bale_notifier.send_message(shutdown_message)
        except Exception as e:
            logger.warning(f"Failed to send shutdown notification: {e}")
        
        logger.info("✅ Service stopped successfully")
    
    def _scan_cycle(self):
        """Execute one arbitrage scanning cycle"""
        if not self.running:
            return
            
        try:
            self.scan_count += 1
            self.last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"🔍 Starting scan #{self.scan_count} at {self.last_scan_time}")
            
            # Run the arbitrage scan
            opportunities = self.service.scan_and_notify()
            
            # Update statistics
            self.total_opportunities += len(opportunities)
            
            # Update Prometheus metrics
            self.metrics.update_service_metrics(self.scan_count)
            
            # Log results
            if opportunities:
                logger.info(f"🎯 Found {len(opportunities)} arbitrage opportunities:")
                for opp in opportunities:
                    logger.info(f"  • {opp.symbol}: {opp.profit_percentage:.6f}% profit "
                              f"(Buy {opp.buy_exchange}, Sell {opp.sell_exchange})")
            else:
                logger.info("📊 No arbitrage opportunities found in this scan")
            
            # Log periodic statistics
            if self.scan_count % 10 == 0:  # Every 10 scans
                self._log_periodic_stats()
                
        except Exception as e:
            logger.error(f"Error in scan cycle #{self.scan_count}: {e}")
            
            # Send error notification
            try:
                if self.service.bale_notifier:
                    self.service.bale_notifier.send_error_notification(f"Scan error: {str(e)}")
            except Exception as notify_error:
                logger.error(f"Failed to send error notification: {notify_error}")
    
    def _log_periodic_stats(self):
        """Log periodic statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        uptime_str = self._format_uptime(uptime)
        
        logger.info("📈 Periodic Statistics:")
        logger.info(f"  Uptime: {uptime_str}")
        logger.info(f"  Scans completed: {self.scan_count}")
        logger.info(f"  Opportunities found: {self.total_opportunities}")
        logger.info(f"  Average opportunities per scan: {self.total_opportunities/max(self.scan_count, 1):.6f}")
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in a human-readable format"""
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_status(self) -> dict:
        """Get current application status"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "running": self.running,
            "uptime": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "scan_count": self.scan_count,
            "total_opportunities": self.total_opportunities,
            "last_scan_time": self.last_scan_time,
            "service_status": self.service.get_service_status()
        }

def main():
    """Main entry point"""
    print("🚀 Arbitrage Detection Application")
    print("=" * 50)
    
    # Create and start the application
    app = ArbitrageApp()
    
    try:
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
