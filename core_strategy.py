# memo.py
from typing import Optional
from core_strategy import Decision

def build_invest_memo(d: Decision) -> str:
    price = d.meta.get("price")
    piv = d.meta.get("pivots", {})

    parts = []
    parts.append(f"### 🎯 Asset: {d.ticker}")
    parts.append(f"**Горизонт:** {('Краткосрок (1–5 дней)' if d.horizon=='short' else 'Среднесрок (1–4 недели)' if d.horizon=='mid' else 'Долгосрок (1–6 месяцев)')}  ")
    parts.append(f"**Текущая цена:** ${price}\n")

    parts.append("## 🧠 Core Recommendation")
    parts.append(f"**Сценарий:** **{d.stance}**")

    if d.entry:
        parts.append(f"**Вход:** ${d.entry[0]} – ${d.entry[1]}")
    if d.target1: parts.append(f"**TP1:** ${d.target1}")
    if d.target2: parts.append(f"**TP2:** ${d.target2}")
    if d.stop:    parts.append(f"**Stop:** ${d.stop}")

    # human-style краткое резюме
    parts.append("\n## 📝 Резюме (human-style)")
    if d.stance == "BUY":
        parts.append("Работаем от поддержки. Важнее качество точки входа, чем скорость. Уровни по прошлому периоду удерживаются.")
    elif d.stance == "SELL":
        parts.append("Перегрев у «крыши». Играем от отказа с коротким стопом. Без подтверждения — не лезем.")
    else:
        parts.append("Сейчас выгоднее подождать. Ждём откат к опорной зоне или явное подтверждение разворота.")

    # Приложим ориентиры (без раскрытия формул)
    parts.append("\n#### Ориентиры (не раскрывая внутренней математики)")
    piv_line = " / ".join([f"{k}: {v}" for k,v in piv.items()])
    parts.append(f"{piv_line}")

    # Альтернатива (если есть)
    alt = d.meta.get("alt")
    if alt:
        parts.append(f"\n_Aльтернатива:_ {alt}")

    return "\n\n".join(parts)
