from dataclasses import dataclass
from typing import Optional, Tuple, Dict
from polygon_client import fetch_daily
from narrator import humanize

@dataclass
class Plan:
    stance: str
    entry: Optional[Tuple[float,float]]
    t1: Optional[float]
    t2: Optional[float]
    stop: Optional[float]
    note: str = ""

def decide_plan(price: float, horizon: str):
    if horizon == "short":
        return ("WAIT", None, None, None, None), ("SHORT", (price*0.99, price*1.0), price*0.985, price*0.97, price*1.01)
    if horizon == "mid":
        return ("WAIT", None, None, None, None), ("BUY", (price*0.97, price*0.99), price*1.02, price*1.05, price*0.95)
    if horizon == "long":
        return ("WAIT", None, None, None, None), ("SHORT", (price*1.0, price*1.02), price*0.95, price*0.9, price*1.05)
    return ("WAIT", None, None, None, None), None

def analyze_ticker(ticker: str, horizon: str) -> Dict:
    df = fetch_daily(ticker, days=400)
    price = float(df['close'].iloc[-1])
    base_tuple, alt_tuple = decide_plan(price, horizon)

    def to_plan(t):
        if not t: return None
        stance, entry, t1, t2, stop = t
        return Plan(stance=stance, entry=entry, t1=t1, t2=t2, stop=stop)

    base = to_plan(base_tuple)
    alt  = to_plan(alt_tuple)

    text, alt_text = humanize(ticker.upper(), price, horizon, base, alt)
    return {'price': price, 'horizon': horizon, 'base': base, 'alt': alt, 'text': text, 'alt_text': alt_text}