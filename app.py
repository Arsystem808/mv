# app.py
# Streamlit-обёртка: вызывает твою стратегию и формирует инвест-мемо БЕЗ Pivot.
import os
import io
import streamlit as st

from core_strategy import analyze_ticker  # оставляем твою логику как есть
from memo import build_invest_memo

st.set_page_config(page_title="CapinteL-Q — Investment Memo", layout="centered")

st.title("CapinteL-Q — Investment Memo (без раскрытия стратегии)")
st.caption("Источник данных: Polygon.io • В тексте — только действия (вход/цели/стоп/альтернатива). Внутренние правила и расчёты скрыты.")

col1, col2 = st.columns([2,1])
with col1:
    ticker = st.text_input("Тикер", value="QQQ").strip()
with col2:
    horizon = st.selectbox("Горизонт", options=[("short","Трейд (1–5 дней)"),
                                                ("mid","Среднесрок (1–4 недели)"),
                                                ("long","Долгосрок (1–6 месяцев)")],
                           index=1, format_func=lambda x: x[1])[0]

if st.button("Сформировать инвест-мемо", use_container_width=True):
    if not ticker:
        st.error("Укажи тикер.")
        st.stop()
    try:
        # ВАЖНО: analyze_ticker должен вернуть словарь в формате, описанном в memo.py
        decision = analyze_ticker(ticker, horizon)
        # Страхуемся: если стратегия вернула «голый dict», это ок — memo ожидает dict
        if not isinstance(decision, dict):
            st.warning("Стратегия вернула неожиданный формат. Пытаюсь привести к dict…")
            decision = dict(decision)

        memo = build_invest_memo(ticker, horizon, decision)

        st.subheader(f"🎯 Asset: {ticker.upper()}")
        st.text(f"Горизонт: {dict(short='Трейд (1–5 дней)', mid='Среднесрок (1–4 недели)', long='Долгосрок (1–6 месяцев)')[horizon]}")
        st.text(f"———")

        st.markdown(memo["core"])
        st.markdown("### ✍️ Резюме (human-style)")
        st.write(memo["summary"])
        st.markdown("### 🎯 Ориентиры (без раскрытия внутренней математики)")
        st.write(memo["levels"])
        if memo["alt"]:
            st.markdown(memo["alt"])

        # Скачивание как .md
        buf = io.BytesIO(memo["markdown"].encode("utf-8"))
        st.download_button("⬇️ Скачать memo (.md)", data=buf, file_name=f"{ticker.upper()}_{horizon}_memo.md", mime="text/markdown")

    except Exception as e:
        st.error(f"Ошибка формирования мемо: {e}")
