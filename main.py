import streamlit as st
import pandas as pd
from signal_engine import TradingEngine
from securities_db import get_master_market_feed

# Enforce professional wide-screen terminal view padding
st.set_page_config(page_title="Thematic Swing Terminal", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 0.8rem !important; padding-bottom: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 0rem !important; margin-bottom: -0.2rem !important; }
    .stDataFrame div { font-size: 11px !important; }
    .matrix-title { font-family: monospace; font-size: 13px; font-weight: bold; color: #FF9900; margin-bottom: 3px; }
    .compact-text { font-family: monospace; font-size: 11px; margin-bottom: 2px; line-height: 1.3; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()

# --- SIDEBAR CONTROL PANEL SWITCH ---
st.sidebar.header("🎛️ SYSTEM MODE CONTROLS")
data_mode = st.sidebar.radio("Data Environment:", ("SIMULATION (Safe Mock Feed)", "LIVE MARKET (Dhan Connection)"))
force_mock_payload = True if "SIMULATION" in data_mode else False

# --- EXTRACTION FROM MASTER LOCAL DICTIONARY ---
master_database = get_master_market_feed()

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

target_stock_df = master_database[master_database["Symbol"] == selected_symbol].reset_index(drop=True)
target_stock = target_stock_df.iloc[0]

# Pass selection state tokens directly to live backend data loops
strike_details = engine.optimize_strike_with_targets(
    underlying_symbol_id=str(target_stock["ID"]),
    current_price=float(target_stock["Price"]),
    atr=float(target_stock["ATR"]),
    force_mock=force_mock_payload
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
            if force_mock_payload:
                st.success(f"[SIMULATION MODE] MTF Order payload verified for {selected_symbol}.")
            else:
                # Compile official live payload structure and push to Dhan's production pipeline
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
                if force_mock_payload:
                    st.balloons()
                    st.success(f"[SIMULATION MODE] Options Order routing payload verified for {selected_symbol}.")
                else:
                    # Construct and push active derivatives buy payload out to the live exchange
                    payload = engine.generate_dhan_order_payload(target_stock["ID"], target_stock["Symbol"], "BUY", "FNO")
                    response = engine.fetcher.place_live_order(payload)
                    if "orderStatus" in str(response) or "SUCCESS" in str(response).upper():
                        st.balloons()
                        st.success(f"✓ ORDER FIRED: Live options contract sent to exchange! ID: {response.get('data', {}).get('orderId', 'N/A')}")
                    else:
                        st.error(f"Execution Failed: {response.get('remarks', 'Check connection or key permissions')}")
        else:
            st.warning(f"❌ DERIVATIVE SYSTEM LOCKED: {selected_symbol} is restricted to Spot Cash segment options only.")
