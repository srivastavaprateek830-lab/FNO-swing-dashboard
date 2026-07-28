import streamlit as st
import pandas as pd
from datetime import datetime
from signal_engine import TradingEngine

# Configure high-end widescreen view
st.set_page_config(page_title="Live Market Sync", layout="wide")

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

# --- TOP LIVE HEADER BAR ---
hdr_col1, hdr_col2 = st.columns([3, 1])
with hdr_col1:
    st.markdown(f"### 📋 LIVE MARKET SYNC: DASHBOARD OVERVIEW")
with hdr_col2:
    if st.button("🔄 Refresh Data Feed", use_container_width=True):
        st.cache_resource.clear()

st.markdown("---")

# --- MASTER DATABASE FEEDS ---
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

# --- HIDDEN PARAMETER STRIP FOR PROCESSING ---
nifty_payload_string = "BULLISH"

# --- SIDE-BY-SIDE CORE WORKSPACE ---
col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        st.markdown("#### 📋 Watchlist Core Feed")
        
        # Format a beautifully styled display dataframe table with visual up/down arrows
        styled_table = master_database[["Symbol", "Price", "RSI", "FnO", "OI_Chg"]].copy()
        styled_table["Price"] = styled_table.apply(lambda r: f"₹ {r['Price']} ↑" if r["RSI"] > 50 else f"₹ {r['Price']} ↓", axis=1)
        styled_table["FnO"] = styled_table["FnO"].apply(lambda x: "🔵 Enabled" if x else "⚪ Cash")
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        selected_symbol = st.selectbox("Select Target Tracker for Asset Diagnostics:", master_database["Symbol"])

with col2:
    with st.container(border=True):
        st.markdown("#### 📊 8-Point Scoring & Routing Engine")
        
        row = master_database[master_database["Symbol"] == selected_symbol].iloc
        metrics_payload = {
            "close": row["Price"], "ema_20": row["EMA20"], "rsi": row["RSI"],
            "volume": row["Vol"], "avg_volume": row["AvgVol"], "prev_high": row["PrevHigh"],
            "iv_rank": row["IVR"], "nifty_trend": nifty_payload_string,
            "oi_change_pct": row["OI_Chg"], "price_change_pct": row["Price_Chg"],
            "day_move": row["DayMove"], "atr": row["ATR"]
        }
        
        analysis = engine.route_asset(row["Symbol"], row["ID"], row["FnO"], metrics_payload)
        
        # Replicating the Gauge Score Section
        score_col1, score_col2 = st.columns([2, 1])
        with score_col1:
            score_color = "green" if analysis["score"] >= 6 else ("orange" if 4 <= analysis["score"] <= 5 else "red")
            st.markdown(f"### Strategy Evaluation Score: :{score_color}[{analysis['score']} / 8]")
            st.markdown(f"**Recommended Route:** `{analysis['route']}`")
        with score_col2:
            # Modern high-contrast numerical dashboard indicator
            st.markdown(f"<div style='text-align:center; padding:10px; background-color:#1E2638; border-radius:10px;'><span style='color:#888; font-size:12px;'>SCORE MATRIX</span><br><b style='font-size:36px; color:#00FF00;'>{analysis['score']}</b><span style='color:#888;'>/8</span></div>", unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("**Evaluation Metric Checklist Breakdown:**")
        
        # Display list with color indicators directly matching the target layout image
        for key, val in analysis["breakdown"].items():
            if "PASS" in str(val) or "BULLISH" in str(val) or "SAFE" in str(val) or "%" in str(val) or "LONG" in str(val):
                st.markdown(f"✅ {key} : <span style='color:#00FF00; font-weight:bold;'>{val}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"❌ {key} : <span style='color:#FF3333; font-weight:bold;'>{val}</span>", unsafe_allow_html=True)

st.markdown("---")

# --- VOLATILITY STRIKE SELECTION LOWER HALF COMPONENT ---
with st.container(border=True):
    st.markdown("#### 🎯 Volatility-Based Strike & Premium Target Projections")
    
    if row["FnO"]:
        # Generating multi-tab navigation to match your reference layout design exactly
        tab1, tab2, tab3 = st.tabs(["🎯 Strike Targets", "💰 Premium Target Projections", "📊 Option Greeks Feed"])
        
        strike_details = engine.optimize_strike_with_targets(
            underlying_symbol=selected_symbol,
            current_price=float(row["Price"]),
            atr=float(row["ATR"]),
            target_delta=0.50
        )
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("OPTIMAL STRIKE LOCK", f"{strike_details['strike']} {strike_details['type']}", "At-The-Money")
            c2.metric("UNDERLYING SPOT PRICE", f"₹ {row['Price']}")
            c3.metric("CONTRACT EXPIRY TARGET", strike_details["expiry"])
            
        with tab2:
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("CURRENT ENTRY PREMIUM", f"₹ {strike_details['current_premium']}")
            cc2.metric("OPTION PREMIUM STOP-LOSS", f"₹ {strike_details['premium_sl']}", f"Spot SL: ₹{strike_details['spot_sl']}", delta_color="inverse")
            cc3.metric("OPTION PREMIUM TAKE-PROFIT", f"₹ {strike_details['premium_tp']}", f"Spot TP: ₹{strike_details['spot_tp']}")
            
        with tab3:
            ccc1, ccc2, ccc3 = st.columns(3)
            ccc1.metric("TARGET DELTA ACCELERATION", f"{strike_details['delta']:.2f}")
            ccc2.metric("DAILY THETA DECAY DRAG", f"{strike_details['theta']:.4f}")
            ccc3.metric("IMPLIED VOLATILITY RANK (IVR)", f"{row['IVR']}%")
            
        st.success(f"✓ Target Lock Armed: Ready to fire automated route allocation for {selected_symbol}.")
    else:
        st.warning("⚠️ SELECTED ASSET IS NOT CONFIGURED FOR F&O CONTRACTS. OPTION STRIKE PROJECTIONS DEACTIVATED.")
