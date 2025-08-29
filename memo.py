# memo.py
from typing import Any, Dict, Optional

# На вход принимаем "решение" как обычный dict (у тебя Decision наследуется от dict)
# и формируем короткое инвест-мемо в человекочитаемом стиле.

def build_invest_memo(decision: Dict[str, Any]) -> str:
    """
    decision: {
      'ticker': 'QQQ',
      'horizon': 'long'|'mid'|'short',
      'stance': 'BUY'|'SELL'|'WAIT',
      'entry': (float|None, float|None),
      'target1': float|None,
      'target2': float|None,
      'stop': float|None,
      'meta': {'price': float, ...}
    }
    """
    tkr: str = decision.get("ticker", "").upper()
    hz: str = decision.get("horizon", "")
    stance: str = decision.get("stance", "WAIT")
    price: Optional[float] = None
    try:
        price = float(decision.get("meta", {}).get("price"))  # может быть Decimal/строка
    except Exception:
        pass

    ent = decision.get("entry")
    if isinstance(ent, (list, tuple)) and len(ent) == 2:
        entry_lo, entry_hi = ent
    else:
        entry_lo = entry_hi = None

    tgt1 = decision.get("target1")
    tgt2 = decision.get("target2")
    stop = decision.get("stop")

    # Заголовок
    lines = []
    lines.append(f"📌 {tkr} — горизонт: {hz}. Текущая оценка: {stance}")

    # Цена
    if price is not None:
        lines.append(f"📊 Цена сейчас: {price:.2f}")

    # План
    if stance == "WAIT":
        lines.append("⏳ База: WAIT — ждём лучшую формацию/цену у опорных уровней.")
    elif stance == "BUY":
        if entry_lo and entry_hi:
            lines.append(f"🟢 BUY-зона: {entry_lo:.2f}…{entry_hi:.2f}")
        if tgt1:
            lines.append(f"🎯 Цель 1: {tgt1:.2f}")
        if tgt2:
            lines.append(f"🎯 Цель 2: {tgt2:.2f}")
        if stop:
            lines.append(f"🛡 Стоп: {stop:.2f}")
    elif stance == "SELL":
        if entry_lo and entry_hi:
            lines.append(f"🔴 SELL-зона: {entry_lo:.2f}…{entry_hi:.2f}")
        if tgt1:
            lines.append(f"🎯 Цель 1: {tgt1:.2f}")
        if tgt2:
            lines.append(f"🎯 Цель 2: {tgt2:.2f}")
        if stop:
            lines.append(f"🛡 Защита: {stop:.2f}")

    # Комментарий-памятка
    lines.append("⚠️ Если сценарий ломается — быстро выходим и ждём новую формацию.")
    return "\n".join(lines)
