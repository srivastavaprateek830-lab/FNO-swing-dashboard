import streamlit as st
import pandas as pd
from signal_engine import TradingEngine
import config

st.set_page_config(page_title="F&O + MTF Analytics Terminal", layout="wide")

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

st.title("⚡ F&O and MTF Swing Analytics Trading Terminal")
st.caption("Connected to DhanHQ API Data Feed")
st.markdown("---")

col1, col2 = st.columns()

with col1:
    st.header("📋 Watchlist Core Feed")
    watchlist_data = pd.DataFrame([
        {"Symbol": "RELIANCE", "ID": "2885", "FnO": True, "Price": 2450.0, "EMA20": 2400.0, "RSI": 58, "Vol": 2200000, "AvgVol": 1200000, "PrevHigh": 2440.0, "IVR": 35},
        {"Symbol": "TCS", "ID": "11536", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 45, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55},
        {"Symbol": "ZOMATO", "ID": "5097", "FnO": False, "Price": 160.0, "EMA20": 145.0, "RSI": 65, "Vol": 15000000, "AvgVol": 8000000, "PrevHigh": 155.0, "IVR": 0}
    ])
    st.dataframe(watchlist_data[["Symbol", "Price", "RSI", "FnO"]], use_container_width=True, hide_index=True)
    selected_symbol = st.selectbox("Select Asset for Diagnostics Run:", watchlist_data["Symbol"])

with col2:
    st.header("📊 Scoring & Routing Engine")
    row = watchlist_data[watchlist_data["Symbol"] == selected_symbol].iloc[0]
    
    metrics_payload = {
        "close": row["Price"], "ema_20": row["EMA20"], "rsi": row["RSI"],
        "volume": row["Vol"], "avg_volume": row["AvgVol"], "prev_high": row["PrevHigh"], "iv_rank": row["IVR"]
    }
    
    analysis = engine.route_asset(row["Symbol"], row["ID"], row["FnO"], metrics_payload)
    
    score_color = "green" if analysis["score"] >= 4 else ("orange" if analysis["score"] == 3 else "red")
    st.markdown(f"### Total Swing Score: :{score_color}[{analysis['score']} / 5]")
    st.info(f"**Recommended Route:** {analysis['route']}")
    
    st.subheader("Evaluation Breakdown")
    for key, value in analysis["breakdown"].items():
        st.text(f"• {key}: {value}")
