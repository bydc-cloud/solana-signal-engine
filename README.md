# Helix Trading System

A Python-based automated trading system for cryptocurrency analysis and signal generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for Birdeye and Helius
- Telegram bot token and chat ID

### Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   BIRDEYE_API_KEY=your_birdeye_api_key
   HELIUS_API_KEY=your_helius_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

### Running the System

#### Option 1: Interactive Mode
```bash
./START_MONEY_PRINTER.sh
```

#### Option 2: Autonomous Mode (Background)
```bash
./RUN_AUTONOMOUS.sh
```

#### Stop the System
```bash
./STOP_SCANNER.sh
```

## 📁 Key Components

- **REALITY_MOMENTUM_SCANNER.py** - Main momentum scanner
- **FINAL_NUCLEAR_HELIX_ENGINE.py** - Core trading engine
- **PRODUCTION_TELEGRAM_TRADER.py** - Telegram integration
- **NUCLEAR_HELIX_SOCIAL_ENGINE.py** - Social signal analysis

## 🔧 Configuration

The system scans tokens every 5 minutes and sends signals with:
- Signal strength threshold: 75+
- Market cap analysis
- Volume validation
- Risk assessment

## 📱 Features

- Real-time token scanning
- Telegram notifications
- Jupiter swap link generation
- Anti-duplicate protection
- Comprehensive logging

## ⚠️ Disclaimer

This software is for educational purposes only. Trading cryptocurrency involves substantial risk of loss. Use at your own risk.