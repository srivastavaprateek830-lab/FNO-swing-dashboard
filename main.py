import streamlit as st
import pandas as pd
from signal_engine import TradingEngine

st.set_page_config(page_title="F&O + MTF Thematic Terminal", layout="wide")

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

# --- TOP HEADER BANNER ---
st.title("⚡ F&O and MTF Thematic Swing Terminal")
st.caption("Live Institutional Sector Rotational Matrix & Alpha 8-Point Engine")
st.markdown("---")

# --- DATABASE / MASTER DATA WATCHLIST ---
# Complete list containing underlying F&O and key MTF liquid stocks grouped by sector
master_database = pd.DataFrame([
    # --- BANKING & FINANCIAL SERVICES ---
    {"Symbol": "HDFC BANK", "ID": "1333", "Sector": "Banking & Financials", "FnO": True, "Price": 1650.0, "EMA20": 1620.0, "RSI": 58, "Vol": 8200000, "AvgVol": 5000000, "PrevHigh": 1640.0, "IVR": 22, "OI_Chg": 4.1, "Price_Chg": 1.2, "DayMove": 18.0, "ATR": 22.0},
    {"Symbol": "ICICI BANK", "ID": "11483", "Sector": "Banking & Financials", "FnO": True, "Price": 1120.0, "EMA20": 1100.0, "RSI": 62, "Vol": 6500000, "AvgVol": 4000000, "PrevHigh": 1115.0, "IVR": 18, "OI_Chg": 3.8, "Price_Chg": 0.9, "DayMove": 12.0, "ATR": 15.0},
    {"Symbol": "SBIN", "ID": "3045", "Sector": "Banking & Financials", "FnO": True, "Price": 780.0, "EMA20": 795.0, "RSI": 45, "Vol": 3100000, "AvgVol": 5000000, "PrevHigh": 790.0, "IVR": 35, "OI_Chg": -1.5, "Price_Chg": -0.8, "DayMove": 8.0, "ATR": 12.0},
    
    # --- INFORMATION TECHNOLOGY (IT) ---
    {"Symbol": "TCS", "ID": "11536", "Sector": "Information Technology", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0},
    {"Symbol": "INFY", "ID": "1594", "Sector": "Information Technology", "FnO": True, "Price": 1520.0, "EMA20": 1500.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3000000, "PrevHigh": 1510.0, "IVR": 28, "OI_Chg": 2.5, "Price_Chg": 1.1, "DayMove": 22.0, "ATR": 28.0},
    {"Symbol": "WIPRO", "ID": "3787", "Sector": "Information Technology", "FnO": True, "Price": 480.0, "EMA20": 472.0, "RSI": 54, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 478.0, "IVR": 14, "OI_Chg": 1.1, "Price_Chg": 0.6, "DayMove": 5.0, "ATR": 8.0},
    
    # --- AUTOMOBILES ---
    {"Symbol": "TATAMOTORS", "ID": "3456", "Sector": "Automobiles", "FnO": True, "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0},
    {"Symbol": "MARUTI", "ID": "10999", "Sector": "Automobiles", "FnO": True, "Price": 12200.0, "EMA20": 12100.0, "RSI": 51, "Vol": 400000, "AvgVol": 350000, "PrevHigh": 12180.0, "IVR": 19, "OI_Chg": 0.5, "Price_Chg": 0.3, "DayMove": 90.0, "ATR": 180.0},
    
    # --- CONSUMER INTERNET & GROWTH (MTF Focus) ---
    {"Symbol": "ZOMATO", "ID": "5097", "Sector": "Consumer Internet", "FnO": False, "Price": 160.0, "EMA20": 145.0, "RSI": 65, "Vol": 15000000, "AvgVol": 8000000, "PrevHigh": 155.0, "IVR": 0, "OI_Chg": 0.0, "Price_Chg": 3.4, "DayMove": 4.0, "ATR": 5.0},
    {"Symbol": "JIOFIN", "ID": "14354", "Sector": "Consumer Internet", "FnO": False, "Price": 355.0, "EMA20": 340.0, "RSI": 59, "Vol": 8000000, "AvgVol": 6000000, "PrevHigh": 352.0, "IVR": 0, "OI_Chg": 0.0, "Price_Chg": 1.5, "DayMove": 6.0, "ATR": 9.0}
])

# --- DYNAMIC SECTOR MOMENTUM ENGINE ---
# Calculates which sector is driving the market based on internal stock metrics
sector_stats = []
for sector, group in master_database.groupby("Sector"):
    # Percentage of stocks in sector with positive momentum filters
    bullish_stocks = group[(group["RSI"] > 50) & (group["Price"] > group["EMA20"])]
    bullish_score = len(bullish_stocks) / len(group) * 100
    avg_price_gain = group["Price_Chg"].mean()
    sector_stats.append({"Sector": sector, "Bullish Strength": f"{bullish_score:.0f}%", "Avg Change": f"{avg_price_gain:+.2f}%", "_score": bullish_score})

sector_df = pd.DataFrame(sector_stats).sort_values(by="_score", ascending=False)

# --- WORKSPACE GRID LAYOUT ---
top_col1, top_col2 = st.columns([1, 2])

with top_col1:
    with st.container(border=True):
        st.subheader("🔥 Sector Momentum Heatmap")
        st.caption("Sorted by Bullish Momentum Concentration")
        st.dataframe(sector_df[["Sector", "Bullish Strength", "Avg Change"]], use_container_width=True, hide_index=True)

with top_col2:
    with st.container(border=True):
        st.subheader("⚙️ Active Filter Filters")
        st.sidebar.header("🌍 Market Environment Sentinel")
        nifty_state = st.sidebar.radio("Nifty 50 Trend Regime Filter:", ("BULLISH (Above 20EMA)", "BEARISH (Below 20EMA)"))
        nifty_payload_string = "BULLISH" if "BULLISH" in nifty_state else "BEARISH"
        
        # Sector Filter selection drop box dropdown
        selected_sector = st.selectbox("🎯 Step 1: Choose Target Industry Sector:", sector_df["Sector"].unique())
        
        # Filters our complete table list instantly to reflect only chosen sector stocks
        filtered_watchlist = master_database[master_database["Sector"] == selected_sector]
        
        selected_symbol = st.selectbox("🔍 Step 2: Choose Stock for Deep Diagnostics Run:", filtered_watchlist["Symbol"])

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("📋 Segmented Watchlist Feed")
        st.caption(f"Currently Showing Active Tickers in: {selected_sector}")
        st.dataframe(filtered_watchlist[["Symbol", "Price", "RSI", "FnO", "OI_Chg"]], use_container_width=True, hide_index=True)

with col2:
    with st.container(border=True):
        st.subheader("📊 8-Point Scoring & Routing Engine")
        row = master_database[master_database["Symbol"] == selected_symbol].iloc[0]
        
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
with st.container(border=True):
    st.subheader("🎯 Volatility-Based Strike & Premium Target Projections")

    if row["FnO"]:
        if st.button(f"Execute Options Matrix Calculation For: {selected_symbol}"):
            with st.spinner("Parsing active option chains and processing volatility bands..."):
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
