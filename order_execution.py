import os
import json
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus

load_dotenv()

trading_client = TradingClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY"),
    paper=True
)

def place_order(decision: dict, current_price: float) -> dict:
    if decision['decision'] == 'reject':
        return {"status": "rejected", "reason": decision['reasoning']}

    if decision['action'] == 'hold':
        return {"status": "hold", "reason": "no trade placed"}

    # Calculate shares from dollar amount
    shares = int(decision['dollar_amount'] / current_price)

    if shares <= 0:
        return {"status": "skipped", "reason": "dollar amount too small for even 1 share"}

    side = OrderSide.BUY if decision['action'] == 'buy' else OrderSide.SELL

    order_request = MarketOrderRequest(
        symbol=decision['symbol'],
        qty=shares,
        side=side,
        time_in_force=TimeInForce.DAY
    )

    order = trading_client.submit_order(order_request)

    return {
        "status": "filled",
        "order_id": str(order.id),
        "symbol": decision['symbol'],
        "action": decision['action'],
        "shares": shares,
        "estimated_value": round(shares * current_price, 2),
        "reasoning": decision['reasoning']
    }

def get_trade_history() -> list:
    request = GetOrdersRequest(status=QueryOrderStatus.CLOSED, limit=20)
    orders = trading_client.get_orders(filter=request)
    result = []
    for o in orders:
        result.append({
            "symbol": str(o.symbol),
            "side": str(o.side),
            "qty": float(o.qty),
            "status": str(o.status),
            "submitted_at": str(o.submitted_at)
        })
    return result

if __name__ == "__main__":
    # Test with a mock approved decision
    mock_decision = {
        "decision": "approve",
        "symbol": "AAPL",
        "action": "buy",
        "dollar_amount": 10000.0,
        "reasoning": "VWAP mean reversion signal"
    }

    print("=== Placing Order ===")
    result = place_order(mock_decision, current_price=300.0)
    print(json.dumps(result, indent=2))

    print("\n=== Trade History ===")
    history = get_trade_history()
    for trade in history:
        print(trade)