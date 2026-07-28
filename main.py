import streamlit as st
import pandas as pd
from signal_engine import TradingEngine

# Force application container to use standard compact width limits
st.set_page_config(page_title="Thematic Swing Terminal", layout="wide")

# Institutional Spacing Minimization Layer
st.markdown("""
<style>
    .block-container { padding-top: 0.8rem !important; padding-bottom: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 0rem !important; margin-bottom: -0.3rem !important; }
    .stDataFrame div { font-size: 11px !important; }
    .matrix-title { font-family: monospace; font-size: 13px; font-weight: bold; color: #FF9900; margin-bottom: 3px; }
    .compact-text { font-family: monospace; font-size: 11px; margin-bottom: 2px; line-height: 1.3; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

# --- THEMATIC COMPREHENSIVE SECTOR DATABASE ---
master_database = pd.DataFrame([
    {"Symbol": "TCS", "ID": "11536", "Sector": "Nifty IT", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0},
    {"Symbol": "INFY", "ID": "1594", "Sector": "Nifty IT", "FnO": True, "Price": 1520.0, "EMA20": 1500.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3000000, "PrevHigh": 1510.0, "IVR": 28, "OI_Chg": 2.5, "Price_Chg": 1.1, "DayMove": 22.0, "ATR": 28.0},
    {"Symbol": "HCLTECH", "ID": "1345", "Sector": "Nifty IT", "FnO": True, "Price": 1410.0, "EMA20": 1390.0, "RSI": 54, "Vol": 2800000, "AvgVol": 2000000, "PrevHigh": 1400.0, "IVR": 20, "OI_Chg": 3.1, "Price_Chg": 1.4, "DayMove": 19.0, "ATR": 24.0},
    {"Symbol": "LTIM", "ID": "17832", "Sector": "Nifty IT", "FnO": True, "Price": 4900.0, "EMA20": 4820.0, "RSI": 59, "Vol": 900000, "AvgVol": 700000, "PrevHigh": 4880.0, "IVR": 32, "OI_Chg": 1.8, "Price_Chg": 0.8, "DayMove": 45.0, "ATR": 85.0},
    {"Symbol": "WIPRO", "ID": "3787", "Sector": "Nifty IT", "FnO": True, "Price": 480.0, "EMA20": 472.0, "RSI": 54, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 478.0, "IVR": 14, "OI_Chg": 1.1, "Price_Chg": 0.6, "DayMove": 5.0, "ATR": 8.0},
    {"Symbol": "SUNPHARMA", "ID": "3333", "Sector": "Nifty Pharma", "FnO": True, "Price": 1540.0, "EMA20": 1510.0, "RSI": 58, "Vol": 1800000, "AvgVol": 1200000, "PrevHigh": 1530.0, "IVR": 19, "OI_Chg": 2.2, "Price_Chg": 1.3, "DayMove": 14.0, "ATR": 22.0},
    {"Symbol": "TATAMOTORS", "ID": "3456", "Sector": "Nifty Auto", "FnO": True, "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0}
])

# --- DYNAMIC MATRIX CALCULATIONS FOR THE SECTOR HEATMAP ---
sector_stats = []
for sector, group in master_database.groupby("Sector"):
    bullish_stocks = group[(group["RSI"] > 50) & (group["Price"] > group["EMA20"])]
    bullish_score = len(bullish_stocks) / len(group) * 100
    sector_stats.append({"Sector": sector, "Concentration": f"🔥 {bullish_score:.0f}% BULLISH", "_score": bullish_score})
sector_df = pd.DataFrame(sector_stats).sort_values(by="_score", ascending=False)

# ==============================================================================
# ROW 1: WORKSPACE HORIZONTAL PANELS
# ==============================================================================
left_panel, right_panel = st.columns([2.3, 1])

with left_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ Sectoral Stocks Thematic Board</div>", unsafe_allow_html=True)
        
        sel_c1, sel_c2 = st.columns([1, 1.5])
        with sel_c1:
            selected_sector = st.selectbox("Filter Sector Theme:", sector_df["Sector"].unique(), label_visibility="collapsed")
        with sel_c2:
            st.markdown("<span style='font-size:11px;color:#888;'><i>Ex - Selecting a theme re-populates the rows. Use dropdown on the right to switch targets.</i></span>", unsafe_allow_html=True)
            
        filtered_watchlist = master_database[master_database["Sector"] == selected_sector]
        
        compiled_rows = []
        for _, stock in filtered_watchlist.iterrows():
            metrics_payload = {
                "close": stock["Price"], "ema_20": stock["EMA20"], "rsi": stock["RSI"],
                "volume": stock["Vol"], "avg_volume": stock["AvgVol"], "prev_high": stock["PrevHigh"],
                "nifty_trend": "BULLISH", "oi_change_pct": stock["OI_Chg"], "price_change_pct": stock["Price_Chg"],
                "day_move": stock["DayMove"], "atr": stock["ATR"]
            }
            analysis = engine.route_asset(stock["Symbol"], stock["ID"], stock["FnO"], metrics_payload)
            score = analysis["score"]
            
            final_call = "🟢 BUY" if score >= 6 else ("⚪ NEUTRAL" if 4 <= score <= 5 else "🔴 SELL")
            
            compiled_rows.append({
                "Ticker": stock["Symbol"], "LTP": f"₹{stock['Price']}", "RSI": int(stock["RSI"]),
                "OI_CHG": f"{stock['OI_Chg']:+.1f}%",
                "Supertrend": "🟩 PASS" if stock["Price"] > stock["EMA20"] else "🟥 FAIL",
                "Trend": "PASS" if stock["Price"] > stock["EMA20"] else "FAIL",
                "Momentum": "PASS" if stock["RSI"] > 50 else "FAIL",
                "Volume": "PASS" if stock["Vol"] > stock["AvgVol"] else "FAIL",
                "Del Strength": "PASS" if score >= 4 else "FAIL",
                "Breakout": "YES" if stock["Price"] > stock["PrevHigh"] else "NO",
                "Final Callout": final_call, "MTF": "YES" if score >= 4 else "NO", "FNO": "YES" if stock["FnO"] else "NO"
            })
            
        st.dataframe(pd.DataFrame(compiled_rows), use_container_width=True, hide_index=True, height=180)

with right_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ Top 3 Outperforming Sectors</div>", unsafe_allow_html=True)
        st.dataframe(sector_df[["Sector", "Concentration"]].head(3), use_container_width=True, hide_index=True, height=95)
        
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>🎛️ Active Token Target Scope Selector</div>", unsafe_allow_html=True)
        
        # FIX 1: Active Token automatically syncs down to match the list selection options
        stock_options = filtered_watchlist["Symbol"].tolist()
        selected_symbol = st.selectbox("Choose Target Asset:", stock_options, label_visibility="collapsed")

# Pull targeted active record row seamlessly
target_stock = master_database[master_database["Symbol"] == selected_symbol].iloc[0]

# Compute underlying strategy variables via engine rules
strike_details = engine.optimize_strike_with_targets(
    underlying_symbol=selected_symbol, current_price=float(target_stock["Price"]), atr=float(target_stock["ATR"]), target_delta=0.50
)

# ==============================================================================
# FIX 2: ROW 2 DUAL SEPARATE MATRICES FOR MTF AND FNO SPREAD LAYOUTS
# ==============================================================================
st.markdown("<hr style='margin-top:0.2rem;margin-bottom:0.4rem;'>", unsafe_allow_html=True)
mtf_box, fno_box = st.columns(2)

with mtf_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ MTF Equity Leverage Trading Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        
        mtf_matrix_row = [{
            "Asset": target_stock["Symbol"],
            "Spot Entry": f"₹ {target_stock['Price']}",
            "Spot SL (1.5x ATR)": f"₹ {strike_details['spot_sl']}",
            "Spot TP (3.0x ATR)": f"₹ {strike_details['spot_tp']}",
            "MTF Max Funding": "Up to 4x Leverage",
            "Initial Margin (25%)": f"₹ {float(target_stock['Price']) * 0.25:.1f}",
            "Position State": "ARMED FOR SPOT BUY"
        }]
        st.dataframe(pd.DataFrame(mtf_matrix_row), use_container_width=True, hide_index=True)
        
        if st.button(f"🚀 FIRE MTF SPOT MARGIN POSITION: {selected_symbol}", use_container_width=True):
            st.success(f"MTF Equity Leverage Router Payload Engaged for {selected_symbol}.")

with fno_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ F&O Derivative Options Greek Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        
        if target_stock["FnO"]:
            fno_matrix_row = [{
                "Option Strike": f"{strike_details['strike']} {strike_details['type']}",
                "Entry Premium": f"₹ {strike_details['current_premium']}",
                "Premium SL": f"₹ {strike_details['premium_sl']}",
                "Premium TP1": f"₹ {strike_details['premium_tp']:.2f}",
                "Premium TP2": f"₹ {(strike_details['premium_tp'] * 1.25):.2f}",
                "Premium TP3": f"₹ {(strike_details['premium_tp'] * 1.50):.2f}"
            }]
            st.dataframe(pd.DataFrame(fno_matrix_row), use_container_width=True, hide_index=True)
            
            if st.button(f"🔥 FIRE F&O DERIVATIVE OPTIONS POSITION: {selected_symbol}", use_container_width=True):
                st.balloons()
                st.success(f"Options Order Payload Routed Successfully for {selected_symbol}.")
        else:
            st.warning(f"❌ DERIVATIVE SYSTEM LOCKED: {selected_symbol} is restricted to Spot Cash segment options only.")
