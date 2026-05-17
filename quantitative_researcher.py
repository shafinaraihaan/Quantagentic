import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def research_new_strategy(failed_strategy: str, market_condition: str) -> dict:
    prompt = f"""You are a quantitative trading researcher specializing in cutting edge price action and order flow strategies.

A trading strategy has been underperforming and needs to be replaced.

Failed strategy type: {failed_strategy}
Market condition it failed in: {market_condition}

Search your knowledge for a cutting edge replacement strategy. Think about:
- Price action concepts
- Order flow and volume analysis  
- Market microstructure
- Recent quantitative research

Respond ONLY with a JSON object in this exact format, no other text:
{{
  "strategy_name": "name of the strategy",
  "concept": "clear explanation of how it works",
  "indicators_needed": ["indicator1", "indicator2"],
  "entry_signal": "specific condition to enter a trade",
  "exit_signal": "specific condition to exit a trade",
  "best_market_condition": "when this strategy works best",
  "reasoning": "why this replaces the failed strategy"
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
    result = research_new_strategy(
        failed_strategy="momentum strategy using RSI",
        market_condition="low volatility sideways market"
    )
    print(json.dumps(result, indent=2))