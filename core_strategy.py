# core_strategy.py
# Минимально самодостаточная версия: Polygon fetch + пивоты (Fibo) + HA/MACD/RSI/ATR
# и выдача Decision. Без "risk overlay".

from __future__ import annotations
import os, math, time, datetime as dt
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Literal
import requests
import pandas as pd
import numpy as np

Horizon = Literal["short","mid","long"]

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "").strip()

@dataclass
class Decision:
    ticker: str
    horizon: Horizon
    stance: Literal["BUY","SELL","WAIT"]
    entry: Optional[Tuple[float, float]]  # (min,max) или None
    target1: Optional[float]
    target2: Optional[float]
    stop: Optional[float]
    meta: Dict[str, object]  # price, pivots, notes (любые поля)

# ------------------ Data ------------------

def _poly_fetch_daily(ticker: str, days: int = 500) -> pd.DataFrame:
    if not POLYGON_API_KEY:
        raise RuntimeError("POLYGON_API_KEY not set in environment")

    end = dt.date.today()
    start = end - dt.timedelta(days=days+5)

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/range/1/day/{start}/{end}"
    params = dict(adjusted="true", sort="asc", limit=50000, apiKey=POLYGON_API_KEY)
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    results = js.get("results", [])
    if not results:
        raise RuntimeError("Polygon returned empty results")

    df = pd.DataFrame(results)
    # columns: t(open ms), o,h,l,c,v
    df["date"] = pd.to_datetime(df["t"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(None).dt.date
    df = df.rename(columns={"o":"open","h":"high","l":"low","c":"close","v":"volume"})
    df = df[["date","open","high","low","close","volume"]]
    df = df.drop_duplicates("date").reset_index(drop=True)
    return df

# ------------------ Indicators ------------------

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta>0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta<0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100/(1+rs))
    return rsi.fillna(50)

def _ema(series: pd.Series, n: int) -> pd.Series:
    return series.ewm(span=n, adjust=False).mean()

def _macd_hist(close: pd.Series) -> pd.Series:
    macd = _ema(close,12) - _ema(close,26)
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return hist

def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

def _heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    ha = pd.DataFrame(index=df.index)
    ha["HA_Close"] = (df["open"]+df["high"]+df["low"]+df["close"])/4
    ha_open = []
    for i in range(len(df)):
        if i==0:
            ha_open.append((df.loc[df.index[i],"open"]+df.loc[df.index[i],"close"])/2)
        else:
            ha_open.append((ha_open[i-1]+ha["HA_Close"].iloc[i-1])/2)
    ha["HA_Open"] = pd.Series(ha_open, index=df.index)
    ha["HA_Up"] = ha["HA_Close"] > ha["HA_Open"]
    return ha

def _streak_bool(b: pd.Series) -> int:
    # длина крайней серии True или False (по последнему значению)
    if b.empty: return 0
    last = b.iloc[-1]
    cnt = 0
    for val in reversed(b.tolist()):
        if val==last: cnt += 1
        else: break
    return cnt if last else -cnt  # знак по направлению

# ------------------ Pivots (Fibonacci) ------------------

def _fib_pivots(H: float, L: float, C: float) -> Dict[str,float]:
    P = (H+L+C)/3
    rng = H-L
    R1 = P + 0.382*rng
    R2 = P + 0.618*rng
    R3 = P + 1.000*rng
    S1 = P - 0.382*rng
    S2 = P - 0.618*rng
    S3 = P - 1.000*rng
    return {"P":round(P,2),"R1":round(R1,2),"R2":round(R2,2),"R3":round(R3,2),
            "S1":round(S1,2),"S2":round(S2,2),"S3":round(S3,2)}

def _last_completed_period_HLC(df: pd.DataFrame, horizon: Horizon) -> Tuple[float,float,float]:
    s = pd.to_datetime(df["date"])
    tmp = df.copy()
    tmp["dt"] = pd.to_datetime(tmp["date"])

    if horizon=="short":
        grp = tmp.set_index("dt").resample("W-FRI")
    elif horizon=="mid":
        grp = tmp.set_index("dt").resample("M")
    else:
        grp = tmp.set_index("dt").resample("Y")

    agg = grp.agg({"high":"max","low":"min","close":"last"}).dropna()
    if len(agg)<2:
        # fallback: взять последнюю «почти завершённую» неделю/месяц по дневным
        H, L, C = tmp["high"].iloc[-10:].max(), tmp["low"].iloc[-10:].min(), tmp["close"].iloc[-1]
        return float(H), float(L), float(C)
    # берём ПРЕДЫДУЩИЙ (завершённый) период
    H, L, C = agg.iloc[-2]["high"], agg.iloc[-2]["low"], agg.iloc[-2]["close"]
    return float(H), float(L), float(C)

# ------------------ Core logic ------------------

def analyze_ticker(ticker: str, horizon: Horizon) -> Decision:
    df = _poly_fetch_daily(ticker, 550)
    df = df.sort_values("date").reset_index(drop=True)

    price = float(df["close"].iloc[-1])
    atr = _atr(df, 14).iloc[-1]
    rsi = _rsi(df["close"],14).iloc[-1]
    hist = _macd_hist(df["close"])
    macd_streak = _streak_bool(hist > 0)  # >0 — зелёная область
    ha = _heikin_ashi(df)
    ha_streak = _streak_bool(ha["HA_Up"])

    H,L,C = _last_completed_period_HLC(df, horizon)
    piv = _fib_pivots(H,L,C)

    # Пороговая «толерантность» по горизонту
    tol = {"short":0.006, "mid":0.009, "long":0.012}[horizon]
    macd_min = {"short":4, "mid":6, "long":8}[horizon]
    ha_min   = {"short":4, "mid":5, "long":6}[horizon]

    stance: Literal["BUY","SELL","WAIT"] = "WAIT"
    entry = t1 = t2 = stop = None

    # --- A) Перегрев у крыши (WAIT / опционально SELL) ---
    near_roof = (price >= piv["R2"]*(1 - tol))
    if near_roof and ha_streak>=ha_min and macd_streak>=macd_min:
        stance = "WAIT"
        # агрессивный SELL опционально — как альтернатива:
        alt = f"SELL от {max(piv['R2'], price):.2f} со стопом выше {piv['R3']:.2f}"
    else:
        alt = None

    # --- B) Перепроданность у дна (покупка) ---
    near_floor = (price <= piv["S2"]*(1 + tol))
    if near_floor and ha_streak<=-ha_min and macd_streak<=-macd_min:
        stance = "BUY"
        # вход в районе S2..S3 с подтверждением
        e1, e2 = min(price, piv["S2"]), max(piv["S2"], piv["S3"])
        entry = (round(min(e1,e2),2), round(max(e1,e2),2))
        # цели зеркально
        t1 = piv["P"]
        t2 = piv["R1"]
        stop = round(min(piv["S3"], price - 0.8*atr), 2)

    # --- C) Базовый “от отката к опоре” (MID/LONG) ---
    if stance=="WAIT" and horizon in ("mid","long"):
        # Ищем вход около P/S1 прошлого периода
        if price < piv["P"]*(1 - tol):
            # ждём возврата в зону опоры (качество точки важнее скорости)
            entry = (round(piv["S1"],2), round(piv["P"],2))
            stance = "BUY"
            t1 = piv["R1"]
            t2 = piv["R2"]
            stop = round(piv["S2"],2)

    # --- D) Если ничего не сложилось — WAIT с ориентиром ---
    if stance=="WAIT":
        # ориентир: ждать цену у опоры или явного отказа от крыши
        entry = None; t1 = t2 = stop = None

    return Decision(
        ticker=ticker.upper(),
        horizon=horizon,
        stance=stance,
        entry=entry,
        target1=t1,
        target2=t2,
        stop=stop,
        meta={
            "price": round(price,2),
            "pivots": piv,
            "rsi": round(float(rsi),2),
            "ha_streak": int(ha_streak),
            "macd_streak": int(macd_streak),
            "atr": round(float(atr),2),
            "alt": alt
        }
    )
