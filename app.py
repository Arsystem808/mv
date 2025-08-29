import streamlit as st
from core_strategy import analyze_ticker

st.set_page_config(page_title="CapinteL-Q AI", layout="wide")

st.title("📊 CapinteL-Q AI — MVP")

ticker = st.text_input("Введите тикер (например: QQQ, AAPL, BTCUSD):", "QQQ")
horizon = st.selectbox("Горизонт:", ["short", "mid", "long"], index=1)

if st.button("Проанализировать"):
    try:
        res = analyze_ticker(ticker, horizon)
        st.subheader("🧠 Результат:")
        st.markdown(res['text'])
        if res.get('alt_text'):
            st.markdown(res['alt_text'])
    except Exception as e:
        st.error(f"Ошибка: {e}")