# memo.py
from typing import Any, Dict, Optional, Tuple

# Небольшие форматтеры, чтобы текст был аккуратным
def _fmt(x: Optional[float]) -> str:
    return f"{x:.2f}" if isinstance(x, (int, float)) else "—"

def _fmt_range(lo: Optional[float], hi: Optional[float]) -> str:
    if isinstance(lo, (int, float)) and isinstance(hi, (int, float)):
        return f"{lo:.2f}…{hi:.2f}"
    return "—"

def _ru_horizon(h: str) -> str:
    h = (h or "").lower()
    return {"short": "Трейд (1–5 дней)",
            "mid": "Среднесрок (1–4 недели)",
            "long": "Долгосрок (1–6 месяцев)"}.get(h, h or "—")

def build_invest_memo(decision: Dict[str, Any]) -> str:
    """
    Преобразует словарь decision в человекочитаемое инвест-мемо.
    Никаких внутренних формул/пивотов не раскрываем.

    Ожидаемые ключи в decision:
      - ticker: str
      - horizon: 'short' | 'mid' | 'long'
      - stance: 'BUY' | 'SELL' | 'WAIT'
      - entry: tuple(low, high) или None
      - target1, target2, stop: float | None
      - meta: { 'price': float, ... } (опционально)
    """
    tkr: str = (decision.get("ticker") or "").upper()
    hz: str = _ru_horizon(decision.get("horizon", ""))
    stance: str = (decision.get("stance") or "WAIT").upper()

    meta: Dict[str, Any] = decision.get("meta") or {}
    price = meta.get("price")

    # Разбираем вход/цели/стоп безопасно
    entry = decision.get("entry")
    if isinstance(entry, (list, tuple)) and len(entry) == 2:
        entry_lo, entry_hi = entry
    else:
        entry_lo, entry_hi = None, None

    tgt1 = decision.get("target1")
    tgt2 = decision.get("target2")
    stop = decision.get("stop")

    lines = []
    header = f"📌 {tkr} — {hz}. Оценка: {stance}"
    lines.append(header)

    if isinstance(price, (int, float)):
        lines.append(f"📊 Цена сейчас: {_fmt(price)}")

    if stance == "WAIT":
        lines.append("⏳ База: WAIT — на текущих уровнях входа нет, ждём лучшей формации.")
        if entry_lo or entry_hi:
            lines.append(f"🎯 Интересная зона для набора: {_fmt_range(entry_lo, entry_hi)}")
    elif stance == "BUY":
        lines.append("🟢 Сценарий: LONG")
        if entry_lo or entry_hi:
            lines.append(f"🎯 Зона входа: {_fmt_range(entry_lo, entry_hi)}")
        if tgt1: lines.append(f"🎯 Цель 1: {_fmt(tgt1)}")
        if tgt2: lines.append(f"🎯 Цель 2: {_fmt(tgt2)}")
        if stop: lines.append(f"🛡 Стоп: {_fmt(stop)}")
        lines.append("🧭 Действуем аккуратно: подтверждение по цене/свечам — в приоритете.")
    elif stance == "SELL":
        lines.append("🔴 Сценарий: SHORT")
        if entry_lo or entry_hi:
            lines.append(f"🎯 Зона входа (шорт): {_fmt_range(entry_lo, entry_hi)}")
        if tgt1: lines.append(f"🎯 Цель 1: {_fmt(tgt1)}")
        if tgt2: lines.append(f"🎯 Цель 2: {_fmt(tgt2)}")
        if stop: lines.append(f"🛡 Защита: {_fmt(stop)}")
        lines.append("🧭 Работаем без суеты: ждём отказ/подтверждение, объём — умеренный.")
    else:
        # На всякий случай — если прилетело что-то нестандартное
        lines.append("ℹ️ Сигнал не распознан. Ждём ясности или пересчитываем условия.")

    lines.append("⚠️ Если сценарий ломается — быстро выходим и ждём новую формацию.")
    return "\n".join(lines)
