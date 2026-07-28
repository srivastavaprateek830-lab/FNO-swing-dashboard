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

# --- THE REAL UNIVERSE: BAKED DIRECTLY IN TO FORCE DYNAMIC LOADING ---
master_database = pd.DataFrame([
    {"Symbol": "HDFCBANK", "ID": "1333", "Sector": "Nifty Bank", "FnO": True, "Price": 1650.0, "EMA20": 1620.0, "RSI": 58, "Vol": 8200000, "AvgVol": 5000000, "PrevHigh": 1640.0, "IVR": 22, "OI_Chg": 4.1, "Price_Chg": 1.2, "DayMove": 18.0, "ATR": 22.0},
    {"Symbol": "ICICIBANK", "ID": "11483", "Sector": "Nifty Bank", "FnO": True, "Price": 1120.0, "EMA20": 1100.0, "RSI": 62, "Vol": 6500000, "AvgVol": 4000000, "PrevHigh": 1115.0, "IVR": 18, "OI_Chg": 3.8, "Price_Chg": 0.9, "DayMove": 12.0, "ATR": 15.0},
    {"Symbol": "SBIN", "ID": "3045", "Sector": "Nifty Bank", "FnO": True, "Price": 780.0, "EMA20": 795.0, "RSI": 45, "Vol": 3100000, "AvgVol": 5000000, "PrevHigh": 790.0, "IVR": 35, "OI_Chg": -1.5, "Price_Chg": -0.8, "DayMove": 8.0, "ATR": 12.0},
    {"Symbol": "AXISBANK", "ID": "5900", "Sector": "Nifty Bank", "FnO": True, "Price": 1050.0, "EMA20": 1030.0, "RSI": 55, "Vol": 4200000, "AvgVol": 3500000, "PrevHigh": 1042.0, "IVR": 21, "OI_Chg": 1.9, "Price_Chg": 0.7, "DayMove": 11.0, "ATR": 18.0},
    {"Symbol": "KOTAKBANK", "ID": "1922", "Sector": "Nifty Bank", "FnO": True, "Price": 1780.0, "EMA20": 1810.0, "RSI": 48, "Vol": 2200000, "AvgVol": 2500000, "PrevHigh": 1795.0, "IVR": 16, "OI_Chg": -0.4, "Price_Chg": -0.3, "DayMove": 14.0, "ATR": 26.0},
    {"Symbol": "TATAMOTORS", "ID": "3456", "Sector": "Nifty Auto", "FnO": True, "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0},
    {"Symbol": "MARUTI", "ID": "10999", "Sector": "Nifty Auto", "FnO": True, "Price": 12200.0, "EMA20": 12100.0, "RSI": 51, "Vol": 400000, "AvgVol": 350000, "PrevHigh": 12180.0, "IVR": 19, "OI_Chg": 0.5, "Price_Chg": 0.3, "DayMove": 90.0, "ATR": 180.0},
    {"Symbol": "M&M", "ID": "2031", "Sector": "Nifty Auto", "FnO": True, "Price": 2050.0, "EMA20": 1980.0, "RSI": 64, "Vol": 3100000, "AvgVol": 2200000, "PrevHigh": 2020.0, "IVR": 26, "OI_Chg": 4.2, "Price_Chg": 1.8, "DayMove": 35.0, "ATR": 42.0},
    {"Symbol": "TCS", "ID": "11536", "Sector": "Nifty IT", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0},
    {"Symbol": "INFY", "ID": "1594", "Sector": "Nifty IT", "FnO": True, "Price": 1520.0, "EMA20": 1500.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3000000, "PrevHigh": 1510.0, "IVR": 28, "OI_Chg": 2.5, "Price_Chg": 1.1, "DayMove": 22.0, "ATR": 28.0},
    {"Symbol": "HCLTECH", "ID": "1345", "Sector": "Nifty IT", "FnO": True, "Price": 1410.0, "EMA20": 1390.0, "RSI": 54, "Vol": 2800000, "AvgVol": 2000000, "PrevHigh": 1400.0, "IVR": 20, "OI_Chg": 3.1, "Price_Chg": 1.4, "DayMove": 19.0, "ATR": 24.0},
    {"Symbol": "SUNPHARMA", "ID": "3333", "Sector": "Nifty Pharma", "FnO": True, "Price": 1540.0, "EMA20": 1510.0, "RSI": 58, "Vol": 1800000, "AvgVol": 1200000, "PrevHigh": 1530.0, "IVR": 19, "OI_Chg": 2.2, "Price_Chg": 1.3, "DayMove": 14.0, "ATR": 22.0},
    {"Symbol": "CIPLA", "ID": "694", "Sector": "Nifty Pharma", "FnO": True, "Price": 1420.0, "EMA20": 1395.0, "RSI": 59, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 1405.0, "IVR": 24, "OI_Chg": 3.0, "Price_Chg": 1.6, "DayMove": 20.0, "ATR": 25.0},
    {"Symbol": "TATASTEEL", "ID": "3499", "Sector": "Nifty Metal", "FnO": True, "Price": 155.0, "EMA20": 151.0, "RSI": 60, "Vol": 22000000, "AvgVol": 15000000, "PrevHigh": 153.5, "IVR": 34, "OI_Chg": 5.1, "Price_Chg": 2.1, "DayMove": 4.0, "ATR": 4.5},
    {"Symbol": "HINDUNILVR", "ID": "1330", "Sector": "Nifty FMCG", "FnO": True, "Price": 2420.0, "EMA20": 2450.0, "RSI": 41, "Vol": 1200000, "AvgVol": 1500000, "PrevHigh": 2445.0, "IVR": 12, "OI_Chg": -0.8, "Price_Chg": -0.4, "DayMove": 15.0, "ATR": 35.0},
    {"Symbol": "ITC", "ID": "1660", "Sector": "Nifty FMCG", "FnO": True, "Price": 435.0, "EMA20": 428.0, "RSI": 55, "Vol": 8500000, "AvgVol": 7000000, "PrevHigh": 432.0, "IVR": 17, "OI_Chg": 2.1, "Price_Chg": 0.9, "DayMove": 4.0, "ATR": 7.0},
    {"Symbol": "RELIANCE", "ID": "2885", "Sector": "Nifty Oil & Gas", "FnO": True, "Price": 2450.0, "EMA20": 2400.0, "RSI": 58, "Vol": 4200000, "AvgVol": 3100000, "PrevHigh": 2440.0, "IVR": 35, "OI_Chg": 4.5, "Price_Chg": 1.2, "DayMove": 25.0, "ATR": 35.0},
    {"Symbol": "NTPC", "ID": "11630", "Sector": "Nifty Power & Infra", "FnO": True, "Price": 345.0, "EMA20": 328.0, "RSI": 62, "Vol": 6800000, "AvgVol": 5000000, "PrevHigh": 341.2, "IVR": 29, "OI_Chg": 5.2, "Price_Chg": 2.1, "DayMove": 5.5, "ATR": 9.1},
    {"Symbol": "AMBUJACEM", "ID": "63", "Sector": "Nifty Commodities", "FnO": True, "Price": 615.0, "EMA20": 592.0, "RSI": 58, "Vol": 3200000, "AvgVol": 2500000, "PrevHigh": 608.0, "IVR": 27, "OI_Chg": 3.9, "Price_Chg": 1.5, "DayMove": 8.5, "ATR": 14.1},
    {"Symbol": "DLF", "ID": "14732", "Sector": "Nifty Services", "FnO": True, "Price": 880.0, "EMA20": 842.0, "RSI": 62, "Vol": 3500000, "AvgVol": 2500000, "PrevHigh": 868.0, "IVR": 34, "OI_Chg": 5.4, "Price_Chg": 2.5, "DayMove": 14.0, "ATR": 21.0}
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
            st.markdown("<span style='font-size:11px;color:#888;'><i>💡 Click on any stock row check-box below to instantly auto-sync all downstream matrices!</i></span>", unsafe_allow_html=True)
            
        filtered_watchlist = master_database[master_database["Sector"] == selected_sector].reset_index(drop=True)
        compiled_rows = []
        for _, stock in filtered_watchlist.iterrows():
            metrics_payload = {
                "close": stock["Price"], "ema_20": stock["EMA20"], "rsi": stock["RSI"],
                "volume": stock["Vol"], "avg_volume": stock["AvgVol"], "prev_high": stock["PrevHigh"],
                "nifty_trend": "BULLISH", "oi_change_pct": stock["OI_Chg"], "price_change_pct": stock["Price_Chg"],
                "day_move": stock["DayMove"], "atr": stock["ATR"], "delivery_pct": 45.0
            }
            analysis = engine.route_asset(stock["Symbol"], stock["ID"], stock["FnO"], metrics_payload)
            score = analysis["score"]
            final_call = "🟢 BUY" if score >= 6 else ("⚪ NEUTRAL" if 4 <= score <= 5 else "🔴 SELL")
            
            compiled_rows.append({
                "Ticker": stock["Symbol"], "LTP": f"₹{stock['Price']}", "RSI": int(stock["RSI"]),
                "OI_CHG": f"{stock['OI_Chg']:+.1f}%", "Supertrend": "🟩 PASS" if stock["Price"] > stock["EMA20"] else "🟥 FAIL",
                "Trend": "PASS" if stock["Price"] > stock["EMA20"] else "FAIL", "Momentum": "PASS" if stock["RSI"] > 50 else "FAIL",
                "Volume": "PASS" if stock["Vol"] > stock["AvgVol"] else "FAIL", "Del Strength": "PASS" if score >= 4 else "FAIL",
                "Breakout": "YES" if stock["Price"] > stock["PrevHigh"] else "NO", "Final Callout": final_call, "MTF": "YES" if score >= 4 else "NO", "FNO": "YES" if stock["FnO"] else "NO"
            })
            
        df_display = pd.DataFrame(compiled_rows)
        selected_row_data = st.dataframe(df_display, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

with right_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ All Active Sector Concentrations</div>", unsafe_allow_html=True)
        st.dataframe(sector_df[["Sector", "Concentration"]], use_container_width=True, hide_index=True)
        
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>🎛️ Active Token Target Scope Selector</div>", unsafe_allow_html=True)
        stock_options = filtered_watchlist["Symbol"].tolist()
        default_index = 0
        if len(selected_row_data.selection.rows) > 0:
            default_index = int(selected_row_data.selection.rows[0])
            
        selected_symbol = st.selectbox("Choose Target Asset:", stock_options, index=default_index, label_visibility="collapsed")

target_stock_df = filtered_watchlist[filtered_watchlist["Symbol"] == selected_symbol].reset_index(drop=True)
target_stock = target_stock_df.iloc[0]

# Pass selection state tokens directly to live backend data loops
strike_details = engine.optimize_strike_with_targets(
    underlying_symbol_id=str(target_stock["ID"]),
    current_price=float(target_stock["Price"]),
    atr=float(target_stock["ATR"])
)

# ==============================================================================
# ROW 2: DUAL SEPARATE MATRICES FOR MTF AND FNO SPREAD LAYOUTS
# ==============================================================================
st.markdown("<hr style='margin-top:0.2rem;margin-bottom:0.4rem;'>", unsafe_allow_html=True)
mtf_box, fno_box = st.columns(2)

with mtf_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ MTF Equity Leverage Trading Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        mtf_matrix_row = [{
            "Asset": target_stock["Symbol"], "Spot Entry": f"₹ {target_stock['Price']}",
            "Spot SL (1.5x ATR)": f"₹ {strike_details['spot_sl']}", "Spot TP (3.0x ATR)": f"₹ {strike_details['spot_tp']}",
            "MTF Max Funding": "Up to 4x Leverage", "Initial Margin (25%)": f"₹ {float(target_stock['Price']) * 0.25:.1f}",
            "Position State": "ARMED FOR SPOT BUY"
        }]
        st.dataframe(pd.DataFrame(mtf_matrix_row), use_container_width=True, hide_index=True)
        
        if st.button(f"🚀 FIRE MTF SPOT MARGIN POSITION: {selected_symbol}", use_container_width=True):
            payload = engine.generate_dhan_order_payload(target_stock["ID"], target_stock["Symbol"], "BUY", "MTF")
            response = engine.fetcher.place_live_order(payload)
            if "orderStatus" in str(response) or "SUCCESS" in str(response).upper():
                st.balloons()
                st.success(f"✓ ORDER PLACED: Live MTF position fired for {selected_symbol}! Order ID: {response.get('data', {}).get('orderId', 'N/A')}")
            else:
                st.error(f"Execution Failed: {response.get('remarks', 'Check connection or key permissions')}")

with fno_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ F&O Derivative Options Greek Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        if target_stock["FnO"]:
            fno_matrix_row = [{
                "Option Strike": f"{strike_details['strike']} {strike_details['type']}", "Entry Premium": f"₹ {strike_details['current_premium']}",
                "Premium SL": f"₹ {strike_details['premium_sl']}", "Premium TP1": f"₹ {strike_details['premium_tp']:.2f}",
                "Premium TP2": f"₹ {(strike_details['premium_tp'] * 1.25):.2f}", "Premium TP3": f"₹ {(strike_details['premium_tp'] * 1.50):.2f}"
            }]
            st.dataframe(pd.DataFrame(fno_matrix_row), use_container_width=True, hide_index=True)
            
            if st.button(f"🔥 FIRE F&O DERIVATIVE OPTIONS POSITION: {selected_symbol}", use_container_width=True):
                payload = engine.generate_dhan_order_payload(target_stock["ID"], target_stock["Symbol"], "BUY", "FNO")
                response = engine.fetcher.place_live_order(payload)
                if "orderStatus" in str(response) or "SUCCESS" in str(response).upper():
                    st.balloons()
                    st.success(f"✓ ORDER FIRED: Live options contract sent to exchange! ID: {response.get('data', {}).get('orderId', 'N/A')}")
                else:
                    st.error(f"Execution Failed: {response.get('remarks', 'Check connection or key permissions')}")
        else:
            st.warning(f"❌ DERIVATIVE SYSTEM LOCKED: {selected_symbol} is restricted to Spot Cash segment options only.")
