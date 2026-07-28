import streamlit as st
import pandas as pd
from signal_engine import TradingEngine

st.set_page_config(page_title="F&O + MTF Analytics Terminal", layout="wide")

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

st.title("⚡ F&O and MTF Swing Analytics Trading Terminal")
st.caption("Alpha 8-Point Matrix Pipeline connected to DhanHQ Engine Layer")
st.markdown("---")

# Global Market Condition Injector Variables
st.sidebar.header("🌍 Market Environment Sentinel")
nifty_state = st.sidebar.radio("Nifty 50 Trend Regime Filter:", ("BULLISH (Above 20EMA)", "BEARISH (Below 20EMA)"))
nifty_payload_string = "BULLISH" if "BULLISH" in nifty_state else "BEARISH"

col1, col2 = st.columns(2)

with col1:
    st.header("📋 Watchlist Core Feed")
    # Enriched data tracking table structures
    watchlist_data = pd.DataFrame([
        {"Symbol": "RELIANCE", "ID": "2885", "FnO": True, "Price": 2450.0, "EMA20": 2400.0, "RSI": 58, "Vol": 2200000, "AvgVol": 1200000, "PrevHigh": 2440.0, "IVR": 35, "OI_Chg": 4.5, "Price_Chg": 1.2, "DayMove": 25.0, "ATR": 35.0},
        {"Symbol": "TCS", "ID": "11536", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 45, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0},
        {"Symbol": "ZOMATO", "ID": "5097", "FnO": False, "Price": 160.0, "EMA20": 145.0, "RSI": 65, "Vol": 15000000, "AvgVol": 8000000, "PrevHigh": 155.0, "IVR": 0, "OI_Chg": 0.0, "Price_Chg": 3.4, "DayMove": 4.0, "ATR": 5.0}
    ])
    st.dataframe(watchlist_data[["Symbol", "Price", "RSI", "FnO", "OI_Chg"]], use_container_width=True, hide_index=True)
    selected_symbol = st.selectbox("Select Asset for Comprehensive Diagnostics Run:", watchlist_data["Symbol"])

with col2:
    st.header("📊 8-Point Scoring & Routing Engine")
    row = watchlist_data[watchlist_data["Symbol"] == selected_symbol].iloc[0]
    
    metrics_payload = {
        "close": row["Price"], "ema_20": row["EMA20"], "rsi": row["RSI"],
        "volume": row["Vol"], "avg_volume": row["AvgVol"], "prev_high": row["PrevHigh"],
        "iv_rank": row["IVR"], "nifty_trend": nifty_payload_string,
        "oi_change_pct": row["OI_Chg"], "price_change_pct": row["Price_Chg"],
        "day_move": row["DayMove"], "atr": row["ATR"]
    }
    
    analysis = engine.route_asset(row["Symbol"], row["ID"], row["FnO"], metrics_payload)
    
    score_color = "green" if analysis["score"] >= 6 else ("orange" if 4 <= analysis["score"] <= 5 else "red")
    st.markdown(f"### Strategy Evaluation Score: :{score_color}[{analysis['score']} / 8]")
    st.info(f"**Automated Recommended Execution Route:** {analysis['route']}")
    
    st.subheader("Evaluation Metric Checklist Breakdown")
    for key, value in analysis["breakdown"].items():
        st.text(f"• {key}: {value}")

st.markdown("---")
st.header("🎯 Volatility-Based Strike & Premium Target Projections")

if row["FnO"]:
    if st.button(f"Execute Options Matrix Calculation For: {selected_symbol}"):
               with st.spinner("Parsing active option chains and processing volatility bands..."):
            
            # Fetch live structural projections using calculated metrics
            strike_details = engine.optimize_strike_with_targets(
                underlying_symbol=selected_symbol,
                current_price=float(row["Price"]),
                atr=float(row["ATR"]),
                target_delta=0.50
            )
            
            if strike_details.get("status") == "Success":
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Optimal Locked Contract", f"{strike_details['strike']} {strike_details['type']}")
                    st.metric("Current Entry Premium", f"₹ {strike_details['current_premium']}")
                with c2:
                    st.metric("Underlying Spot Stop-Loss", f"₹ {strike_details['spot_sl']}")
                    st.metric("Target Option Premium SL", f"₹ {strike_details['premium_sl']}")
                with c3:
                    st.metric("Underlying Spot Take-Profit", f"₹ {strike_details['spot_tp']}")
                    st.metric("Target Option Premium TP", f"₹ {strike_details['premium_tp']}")
                    
                st.success(f"Execution Target Confirmed: Buy {selected_symbol} {strike_details['expiry']} Strike {strike_details['strike']} CE")
            else:
                st.error(f"Strategy Compilation Failed: {strike_details.get('message')}")
else:
    st.warning("Selected asset is not configured for F&O contracts. Option strike projections deactivated.")

