import os
import json
from dotenv import load_dotenv
from google import genai
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.trading.requests import MarketOrderRequest

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
trading_client = TradingClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY"),
    paper=True
)

def get_portfolio_state() -> dict:
    account = trading_client.get_account()
    positions = trading_client.get_all_positions()

    position_list = []
    for p in positions:
        position_list.append({
            "symbol": p.symbol,
            "qty": float(p.qty),
            "entry_price": float(p.avg_entry_price),
            "current_price": float(p.current_price),
            "unrealized_pnl": float(p.unrealized_pl),
            "market_value": float(p.market_value)
        })

    return {
        "portfolio_value": float(account.portfolio_value),
        "cash": float(account.cash),
        "buying_power": float(account.buying_power),
        "allocated_pct": round(
            (float(account.portfolio_value) - float(account.cash)) 
            / float(account.portfolio_value) * 100, 2
        ),
        "positions": position_list
    }

def evaluate_signal(strategy_signal: dict) -> dict:
    portfolio = get_portfolio_state()

    prompt = f"""You are the Portfolio Manager for a scalping trading system with ${portfolio['portfolio_value']:,.2f} in total capital.

Current portfolio state:
- Cash available: ${portfolio['cash']:,.2f}
- Buying power: ${portfolio['buying_power']:,.2f}
- Currently allocated: {portfolio['allocated_pct']}% of portfolio
- Open positions: {json.dumps(portfolio['positions'], indent=2)}

Strategy Dev is recommending the following trade:
{json.dumps(strategy_signal, indent=2)}

Your job is to:
1. Decide whether to approve, reduce, or reject this trade
2. Determine the exact dollar amount to allocate based on:
   - Never risk more than 20% of portfolio on a single trade
   - Keep at least 30% cash reserve at all times
   - If already holding the same symbol, consider adding or closing instead
   - Reject trades with confidence below 0.6
   - Scale allocation based on confidence level

Respond ONLY with this JSON format, no other text:
{{
  "decision": "approve/reduce/reject",
  "symbol": "AAPL",
  "action": "buy/sell/hold",
  "dollar_amount": 0.00,
  "shares": 0,
  "reasoning": "explanation of decision",
  "risk_notes": "any risk concerns"
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
    # Test with a mock strategy signal
    mock_signal = {
        "symbol": "AAPL",
        "final_signal": "buy",
        "final_confidence": 0.82,
        "suggested_allocation_pct": 10,
        "reasoning": "VWAP mean reversion signal with strong order flow"
    }

    print("=== Portfolio State ===")
    portfolio = get_portfolio_state()
    print(json.dumps(portfolio, indent=2))

    print("\n=== Portfolio Manager Decision ===")
    decision = evaluate_signal(mock_signal)
    print(json.dumps(decision, indent=2))