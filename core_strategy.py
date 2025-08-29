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

# core_strategy.py
from typing import Any, Dict, Optional

def analyze_ticker(ticker: str, horizon: str) -> Dict[str, Any]:
    """
    Заглушка-адаптер. Замени на твою реальную логику.
    Важно: вернуть dict с такими ключами (можно без некоторых, memo выдержит):
    - "ticker": str
    - "horizon": "short" | "mid" | "long"
    - "stance": "BUY" | "SELL" | "WAIT"
    - "entry": (lo, hi) | число | None
    - "target1"/"target2": float | None
    - "stop": float | None
    - "alt": str | None
    - "meta": {"price": float, ...}  # meta — словарь
    """
    # Пример: вернём WAIT c текущей ценой None, чтобы ты видел, что memo живой.
    return {
        "ticker": ticker.upper(),
        "horizon": horizon,
        "stance": "WAIT",
        "entry": (None, None),
        "target1": None,
        "target2": None,
        "stop": None,
        "alt": None,
        "meta": {"price": None},
    }

    def to_plan(t):
        if not t: return None
        stance, entry, t1, t2, stop = t
        return Plan(stance=stance, entry=entry, t1=t1, t2=t2, stop=stop)

    base = to_plan(base_tuple)
    alt  = to_plan(alt_tuple)

    text, alt_text = humanize(ticker.upper(), price, horizon, base, alt)
    return {'price': price, 'horizon': horizon, 'base': base, 'alt': alt, 'text': text, 'alt_text': alt_text}
