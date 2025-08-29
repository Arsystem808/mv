# memo.py
# Формирует инвест-мемо «по-человечески», без раскрытия внутренних расчётов и без Pivot.

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

Number = Optional[float]
Entry = Optional[Tuple[Number, Number]]

def _fmt(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:,.2f}".replace(",", " ").replace("\xa0", " ")

def _stance_badge(stance: str) -> str:
    s = (stance or "").upper()
    return {"BUY": "🟢 BUY", "SELL": "🔴 SELL", "WAIT": "⏳ WAIT"}.get(s, s)

def _levels_block(dec: Dict[str, Any]) -> str:
    """Читаемые уровни без упоминания источника (Pivot и т.п.)."""
    entry: Entry   = dec.get("entry")
    t1: Number     = dec.get("target1")
    t2: Number     = dec.get("target2")
    stop: Number   = dec.get("stop")

    if entry is None and t1 is None and t2 is None and stop is None:
        return "• Вход: ждём подходящей формации\n• Цели: появятся после подтверждения\n• Защита: по факту структуры"

    if isinstance(entry, tuple) and len(entry) == 2:
        entry_txt = f"{_fmt(entry[0])}…{_fmt(entry[1])}"
    else:
        entry_txt = _fmt(entry if isinstance(entry, (int, float)) else None)

    lines = [
        f"• Вход: {entry_txt or '—'}",
        f"• Цель 1: {_fmt(t1)}",
        f"• Цель 2: {_fmt(t2)}",
        f"• Защита/стоп: {_fmt(stop)}",
    ]
    return "\n".join(lines)

def build_invest_memo(ticker: str, horizon: str, decision: Dict[str, Any]) -> Dict[str, str]:
    """
    На входе — ticker, horizon ('short'/'mid'/'long') и словарь decision
    вида: {'stance': 'BUY|SELL|WAIT', 'entry': (low, high)|None, 'target1': float|None,
           'target2': float|None, 'stop': float|None, 'meta': {'price': float, 'horizon': str}, 'alt': '...'}
    Возвращает готовые текстовые блоки для UI/скачивания.
    """
    meta: Dict[str, Any] = decision.get("meta", {}) or {}
    price = meta.get("price")
    stance = (decision.get("stance") or "").upper()

    # Шапка
    dt = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    title = f"📄 CapinteL-Q • Investment Memo\nДата: {dt}\nАктив: {ticker.upper()} | Горизонт: {horizon}\nТекущая цена: {_fmt(price)}"

    # Core Recommendation
    core = f"### 🧠 Core Recommendation: {_stance_badge(stance)}"

    # Human-style резюме (без упоминания Pivot)
    if stance == "BUY":
        summary = (
            "Сценарий: **покупка** от опорной зоны/после подтверждения спроса. "
            "Работаем аккуратно: фиксируем часть на первой цели, переносим стоп за зону."
        )
    elif stance == "SELL":
        summary = (
            "Сценарий: **продажа** от перегрева/верхней границы при признаках отказа. "
            "Цели ступенчато; защищаем позицию выше локального экстремума."
        )
    else:
        summary = (
            "Сейчас выгоднее **подождать**. Ждём либо отката к удобной зоне для входа, "
            "либо явного подтверждения разворота/продолжения."
        )

    # Уровни (без указания их природы)
    levels = _levels_block(decision)

    # Альтернатива (если есть краткая строка в decision['alt'])
    alt_txt = decision.get("alt")
    alt_block = f"**Альтернатива:** {alt_txt}" if alt_txt else ""

    # Сборка Markdown
    md = "\n\n".join([
        title,
        core,
        "### ✍️ Резюме (human-style)\n" + summary,
        "### 🎯 Ориентиры (без раскрытия внутренней математики)\n" + levels,
        alt_block
    ]).strip()

    # Короткая версия для превью на экране
    preview = "\n".join([
        f"**{ticker.upper()}** — {_stance_badge(stance)} | Цена: {_fmt(price)}",
        summary,
        levels
    ])

    return {"title": title, "core": core, "summary": summary, "levels": levels, "alt": alt_block, "markdown": md, "preview": preview}
