TRADING_PAIRS = [
    "BTCUSDT",
    "ETHUSDT", 
    "LTCUSDT",
    "XRPUSDT",
    "BCHUSDT",
    "BNBUSDT",
    "XLMUSDT",
    "ETCUSDT",
    "TRXUSDT",
    "DOGEUSDT",
    "UNIUSDT",
    "DAIUSDT",
    "LINKUSDT",
    "DOTUSDT",
    "AAVEUSDT"
]

# API Configuration
NOBITEX_BASE_URL = "https://apiv2.nobitex.ir"
WALLEX_BASE_URL = "https://api.wallex.ir"

# Rate limiting configuration
NOBITEX_RATE_LIMIT = 60  # requests per minute
WALLEX_RATE_LIMIT = 60   # requests per minute (estimated)

# Arbitrage detection settings
ARBITRAGE_THRESHOLD = 0.01  # 1% minimum profit threshold
CHECK_INTERVAL_SECONDS = 60  # Check every 60 seconds
