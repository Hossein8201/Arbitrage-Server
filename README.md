# Arbitrage Detection Application

A continuous cryptocurrency arbitrage detection service that monitors price differences between Nobitex and Wallex exchanges and sends notifications via Bale bot.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r arbitrage_app/requirements.txt
```

### 2. Configure Bale Bot (Optional)
Set environment variables for notifications:
```bash
export BALE_BOT_TOKEN="your_bot_token"
export BALE_CHAT_ID="your_chat_id"
```

### 3. Start the Service
```bash
python arbitrage_app.py
```

Or use the manager script:
```bash
python start_arbitrage.py start
```

## 📁 Project Structure

```
arbitrage_app/
├── scraper/
│   ├── api/
│   │   ├── nobitex_api.py      # Nobitex exchange API client
│   │   └── wallex_api.py       # Wallex exchange API client
│   └── detector/
│       └── arbitrage_detector.py # Core arbitrage detection logic
├── bot/
│   └── notifier/
│       ├── bale_notifier.py    # Bale bot notification client
│       └── notification_service.py # Notification service
├── sample_trading.py           # Trading pairs and configuration
└── requirements.txt            # Python dependencies
```

## 🔧 Configuration

### Trading Pairs
Edit `arbitrage_app/sample_trading.py` to modify:
- Trading pairs to monitor
- Arbitrage threshold (default: 1%)
- Check interval (default: 5 seconds)

### Environment Variables
- `BALE_BOT_TOKEN`: Bale bot token for notifications
- `BALE_CHAT_ID`: Chat ID for notifications

## 📊 Features

- **Continuous Monitoring**: Scans all trading pairs every 5 seconds
- **Rate Limiting**: Respects API rate limits (60 requests/minute)
- **Smart Notifications**: Cooldown system prevents spam
- **Error Handling**: Robust error handling and recovery
- **Logging**: Comprehensive logging to file and console
- **Graceful Shutdown**: Handles Ctrl+C and system signals

## 🧪 Testing

Test the service components:
```bash
python start_arbitrage.py test
```

Check service status:
```bash
python start_arbitrage.py status
```

## 📝 Logs

The application creates `arbitrage_app.log` with detailed information about:
- Scan results
- Arbitrage opportunities found
- Error messages
- Service statistics

## 🛑 Stopping the Service

Press `Ctrl+C` to stop the service gracefully. The service will:
- Complete current scan
- Send shutdown notification
- Log final statistics
- Clean up resources

## 📈 Monitoring

The service provides real-time statistics:
- Total uptime
- Number of scans completed
- Total arbitrage opportunities found
- Last scan time

## ⚠️ Important Notes

- The service respects API rate limits
- Notifications have a 5-minute cooldown per symbol
- Missing price data is handled gracefully
- The service runs continuously until stopped
- All sensitive data should be in environment variables
