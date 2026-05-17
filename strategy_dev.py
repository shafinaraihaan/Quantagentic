import os
import json
from dotenv import load_dotenv
from google import genai
from data import get_latest_quote, get_ohlcv_bars
from indicators import calculate_indicators

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# These are the 5 strategies Strategy Dev runs in parallel
# They start simple — Quantitative Researcher will replace underperformers over time
ACTIVE_STRATEGIES = [
    {
        "id": 1,
        "name": "RSI Oversold Bounce",
        "description": "Buy when RSI < 35, sell when RSI > 60"
    },
    {
        "id": 2,
        "name": "MACD Crossover",
        "description": "Buy when MACD crosses above signal line, sell when it crosses below"
    },
    {
        "id": 3,
        "name": "VWAP Mean Reversion",
        "description": "Buy when price is below VWAP and order flow imbalance is positive, sell when price returns to VWAP"
    },
    {
        "id": 4,
        "name": "Order Flow Momentum",
        "description": "Buy when order flow imbalance > 0.3 and price is rising, sell when imbalance flips negative"
    },
    {
        "id": 5,
        "name": "Spread Compression",
        "description": "Buy when bid/ask spread is tightening and volume is increasing, indicates institutional accumulation"
    }
]

def analyze_market(symbol: str) -> dict:
    # Get data
    quote = get_latest_quote(symbol)
    bars = get_ohlcv_bars(symbol, lookback_minutes=50)
    indicators = calculate_indicators(bars)

    # Build prompt for Strategy Dev
    prompt = f"""You are Strategy Dev, an expert quantitative trader specializing in 1-minute scalping.

Current market data for {symbol}:
- Price: ${indicators['current_price']}
- RSI: {indicators['rsi']}
- MACD: {indicators['macd']} (Signal: {indicators['macd_signal']}, Hist: {indicators['macd_hist']})
- VWAP: {indicators['vwap']}
- Bid: ${quote['bid_price']} (size: {quote['bid_size']})
- Ask: ${quote['ask_price']} (size: {quote['ask_size']})
- Order Flow Imbalance: {quote['order_flow_imbalance']} (-1 = all sellers, +1 = all buyers)

You are running these 5 strategies simultaneously:
{json.dumps(ACTIVE_STRATEGIES, indent=2)}

Analyze ALL 5 strategies against the current data. For each strategy determine if it gives a buy, sell, or hold signal right now.

Then make a final recommendation based on the weight of evidence across all strategies.

Respond ONLY with this JSON format, no other text:
{{
  "symbol": "{symbol}",
  "strategy_signals": [
    {{"id": 1, "name": "strategy name", "signal": "buy/sell/hold", "confidence": 0.0-1.0, "reasoning": "..."}}
  ],
  "final_signal": "buy/sell/hold",
  "final_confidence": 0.0-1.0,
  "suggested_allocation_pct": 5-20,
  "reasoning": "overall reasoning for final signal",
  "needs_research": false,
  "research_request": null
}}

Note: Set needs_research to true and describe what to research in research_request if market conditions seem unusual or you need more information.
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


if __name__ == "__main__":
    print("Strategy Dev analyzing AAPL...")
    result = analyze_market("AAPL")
    print(json.dumps(result, indent=2))