import streamlit as st
import pandas as pd
from signal_engine import TradingEngine

st.set_page_config(page_title="Institutional Swing Terminal", layout="wide")

# Institutional Theme Styling Layer: Restricts row inflation and enforces compact typography
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 0rem !important; margin-bottom: -0.2rem !important; }
    .stDataFrame div { font-size: 12px !important; }
    .compact-text { font-family: monospace; font-size: 11px; margin-bottom: 2px; line-height: 1.3; }
    h3, h4 { margin-top: 0rem !important; margin-bottom: 0.2rem !important; padding: 0rem !important; font-size: 14px !important; font-weight: bold !important; color: #E2E8F0 !important; }
    .stAlert { padding: 5px !important; margin-top: 5px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

# --- INSTALMENT TRACKING DATABASE ---
master_database = pd.DataFrame([
    {"Symbol": "HDFC BANK", "ID": "1333", "Sector": "Banking & Financials", "FnO": True, "Price": 1650.0, "EMA20": 1620.0, "RSI": 58, "Vol": 8200000, "AvgVol": 5000000, "PrevHigh": 1640.0, "IVR": 22, "OI_Chg": 4.1, "Price_Chg": 1.2, "DayMove": 18.0, "ATR": 22.0},
    {"Symbol": "ICICI BANK", "ID": "11483", "Sector": "Banking & Financials", "FnO": True, "Price": 1120.0, "EMA20": 1100.0, "RSI": 62, "Vol": 6500000, "AvgVol": 4000000, "PrevHigh": 1115.0, "IVR": 18, "OI_Chg": 3.8, "Price_Chg": 0.9, "DayMove": 12.0, "ATR": 15.0},
    {"Symbol": "SBIN", "ID": "3045", "Sector": "Banking & Financials", "FnO": True, "Price": 780.0, "EMA20": 795.0, "RSI": 45, "Vol": 3100000, "AvgVol": 5000000, "PrevHigh": 790.0, "IVR": 35, "OI_Chg": -1.5, "Price_Chg": -0.8, "DayMove": 8.0, "ATR": 12.0},
    {"Symbol": "TCS", "ID": "11536", "Sector": "Information Technology", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0},
    {"Symbol": "INFY", "ID": "1594", "Sector": "Information Technology", "FnO": True, "Price": 1520.0, "EMA20": 1500.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3000000, "PrevHigh": 1510.0, "IVR": 28, "OI_Chg": 2.5, "Price_Chg": 1.1, "DayMove": 22.0, "ATR": 28.0},
    {"Symbol": "TATAMOTORS", "ID": "3456", "Sector": "Automobiles", "FnO": True, "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0},
    {"Symbol": "MARUTI", "ID": "10999", "Sector": "Automobiles", "FnO": True, "Price": 12200.0, "EMA20": 12100.0, "RSI": 51, "Vol": 400000, "AvgVol": 350000, "PrevHigh": 12180.0, "IVR": 19, "OI_Chg": 0.5, "Price_Chg": 0.3, "DayMove": 90.0, "ATR": 180.0},
    {"Symbol": "ZOMATO", "ID": "5097", "Sector": "Consumer Internet", "FnO": False, "Price": 160.0, "EMA20": 145.0, "RSI": 65, "Vol": 15000000, "AvgVol": 8000000, "PrevHigh": 155.0, "IVR": 0, "OI_Chg": 0.0, "Price_Chg": 3.4, "DayMove": 4.0, "ATR": 5.0}
])

# --- DYNAMIC SECTOR MOMENTUM ENGINE ---
sector_stats = []
for sector, group in master_database.groupby("Sector"):
    bullish_stocks = group[(group["RSI"] > 50) & (group["Price"] > group["EMA20"])]
    bullish_score = len(bullish_stocks) / len(group) * 100
    avg_price_gain = group["Price_Chg"].mean()
    sector_stats.append({"Sector": sector, "Strength": f"🔥 {bullish_score:.0f}% BULLISH", "Avg Gain": f"{avg_price_gain:+.2f}%", "_score": bullish_score})

sector_df = pd.DataFrame(sector_stats).sort_values(by="_score", ascending=False)

# --- GLOBAL BRANDING HEADER STRIP ---
hc1, hc2, hc3 = st.columns([2, 1, 1])
with hc1:
    st.markdown("### ⚡ LIVE THEMATIC TRADING TERMINAL")
with hc2:
    st.markdown("<div style='text-align:right;font-size:12px;color:#888;'>Index: <b style='color:#00FF00;'>NIFTY 50 BULLISH</b></div>", unsafe_allow_html=True)
with hc3:
    st.markdown("<div style='text-align:right;font-size:12px;color:#888;'>Volatility: <b style='color:#FF9900;'>ATR NORMAL</b></div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0.1rem;margin-bottom:0.4rem;'>", unsafe_allow_html=True)

# ==============================================================================
# ROW 1: SECTOR HEATMAP & RADAR CONTROLS (BALANCED HORIZONTAL SPREAD)
# ==============================================================================
r1_col1, r1_col2 = st.columns([1.2, 1])

with r1_col1:
    with st.container(border=True):
        st.markdown("#### 🔥 Industry Sector Rotation Matrix")
        st.dataframe(sector_df[["Sector", "Strength", "Avg Gain"]], use_container_width=True, hide_index=True, height=120)

with r1_col2:
    with st.container(border=True):
        st.markdown("#### 🎛️ Terminal Interactive Radar")
        # Sector drop box filters data
        selected_sector = st.selectbox("1. Filter Watchlist by Sector Theme:", sector_df["Sector"].unique())
        filtered_watchlist = master_database[master_database["Sector"] == selected_sector]
        
        # Stock dropdown updates based on the selected sector
        selected_symbol = st.selectbox("2. Select Active Target Asset:", filtered_watchlist["Symbol"])

st.markdown("<hr style='margin-top:0.2rem;margin-bottom:0.4rem;'>", unsafe_allow_html=True)

# Lock target data row instantly
row = master_database[master_database["Symbol"] == selected_symbol].iloc[0]

# ==============================================================================
# ROW 2: DETAILED ANALYSIS DESK (THE 3-COLUMN INTUITIVE MATRIX)
# ==============================================================================
col1, col2, col3 = st.columns([1, 1.1, 1.2])

with col1:
    with st.container(border=True):
        st.markdown(f"#### 📋 Feed: {selected_sector}")
        # Displays the stock list filtered by your selected sector
        st.dataframe(filtered_watchlist[["Symbol", "Price", "RSI", "OI_Chg"]], use_container_width=True, hide_index=True, height=220)

with col2:
    with st.container(border=True):
        st.markdown("#### 📊 8-Point Compliance Matrix")
        
        metrics_payload = {
            "close": row["Price"], "ema_20": row["EMA20"], "rsi": row["RSI"],
            "volume": row["Vol"], "avg_volume": row["AvgVol"], "prev_high": row["PrevHigh"],
            "iv_rank": row["IVR"], "nifty_trend": "BULLISH", "oi_change_pct": row["OI_Chg"],
            "price_change_pct": row["Price_Chg"], "day_move": row["DayMove"], "atr": row["ATR"]
        }
        
        analysis = engine.route_asset(row["Symbol"], row["ID"], row["FnO"], metrics_payload)
        
        score_color = "green" if analysis["score"] >= 6 else ("orange" if 4 <= analysis["score"] <= 5 else "red")
        st.markdown(f"**Score:** :{score_color}[**{analysis['score']}/8**] | **Route:** `{analysis['route'][:20]}...`")
        st.markdown("<hr style='margin:0.15rem;'>", unsafe_allow_html=True)
        
        # Highly optimized checklist layout with zero vertical bloating
        for key, val in analysis["breakdown"].items():
            color = "🟢" if "PASS" in str(val) or "BULLISH" in str(val) or "SAFE" in str(val) or "%" in str(val) or "LONG" in str(val) else "🔴"
            st.markdown(f"<div class='compact-text'>{color} {key[3:]}: <b>{val}</b></div>", unsafe_allow_html=True)

with col3:
    with st.container(border=True):
        st.markdown("#### 🎯 Option Greek Target Matrix")
        
        if row["FnO"]:
            strike_details = engine.optimize_strike_with_targets(
                underlying_symbol=selected_symbol, current_price=float(row["Price"]), atr=float(row["ATR"]), target_delta=0.50
            )
            
            st.markdown(f"**Target Lock:** <span style='color:#00FF00;font-weight:bold;'>{strike_details['strike']} {strike_details['type']} ({strike_details['expiry']})</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.15rem;'>", unsafe_allow_html=True)
            
            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown(f"<div class='compact-text'>▶ Entry Prem: <b>₹{strike_details['current_premium']}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='compact-text'>▶ Spot SL: <b>₹{strike_details['spot_sl']}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='compact-text'>▶ Premium SL: <span style='color:#FF3333;'><b>₹{strike_details['premium_sl']}</b></span></div>", unsafe_allow_html=True)
            with rc2:
                st.markdown(f"<div class='compact-text'>▶ Target Delta: <b>{strike_details['delta']:.2f}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='compact-text'>▶ Spot TP: <b>₹{strike_details['spot_tp']}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='compact-text'>▶ Premium TP: <span style='color:#00FF00;'><b>₹{strike_details['premium_tp']}</b></span></div>", unsafe_allow_html=True)
                
            st.markdown("<hr style='margin:0.15rem;'>", unsafe_allow_html=True)
            st.success("🎯 Order Router Armed.")
        else:
            st.warning("⚠️ CASH SEGMENT ONLY: Derivative targeting modules locked for this asset.")
