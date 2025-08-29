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

def _to_dict(decision: Any) -> Dict[str, Any]:
    # принимает dict / dataclass / SimpleNamespace / pydantic / прочее
    if isinstance(decision, dict):
        return decision
    try:
        # dataclass / pydantic alike
        return dict(decision)
    except Exception:
        try:
            return vars(decision)
        except Exception:
            return {"raw": decision}

def build_invest_memo(decision_in: Any) -> str:
    """
    Преобразует решение стратегии в человекочитаемое инвест-мемо
    и не падает, даже если пришёл необычный формат.
    """
    d = _to_dict(decision_in)

    tkr = str(d.get("ticker", "")).upper()
    hz = _ru_horizon(str(d.get("horizon", "")))
    stance = str(d.get("stance", "WAIT")).upper()

    meta = d.get("meta") or {}
    if not isinstance(meta, dict):
        meta = {}
    price = meta.get("price")

    # entry может быть числом, кортежем или None
    entry = d.get("entry")
    entry_lo = entry_hi = None
    if isinstance(entry, (list, tuple)) and len(entry) == 2:
        entry_lo, entry_hi = entry
    elif isinstance(entry, (int, float)):
        entry_lo = entry_hi = float(entry)

    tgt1 = d.get("target1")
    tgt2 = d.get("target2")
    stop = d.get("stop")
    alt  = d.get("alt")

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
    else:
        # неизвестная стойка — просто распечатаем ключевые поля
        if entry_lo or entry_hi:
            lines.append(f"🎯 Вход: {_fmt_range(entry_lo, entry_hi)}")
        if tgt1: lines.append(f"🎯 Цель 1: {_fmt(tgt1)}")
        if tgt2: lines.append(f"🎯 Цель 2: {_fmt(tgt2)}")
        if stop: lines.append(f"🛡 Защита: {_fmt(stop)}")

    if alt:
        lines.append(f"🔁 Альтернатива: {alt}")

    lines.append("⚠️ Если сценарий ломается — быстро выходим и ждём новую формацию.")
    return "\n".join(lines)
