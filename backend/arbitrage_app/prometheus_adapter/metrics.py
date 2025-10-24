"""
Prometheus metrics collection for Arbitrage Detection Service
"""

import time
import logging
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Request counters for each exchange
nobitex_requests_total = Counter(
    'nobitex_requests_total', 
    'Total number of requests to Nobitex API',
    ['status']  # 'success' or 'error'
)

wallex_requests_total = Counter(
    'wallex_requests_total', 
    'Total number of requests to Wallex API',
    ['status']  # 'success' or 'error'
)

# Response time histograms for each exchange
nobitex_response_time = Histogram(
    'nobitex_response_time_seconds',
    'Response time for Nobitex API requests',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

wallex_response_time = Histogram(
    'wallex_response_time_seconds',
    'Response time for Wallex API requests',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Arbitrage opportunity metrics
arbitrage_opportunities_total = Counter(
    'arbitrage_opportunities_total',
    'Total number of arbitrage opportunities discovered',
    ['symbol', 'buy_exchange', 'sell_exchange']
)

arbitrage_discovery_rate = Counter(
    'arbitrage_discovery_rate_total',
    'Rate of arbitrage opportunity discoveries per interval'
)

# Price difference metrics for each currency pair
price_difference_gauge = Gauge(
    'price_difference_percentage',
    'Last observed price difference percentage between exchanges',
    ['symbol']
)

# Service health metrics
service_uptime = Gauge(
    'service_uptime_seconds',
    'Service uptime in seconds'
)

service_scans_total = Counter(
    'service_scans_total',
    'Total number of arbitrage scans performed'
)

# Exchange-specific price gauges
nobitex_price_gauge = Gauge(
    'nobitex_price',
    'Last observed price from Nobitex',
    ['symbol']
)

wallex_price_gauge = Gauge(
    'wallex_price',
    'Last observed price from Wallex',
    ['symbol']
)

class PrometheusMetrics:
    """Prometheus metrics collector for the arbitrage service"""
    
    def __init__(self, start_time: float):
        self.start_time = start_time
        self.last_arbitrage_count = 0
    
    def record_nobitex_request(self, success: bool, response_time: float):
        """Record a Nobitex API request"""
        status = 'success' if success else 'error'
        nobitex_requests_total.labels(status=status).inc()
        
        if success:
            nobitex_response_time.observe(response_time)
    
    def record_wallex_request(self, success: bool, response_time: float):
        """Record a Wallex API request"""
        status = 'success' if success else 'error'
        wallex_requests_total.labels(status=status).inc()
        
        if success:
            wallex_response_time.observe(response_time)
    
    def record_arbitrage_opportunity(self, symbol: str, buy_exchange: str, sell_exchange: str):
        """Record an arbitrage opportunity discovery"""
        arbitrage_opportunities_total.labels(
            symbol=symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange
        ).inc()
        
        arbitrage_discovery_rate.inc()
    
    def update_price_difference(self, symbol: str, difference_percentage: float):
        """Update price difference metric for a symbol"""
        price_difference_gauge.labels(symbol=symbol).set(difference_percentage)
    
    def update_exchange_prices(self, symbol: str, nobitex_price: Optional[float], wallex_price: Optional[float]):
        """Update price gauges for both exchanges"""
        if nobitex_price is not None:
            nobitex_price_gauge.labels(symbol=symbol).set(nobitex_price)
        
        if wallex_price is not None:
            wallex_price_gauge.labels(symbol=symbol).set(wallex_price)
    
    def update_service_metrics(self, scan_count: int):
        """Update service-level metrics"""
        service_uptime.set(time.time() - self.start_time)
        service_scans_total.inc()
    
    def get_metrics_summary(self) -> Dict[str, any]:
        """Get a summary of current metrics"""
        current_time = time.time()
        
        return {
            "uptime_seconds": current_time - self.start_time,
            "total_scans": scan_count,
            "nobitex_success_rate": self._calculate_success_rate('nobitex'),
            "wallex_success_rate": self._calculate_success_rate('wallex'),
            "arbitrage_discovery_rate": arbitrage_discovery_rate._value.get()
        }
    
    def _calculate_success_rate(self, exchange: str) -> float:
        """Calculate success rate for an exchange"""
        if exchange == 'nobitex':
            success_counter = nobitex_requests_total.labels(status='success')._value.get()
            error_counter = nobitex_requests_total.labels(status='error')._value.get()
        elif exchange == 'wallex':
            success_counter = wallex_requests_total.labels(status='success')._value.get()
            error_counter = wallex_requests_total.labels(status='error')._value.get()
        else:
            return 0.0
        
        total = success_counter + error_counter
        return (success_counter / total * 100) if total > 0 else 0.0

def start_metrics_server(port: int = 8000):
    """Start the Prometheus metrics HTTP server"""
    start_http_server(port)
    logger.info(f"📊 Prometheus metrics server started on port {port}")
    logger.info(f"🔗 Metrics endpoint: http://localhost:{port}/metrics")

def get_metrics_data():
    """Get the latest metrics data in Prometheus format"""
    return generate_latest()
