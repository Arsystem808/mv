def _fmt_zone(z):
    if not z:
        return "—"
    a, b = z
    return f"{a:.2f}…{b:.2f}" if abs(a-b)>0.01 else f"{a:.2f}"

def _plan_line(tag, plan):
    if not plan: return ""
    if plan.stance == "WAIT":
        return "✅ База: WAIT — лучше подождать подтверждения."
    icon = "🟢 BUY" if plan.stance=="BUY" else "🔴 SHORT"
    entry = _fmt_zone(plan.entry)
    t1 = f"{plan.t1:.2f}" if plan.t1 else "—"
    t2 = f"{plan.t2:.2f}" if plan.t2 else "—"
    stop = f"{plan.stop:.2f}" if plan.stop else "—"
    lead = "✅ База" if tag=="base" else "🧭 Альтернатива"
    return f"{lead}: {icon} | вход {entry} | цели {t1}/{t2} | стоп {stop}"

def humanize(ticker: str, price: float, horizon: str, base, alt):
    head = f"📈 {ticker} — текущая цена: {price:.2f}\n"
    base_line = _plan_line("base", base)
    alt_line = _plan_line("alt", alt) if alt else ""
    tail = "\n\n⚠️ Действуем без спешки: входим там, где перевес очевиден."
    return head+base_line, (alt_line+tail if alt_line else tail)