# memo.py
import random
from core_strategy import Decision  # используем твой dataclass Decision

HUMAN_HORIZON = {
    "short": "Трейд (1–5 дней)",
    "mid":   "Среднесрок (1–4 недели)",
    "long":  "Долгосрок (1–6 месяцев)"
}

def _fmt_range(z):
    if not z or any(v is None for v in z):
        return "—"
    lo, hi = sorted([float(z[0]), float(z[1])])
    return f"{lo:.2f}…{hi:.2f}" if hi - lo >= 0.01 else f"{lo:.2f}"

def _stance_ru(s):
    return {"BUY":"Покупка","SHORT":"Шорт","SELL":"Продажа","WAIT":"WAIT"}.get(s.upper(), s)

def _tone_snippet():
    pool = [
        "Видится мне, рынок дышит чаще обычного — лучше не спешить.",
        "По ощущению рынка, толпа слегка перегрелась — действуем аккуратно.",
        "Импульс будто устал — берём только качественные точки.",
    ]
    return random.choice(pool)

def _derive_alt(base: Decision, price: float) -> Decision | None:
    """Если база WAIT — предложим аккуратную альтернативу.
       Если база BUY/SHORT — альтернатива в виде WAIT (без контртренда по умолчанию)."""
    if base.stance == "WAIT":
        # Нейтральная аккуратная альтернатива: вход вокруг заданной зоны, если она есть
        if base.entry:
            lo, hi = sorted(base.entry)
            if price <= (lo + hi)/2:
                # предложим осторожный BUY
                return Decision(
                    stance="BUY",
                    entry=(lo, hi),
                    target1=base.target1,  # числа берём из ядра — без раскрытия логики
                    target2=base.target2,
                    stop=base.stop,
                    meta=base.meta
                )
            else:
                # предложим осторожный SHORT
                return Decision(
                    stance="SHORT",
                    entry=(lo, hi),
                    target1=base.target1,
                    target2=base.target2,
                    stop=base.stop,
                    meta=base.meta
                )
        return None
    else:
        # Если уже есть явный план (BUY/SHORT) — альтернативой сделаем WAIT, без контртренда
        return Decision(stance="WAIT", entry=None, target1=None, target2=None, stop=None, meta=base.meta)

def build_invest_memo(ticker: str, price: float, horizon: str, base: Decision) -> str:
    """Возвращает готовый markdown для инвест-мемо (без «стратегий», только цены/действия)."""
    hz = HUMAN_HORIZON.get(horizon, horizon)
    headline = f"### Инвестиционная идея\n**Ticker:** {ticker.upper()}  \n**Горизонт:** {hz}  \n**Рекомендация:** {_stance_ru(base.stance)}"

    situation = (
        "### Текущая ситуация\n"
        f"{_tone_snippet()} Цена сейчас вокруг **{price:.2f}**. "
        "Смотрим на поведение цены и выбираем точку с явным перевесом."
    )

    # Базовый план
    base_block = [
        f"### Торговый план — базовый ({_stance_ru(base.stance)})",
        f"Вход: {_fmt_range(base.entry)}",
        f"Цель 1: {base.target1:.2f}" if base.target1 else "Цель 1: —",
        f"Цель 2: {base.target2:.2f}" if base.target2 else "Цель 2: —",
        f"Стоп: {base.stop:.2f}" if base.stop else "Стоп: —",
    ]
    base_text = "\n".join(base_block)

    # Альтернатива
    alt = _derive_alt(base, price)
    if alt:
        alt_block = [
            f"### Альтернативный сценарий ({_stance_ru(alt.stance)})",
            f"Вход: {_fmt_range(alt.entry)}",
            f"Цель 1: {alt.target1:.2f}" if alt.target1 else "Цель 1: —",
            f"Цель 2: {alt.target2:.2f}" if alt.target2 else "Цель 2: —",
            f"Стоп: {alt.stop:.2f}" if alt.stop else "Стоп: —",
        ]
        alt_text = "\n".join(alt_block)
    else:
        alt_text = ""

    footer = (
        "### Резюме\n"
        "Работаем спокойно: берём там, где перевес очевиден. "
        "Если сценарий ломается — быстро выходим и ждём следующую форму. "
        "Без суеты."
    )

    parts = [headline, situation, base_text]
    if alt_text:
        parts.append(alt_text)
    parts.append(footer)
    return "\n\n".join(parts)
