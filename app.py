# app.py
import streamlit as st
from core_strategy import analyze_ticker       # твоё ядро: возвращает narrator.Decision
from memo import build_invest_memo             # форматируем инвест-мемо

st.set_page_config(page_title="CapinteL-Q — Investment Memo", page_icon="🧭", layout="centered")
st.title("CapinteL-Q — Investment Memo (без раскрытия стратегии)")

# Вводы
ticker = st.text_input("Тикер:", value="QQQ", help="Например: QQQ, AAPL, X:BTCUSD для кроссов.")
h_map = {
    "Трейд (1–5 дней)": "short",
    "Среднесрок (1–4 недели)": "mid",
    "Долгосрок (1–6 месяцев)": "long",
}
h_label = st.selectbox("Горизонт:", list(h_map.keys()), index=1)
horizon = h_map[h_label]

# Кнопка
if st.button("Сформировать инвест-мемо", type="primary", use_container_width=True):
    try:
        dec = analyze_ticker(ticker, horizon)                    # Decision(meta={'price', 'horizon'})
        price = float(dec.meta.get("price", 0.0))
        memo_md = build_invest_memo(ticker, price, horizon, dec) # без индикаторов, только план
        st.markdown(memo_md)
    except Exception as e:
        st.error(f"Ошибка: {e}")

st.caption("В тексте — только действия (вход/цели/стоп/альтернатива). Внутренние правила и расчёты скрыты.")
