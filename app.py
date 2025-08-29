# app.py
import streamlit as st
from memo import build_invest_memo
from core_strategy import analyze_ticker  # твоя стратегия

HUMAN = {
    "short": "Трейд (1–5 дней)",
    "mid":   "Среднесрок (1–4 недели)",
    "long":  "Долгосрок (1–6 месяцев)",
}
TO_CODE = {v: k for k, v in HUMAN.items()}

st.set_page_config(page_title="CapinteL-Q — Investment Memo", layout="centered")
st.title("CapinteL-Q — Investment Memo (без раскрытия стратегии)")

ticker = st.text_input("Тикер:", "QQQ").upper().strip()
hz_label = st.selectbox("Горизонт:", list(HUMAN.values()), index=2)  # по умолчанию long
hz = TO_CODE[hz_label]

if st.button("Сформировать инвест-мемо"):
    try:
        decision = analyze_ticker(ticker, hz)  # <- должен вернуть dict в стиле твоей системы
        # подсказка на случай разбирательств
        with st.expander("Диагностика (сырые данные решения)"):
            st.json(decision)

        memo_text = build_invest_memo(decision)
        st.subheader("Мемо")
        st.write(memo_text)

    except Exception as e:
        st.error(f"Ошибка формирования мемо: {e}")
