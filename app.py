# app.py — Streamlit UI, генерит инвест-мемо без risk overlay

import os
import streamlit as st
from core_strategy import analyze_ticker
from memo import build_invest_memo

st.set_page_config(page_title="CapinteL-Q — Investment Memo", page_icon="📑", layout="centered")

st.markdown("# CapinteL-Q — Investment Memo *(без раскрытия стратегии)*")
st.caption("Источник данных: Polygon.io. Внутренние формулы скрыты, текст — «человеческий».")

ticker = st.text_input("Тикер (например, QQQ, AAPL, X:BTCUSD):", "QQQ").strip()
horizon_map = {
    "Трейд (1–5 дней)": "short",
    "Среднесрок (1–4 недели)": "mid",
    "Долгосрок (1–6 месяцев)": "long",
}
h_label = st.selectbox("Горизонт:", list(horizon_map.keys()), index=1)
horizon = horizon_map[h_label]

ok = st.button("Сформировать инвест-мемо", type="primary")

# Читаем ключ Polygon из Secrets/ENV
polygon_key = os.getenv("POLYGON_API_KEY", "")
if not polygon_key:
    st.info("Добавь переменную окружения **POLYGON_API_KEY** (в Streamlit — в **Secrets**).", icon="ℹ️")

if ok:
    try:
        d = analyze_ticker(ticker, horizon)
        memo_md = build_invest_memo(d)
        st.markdown("---")
        st.markdown(memo_md)
    except Exception as e:
        st.error(f"Ошибка: {e}")
