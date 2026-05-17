import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from datetime import datetime, timedelta

load_dotenv()

data_client = StockHistoricalDataClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY")
)

def get_latest_quote(symbol: str) -> dict:
    request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
    quote = data_client.get_stock_latest_quote(request)
    q = quote[symbol]
    bid = float(q.bid_size)
    ask = float(q.ask_size)
    imbalance = round((bid - ask) / (bid + ask), 4) if (bid + ask) > 0 else 0.0
    return {
        "symbol": symbol,
        "bid_price": float(q.bid_price),
        "ask_price": float(q.ask_price),
        "bid_size": bid,
        "ask_size": ask,
        "spread": round(float(q.ask_price) - float(q.bid_price), 4),
        "order_flow_imbalance": imbalance
    }

def get_ohlcv_bars(symbol: str, lookback_minutes: int = 50) -> list:
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=datetime.now() - timedelta(days=5),
        end=datetime.now() - timedelta(minutes=15),
        feed=DataFeed.IEX
    )
    bars = data_client.get_stock_bars(request)
    if symbol not in bars.data:
        print(f"No bars found for {symbol}")
        return []
    result = []
    for bar in bars.data[symbol]:
        result.append({
            "timestamp": str(bar.timestamp),
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "volume": float(bar.volume)
        })
    return result[-lookback_minutes:]

if __name__ == "__main__":
    import json
    print("=== Latest Quote ===")
    quote = get_latest_quote("AAPL")
    print(json.dumps(quote, indent=2))
    print("\n=== Last 50 bars ===")
    bars = get_ohlcv_bars("AAPL", lookback_minutes=50)
    for bar in bars:
        print(bar)