# Quantagentic 🤖📈

A multi-agent AI trading system that uses LLM-powered agents to analyze markets, develop strategies, and execute paper trades autonomously.

## Overview

Quantagentic is a fully autonomous trading agent stack built for intraday scalping simulation. Three specialized AI agents (powered by Gemini 2.0 Flash) collaborate in real-time to analyze market conditions, manage risk, and execute trades on Alpaca's paper trading platform — no real money involved.

## Agent Architecture

| Agent | Type | Role |
|---|---|---|
| Quantitative Researcher | LLM | Researches cutting-edge strategies from the web when existing ones underperform |
| Strategy Dev | LLM | Runs 5 strategies in parallel, analyzes market conditions, generates trade signals |
| Portfolio Manager | LLM | Evaluates signals against portfolio state, approves/rejects trades, manages risk |
| Data Fetcher | Hardcoded | Pulls real-time bid/ask quotes and 1-min OHLCV bars from Alpaca |
| Indicators | Hardcoded | Calculates RSI, MACD, VWAP from price data |
| Order Execution | Hardcoded | Places paper trades via Alpaca API |

## How It Works

Every 60 seconds:
1. **Data** fetches live price, bid/ask, and 1-min bars from Alpaca
2. **Indicators** calculates RSI, MACD, VWAP, order flow imbalance
3. **Strategy Dev** evaluates all 5 strategies and generates a trade signal
4. **Quantitative Researcher** is triggered if a strategy is underperforming
5. **Portfolio Manager** approves/rejects based on portfolio state and risk rules
6. **Order Execution** places the paper trade on Alpaca
7. All decisions and reasoning are logged to SQLite for analysis

## Tech Stack

- **Python 3.11+**
- **Gemini 2.5 Flash** — LLM brain for all AI agents (free tier)
- **Alpaca Paper Trading API** — real market data + simulated order execution (free)
- **pandas-ta** — technical indicators
- **SQLite** — local trade and agent log storage

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/shafinaraihaan/Quantagentic.git
cd Quantagentic
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install google-genai alpaca-py pandas pandas-ta python-dotenv
```

### 4. Get free API keys
- **Gemini**: [aistudio.google.com](https://aistudio.google.com) — free, no credit card
- **Alpaca**: [alpaca.markets](https://alpaca.markets) — free paper trading account

### 5. Create `.env` file
GEMINI_API_KEY=your_gemini_key
APCA_API_KEY_ID=your_alpaca_key
APCA_API_SECRET_KEY=your_alpaca_secret

### 6. Run
```bash
python main.py
```

The system will start cycling every 60 seconds. Press `Ctrl+C` to stop.

## Best run during market hours
**NYSE market hours: 9:30am — 4:00pm ET, Monday—Friday**

Outside market hours the system will still run but bid/ask data will be empty and agents will correctly hold positions.

## Project Structure
Quantagentic/
├── main.py                      # Orchestrates all agents in a loop
├── strategy_dev.py              # LLM agent — generates trade signals
├── portfolio_manager.py         # LLM agent — manages risk and capital
├── quantitative_researcher.py   # LLM agent — researches new strategies
├── data.py                      # Fetches market data from Alpaca
├── indicators.py                # Calculates technical indicators
├── order_execution.py           # Places paper trades
└── .env                         # API keys (not committed)

## Disclaimer
This project is for educational and portfolio purposes only. It uses paper trading with simulated money. Not financial advice.