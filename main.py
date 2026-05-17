import os
import json
import time
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from data import get_latest_quote, get_ohlcv_bars
from indicators import calculate_indicators
from strategy_dev import analyze_market
from portfolio_manager import evaluate_signal, get_portfolio_state
from order_execution import place_order
from quantitative_researcher import research_new_strategy

load_dotenv()

# Setup SQLite database to store trade history and agent logs
def init_db():
    conn = sqlite3.connect("quantagentic.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            action TEXT,
            shares INTEGER,
            price REAL,
            value REAL,
            reasoning TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            agent TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_agent(agent: str, message: str):
    conn = sqlite3.connect("quantagentic.db")
    c = conn.cursor()
    c.execute("INSERT INTO agent_logs (timestamp, agent, message) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), agent, message))
    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{agent}] {message}")

def log_trade(trade: dict, price: float):
    if trade.get('status') != 'filled':
        return
    conn = sqlite3.connect("quantagentic.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO trades (timestamp, symbol, action, shares, price, value, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        trade['symbol'],
        trade['action'],
        trade['shares'],
        price,
        trade['estimated_value'],
        trade['reasoning']
    ))
    conn.commit()
    conn.close()

# Track strategy performance
strategy_performance = {1: [], 2: [], 3: [], 4: [], 5: []}

def run_cycle(symbol: str = "AAPL"):
    print(f"\n{'='*50}")
    print(f"CYCLE START: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")

    # Step 1: Get market data
    log_agent("DATA", f"Fetching data for {symbol}")
    bars = get_ohlcv_bars(symbol, lookback_minutes=50)
    quote = get_latest_quote(symbol)
    indicators = calculate_indicators(bars)
    current_price = indicators['current_price']
    log_agent("DATA", f"Price: ${current_price} | RSI: {indicators['rsi']} | VWAP: {indicators['vwap']}")

    # Step 2: Strategy Dev analyzes
    log_agent("STRATEGY DEV", "Analyzing market conditions...")
    strategy_signal = analyze_market(symbol)
    log_agent("STRATEGY DEV", f"Signal: {strategy_signal['final_signal'].upper()} | Confidence: {strategy_signal['final_confidence']} | {strategy_signal['reasoning'][:100]}...")

    # Step 3: Check if research needed
    if strategy_signal.get('needs_research') and strategy_signal.get('research_request'):
        log_agent("STRATEGY DEV", f"Requesting research: {strategy_signal['research_request']}")
        research = research_new_strategy(
            failed_strategy=strategy_signal['research_request'],
            market_condition=f"Current RSI: {indicators['rsi']}, Price vs VWAP: {'above' if current_price > indicators['vwap'] else 'below'}"
        )
        log_agent("QUANT RESEARCHER", f"Found strategy: {research['strategy_name']} — {research['concept'][:100]}...")

    # Step 4: Portfolio Manager evaluates
    log_agent("PORTFOLIO MGR", "Evaluating signal against portfolio...")
    decision = evaluate_signal(strategy_signal)
    log_agent("PORTFOLIO MGR", f"Decision: {decision['decision'].upper()} | Action: {decision['action']} | Amount: ${decision['dollar_amount']:,.2f}")

    # Step 5: Execute order
    if decision['decision'] == 'approve':
        log_agent("ORDER EXEC", f"Placing {decision['action']} order for {symbol}...")
        trade = place_order(decision, current_price)
        log_trade(trade, current_price)
        log_agent("ORDER EXEC", f"Status: {trade['status']} | Shares: {trade.get('shares', 0)}")
    else:
        log_agent("ORDER EXEC", f"No order placed — {decision['reasoning'][:80]}...")

    # Step 6: Portfolio summary
    portfolio = get_portfolio_state()
    log_agent("SYSTEM", f"Portfolio: ${portfolio['portfolio_value']:,.2f} | Cash: ${portfolio['cash']:,.2f} | Allocated: {portfolio['allocated_pct']}%")

    return {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "price": current_price,
        "indicators": indicators,
        "signal": strategy_signal,
        "decision": decision,
        "portfolio": portfolio
    }

if __name__ == "__main__":
    init_db()
    print("QUANTAGENTIC STARTING...")
    print("Press Ctrl+C to stop\n")

    cycle_count = 0
    while True:
        try:
            result = run_cycle("AAPL")
            cycle_count += 1
            print(f"\nCycle {cycle_count} complete. Waiting 60 seconds...\n")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nQuantagentic stopped.")
            break
        except Exception as e:
            print(f"Error in cycle: {e}")
            time.sleep(10)