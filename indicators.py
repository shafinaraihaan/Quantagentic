import pandas as pd
import pandas_ta as ta

def calculate_indicators(bars: list) -> dict:
    if len(bars) < 26:
        return {"error": "Not enough bars to calculate indicators"}

    df = pd.DataFrame(bars)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')  
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['volume'] = df['volume'].astype(float)

    # RSI
    df['rsi'] = ta.rsi(df['close'], length=14)

    # MACD
    macd = ta.macd(df['close'])
    if macd is not None:
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']
    else:
        df['macd'] = None
        df['macd_signal'] = None
        df['macd_hist'] = None
        
    # VWAP
    df['vwap'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])

    latest = df.iloc[-1]

    return {
        "rsi": round(float(latest['rsi']), 2) if not pd.isna(latest['rsi']) else None,
        "macd": round(float(latest['macd']), 4) if not pd.isna(latest['macd']) else None,
        "macd_signal": round(float(latest['macd_signal']), 4) if not pd.isna(latest['macd_signal']) else None,
        "macd_hist": round(float(latest['macd_hist']), 4) if not pd.isna(latest['macd_hist']) else None,
        "vwap": round(float(latest['vwap']), 2) if not pd.isna(latest['vwap']) else None,
        "current_price": round(float(latest['close']), 2)
    }

if __name__ == "__main__":
    import json
    from data import get_ohlcv_bars
    bars = get_ohlcv_bars("AAPL", lookback_minutes=50)
    indicators = calculate_indicators(bars)
    print(json.dumps(indicators, indent=2))