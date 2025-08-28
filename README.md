# TradingView to MT5 Integration

A robust, automated trading solution that connects TradingView alerts directly to MetaTrader 5, enabling seamless execution of trades based on your custom indicators and strategies.

<img width="1368" height="858" alt="image" src="https://github.com/user-attachments/assets/49f466a4-2cd9-47f7-8de9-a05ba4273081" />



## 🎯 Overview

This project creates a secure bridge between TradingView and MetaTrader 5 using a local Flask server and Ngrok tunneling. When your TradingView alerts trigger, they automatically execute trades in your MT5 account with customizable parameters including stop loss, take profit, and position sizing.

### How It Works

1. **TradingView Alert** → Triggers webhook with trading signal
2. **Ngrok Tunnel** → Securely forwards webhook to your local server
3. **Flask Server** → Processes the trading signal
4. **MT5 Integration** → Executes the trade in your MetaTrader 5 account

## ✨ Key Features

- 🔗 **Direct Integration**: Connect any TradingView indicator or strategy to MT5
- 🔒 **Secure Tunneling**: Uses Ngrok for safe webhook delivery
- ⚡ **Real-time Execution**: Instant trade execution from alerts
- 📊 **Flexible Orders**: Supports market orders, stop loss, take profit, partial closes
- 🏷️ **Symbol Management**: Handles broker-specific symbol suffixes
- 📧 **Email Notifications**: Get notified of server events and errors
- 🔧 **Position Management**: API endpoints for viewing and closing positions
- 📱 **Easy Monitoring**: Built-in health check endpoints

## 📋 Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.11+ ([Download](https://www.python.org/downloads/release/python-3110/)) |
| **MetaTrader 5** | Installed and configured |
| **TradingView** | Pro/Premium account (for webhook alerts) |
| **Ngrok** | Free account ([Sign up](https://ngrok.com/)) |
| **Email** | Gmail account (for notifications) |
| **UptimeRobot** | Free account ([Sign up](https://uptimerobot.com)) - *Optional for monitoring* |

## 📁 Project Structure

```
tradingview-alerts-to-metatrader5/
├── app/                          # Core application
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Environment configuration
│   ├── mt5_handler.py           # MT5 trading logic
│   ├── server.py                # Flask webhook server
│   └── utils.py                 # Utility functions
├── scripts/                     # Helper scripts
│   ├── get_symbols.py           # Fetch broker symbols
│   └── test_mt5_connection.py   # Connection testing
├── .env.example                 # Configuration template
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

## 🚀 Quick Start

### Step 1: Installation

1. **Clone the repository**
   ```bash
   cd %HOMEPATH%\Downloads
   git clone https://github.com/Jayfrej/4607.git
   cd 4607
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate.bat
   ```
   > 💡 Your prompt should show `(venv)` when activated

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configuration

1. **Create environment file**
   ```bash
   copy .env.example .env
   ```

2. **Configure your settings** (edit `.env` file):

```ini
# =============================================================================
# MT5 TRADING ACCOUNT CONFIGURATION
# =============================================================================
MT5_ACCOUNT=12345678                                    # Your MT5 account number
MT5_PASSWORD=YourPassword                               # Your MT5 password
MT5_SERVER=YourBroker-Demo                             # Your broker's server name
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe  # Path to MT5 executable

# =============================================================================
# SYMBOL SETTINGS
# =============================================================================
MT5_DEFAULT_SUFFIX=                                     # Leave empty unless broker uses suffixes

# =============================================================================
# SERVER CONFIGURATION
# =============================================================================
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DEBUG=True

# =============================================================================
# NGROK TUNNELING
# =============================================================================
NGROK_AUTH_TOKEN=your_ngrok_auth_token_here            # Get from ngrok dashboard

# =============================================================================
# EMAIL NOTIFICATIONS
# =============================================================================
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password                # Generate app password
RECEIVER_EMAIL=alerts@yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Step 3: Get Required Credentials

#### 🔑 Ngrok Auth Token
1. Visit [Ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Copy your auth token
3. Paste it in the `.env` file

#### 📧 Gmail App Password
1. Visit [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Generate a new app password
3. Use this password (not your regular Gmail password)

#### 📂 MT5 Path
1. Right-click on MetaTrader 5 executable
2. Select "Copy as path"
3. Paste in the `.env` file

### Step 4: MetaTrader 5 Setup

1. **Enable Expert Advisor for webhooks**:
   - Press `F4` in MT5 to open MetaEditor
   - Create new Expert Advisor
   - Paste the following code:

```mql5
//+------------------------------------------------------------------+
//|                                           TradingWebhookEA.mq5   |
//|                        Webhook Integration for Python Server     |
//+------------------------------------------------------------------+
#property strict

input string WebhookURL = "http://127.0.0.1:5000/webhook";
input int PollingInterval = 5;
input double DefaultVolume = 0.01;
input int Slippage = 10;
input string TradeComment = "WebhookEA";
input int MagicNumber = 12345;

datetime last_poll_time = 0;

int OnInit()
{
   Print("WebhookEA initialized. Polling URL: ", WebhookURL);
   return(INIT_SUCCEEDED);
}

void OnTick()
{
   if (TimeCurrent() - last_poll_time < PollingInterval)
      return;
   
   string headers = "";
   char data[];
   char result[];
   string result_headers;
   int timeout = 5000;
   
   int response = WebRequest("GET", WebhookURL, headers, timeout, data, result, result_headers);
   
   if (response == 200 && ArraySize(result) > 0)
   {
      string json_result = CharArrayToString(result);
      string action = GetValue(json_result, "action");
      string symbol = GetValue(json_result, "symbol");
      double volume = StringToDouble(GetValue(json_result, "volume"));
      
      if (volume <= 0) volume = DefaultVolume;
      if (symbol == "" || action == "") return;
      if (symbol != Symbol()) symbol = Symbol();
      
      if (action == "buy") ExecuteBuyOrder(symbol, volume);
      else if (action == "sell") ExecuteSellOrder(symbol, volume);
   }
   
   last_poll_time = TimeCurrent();
}

void ExecuteBuyOrder(string symbol, double volume)
{
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = volume;
   request.type = ORDER_TYPE_BUY;
   request.price = SymbolInfoDouble(symbol, SYMBOL_ASK);
   request.deviation = Slippage;
   request.magic = MagicNumber;
   request.comment = TradeComment;
   
   OrderSend(request, result);
}

void ExecuteSellOrder(string symbol, double volume)
{
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = symbol;
   request.volume = volume;
   request.type = ORDER_TYPE_SELL;
   request.price = SymbolInfoDouble(symbol, SYMBOL_BID);
   request.deviation = Slippage;
   request.magic = MagicNumber;
   request.comment = TradeComment;
   
   OrderSend(request, result);
}

string GetValue(string json, string key)
{
   string pattern = "\"" + key + "\":\"";
   int start = StringFind(json, pattern);
   if (start == -1) return "";
   
   start += StringLen(pattern);
   int end = StringFind(json, "\"", start);
   if (end == -1) return "";
   
   return StringSubstr(json, start, end - start);
}
```

2. **Save and compile** the Expert Advisor
3. **Add to chart** and enable automated trading

## ▶️ Running the Application

### First Time Setup
```bash
python main.py
```

The application will:
- ✅ Initialize MT5 connection
- ✅ Start the Flask webhook server
- ✅ Create Ngrok tunnel
- ✅ Generate webhook URL
- ✅ Save URL to `webhook_url.txt`

### Subsequent Runs
```bash
cd C:\Users\YourUser\Downloads\4607
venv\Scripts\activate.bat
python main.py
```

### Check Available Symbols
```bash
python get_symbols.py
```

## 📈 TradingView Alert Setup

### 1. Get Your Webhook URL
After running `python main.py`, find your webhook URL in `webhook_url.txt`. It will look like:
```
https://abc123.ngrok-free.app/trade
```

### 2. Create TradingView Alert
1. In TradingView, create or edit an alert
2. Go to **Notifications** tab
3. Enable **Webhook URL**
4. Paste your webhook URL
5. Configure the message (see examples below)

### 3. Alert Message Examples

#### 🎯 Strategy-Based (Recommended)
```json
{
    "symbol": "{{ticker}}",
    "action": "{{strategy.order.action}}",
    "volume": "{{strategy.order.contracts}}"
}
```

#### 📊 Fixed Volume Trades
```json
{
    "symbol": "{{ticker}}",
    "action": "buy",
    "volume": "0.01"
}
```

#### 🎛️ Advanced with Stop Loss/Take Profit
```json
{
    "symbol": "XAUUSD",
    "action": "sell",
    "volume": "0.02",
    "sl": "2380.00",
    "tp": "2360.00"
}
```

#### 🔒 Close Position
```json
{
    "symbol": "{{ticker}}",
    "action": "close",
    "volume": "0.01"
}
```

## 🔧 Monitoring & Health Checks

### Built-in Endpoints
- `https://your-ngrok-url.app/health` - Health status
- `https://your-ngrok-url.app/positions` - View open positions
- `https://your-ngrok-url.app/close/<symbol>` - Close positions

### Recommended Monitoring
Use [UptimeRobot](https://uptimerobot.com) to monitor your health endpoint:
```
https://your-ngrok-url.app/health
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### ❌ "Symbol not found"
**Problem**: `Symbol eurusdEURUSD not found`
**Solution**: 
- Run `python get_symbols.py` to see exact symbol names
- Ensure `MT5_DEFAULT_SUFFIX` is correctly set (usually empty)
- Match TradingView symbol with MT5 Market Watch exactly

#### ❌ "Invalid stops (retcode: 10016)"
**Problem**: Stop loss/take profit too close to market price
**Solution**: 
- Increase distance between entry and SL/TP
- Check your broker's minimum stop level requirements
- Ensure SL is below entry for buy orders, above entry for sell orders

#### ❌ "Invalid volume format"
**Problem**: `'{{strategy.order.contracts}}'` not resolving
**Solution**: 
- Ensure your strategy actually places orders
- Use fixed volume like `"0.01"` for testing
- Check alert triggers when valid trades exist

#### ❌ "Unknown action"
**Problem**: Action field contains invalid value
**Solution**: 
- Use only: `buy`, `sell`, `long`, `short`, or `close`
- Verify `{{strategy.order.action}}` resolves correctly
- Test with fixed action like `"buy"` first

## 🏭 Production Deployment

### For 24/7 Operation

1. **Use a VPS (Recommended)**
   - Deploy on Windows VPS with MT5 installed
   - Ensures continuous operation
   - Better internet connectivity

2. **Replace Ngrok (Optional)**
   - Register domain name
   - Use reverse proxy (Nginx/Apache)
   - Configure SSL certificates
   - Set up proper authentication

3. **Enhanced Security**
   - Add API key authentication
   - Implement request signing
   - Use IP whitelisting
   - Monitor for suspicious activity

### Environment-Specific Commands

**Development**:
```bash
python main.py
```

**Production**:
```bash
python main.py --production
```

## 📝 API Reference

### Webhook Endpoint
```
POST /trade
Content-Type: application/json

{
    "symbol": "EURUSD",
    "action": "buy|sell|close",
    "volume": "0.01",
    "sl": "1.0500",      // Optional
    "tp": "1.0600"       // Optional
}
```

### Health Check
```
GET /health
Response: {"status": "healthy", "mt5_connected": true}
```

### Position Management
```
GET /positions
Response: [{"symbol": "EURUSD", "volume": 0.01, "profit": 1.50}]
```

## 🤝 Support

### Getting Help
- 📖 Read this documentation thoroughly
- 🔍 Check the troubleshooting section
- 📋 Review logs for error messages
- 🧪 Test with simple fixed-value alerts first

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading involves substantial risk of loss. Use at your own risk and ensure you understand the implications of automated trading before deploying with real money.

## 📄 License

This project is for educational and personal use only. Please ensure compliance with your broker's terms of service and local regulations.

