import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()

client = TradingClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY"),
    paper=True
)

account = client.get_account()
print(f"Account status: {account.status}")
print(f"Portfolio value: ${account.portfolio_value}")
print(f"Cash: ${account.cash}")