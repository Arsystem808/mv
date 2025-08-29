# memo.py
from typing import Any, Dict, Optional

def _fmt(x: Optional[float]) -> str:
    return f"{x:.2f}" if isinstance(x, (int, float)) else "—"

def _fmt_range(lo: Optional[float], hi: Optional[float]) -> str:
    if isinstance(lo, (int, float)) and isinstance(hi, (int, float)):
        return f"{lo:.2f}…{hi:.2f}"
    return "—"

def _ru_horizon(h: str) -> str:
    h = (h or "").lower()
    return {
        "short": "Трейд (1–5 дней)",
        "mid": "Среднесрок (1–4 недели)",
        "long": "Долгосрок (1–6 месяцев)"
    }.get(h, h or "—")

def build_invest_memo(decision: Dict[str, Any]) -> str:
    """
    Преобразует словарь decision в человекочитаемое инвест-мемо.
    """
    tkr = str(decision.get("ticker", "")).upper()
    hz = _ru_horizon(decision.get("horizon", ""))
    stance = str(decision.get("stance", "WAIT")).upper()

    # meta может отсутствовать или быть dict
    meta = decision.get("meta", {}) or {}
    price = meta.get("price")

    entry = decision.get("entry")
    if isinstance(entry, (list, tuple)) and len(entry) == 2:
        entry_lo, entry_hi = entry
    else:
        entry_lo, entry_hi = None, None

    tgt1 = decision.get("target1")
    tgt2 = decision.get("target2")
    stop = decision.get("stop")

    lines = [f"📌 {tkr} — {hz}. Оценка: {stance}"]

    if isinstance(price, (int, float)):
        lines.append(f"📊 Цена сейчас: {_fmt(price)}")

    if stance == "WAIT":
        lines.append("⏳ База: WAIT — на текущих уровнях входа нет, ждём лучшей формации.")
        if entry_lo or entry_hi:
            lines.append(f"🎯 Интересная зона: {_fmt_range(entry_lo, entry_hi)}")
    elif stance == "BUY":
        lines.append("🟢 Сценарий: LONG")
        if entry_lo or entry_hi:
            lines.append(f"🎯 Вход: {_fmt_range(entry_lo, entry_hi)}")
        if tgt1: lines.append(f"🎯 Цель 1: {_fmt(tgt1)}")
        if tgt2: lines.append(f"🎯 Цель 2: {_fmt(tgt2)}")
        if stop: lines.append(f"🛡 Стоп: {_fmt(stop)}")
    elif stance == "SELL":
        lines.append("🔴 Сценарий: SHORT")
        if entry_lo or entry_hi:
            lines.append(f"🎯 Вход (шорт): {_fmt_range(entry_lo, entry_hi)}")
        if tgt1: lines.append(f"🎯 Цель 1: {_fmt(tgt1)}")
        if tgt2: lines.append(f"🎯 Цель 2: {_fmt(tgt2)}")
        if stop: lines.append(f"🛡 Защита: {_fmt(stop)}")

    lines.append("⚠️ Если сценарий ломается — быстро выходим и ждём новую формацию.")
    return "\n".join(lines)

