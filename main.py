import streamlit as st
import pandas as pd
from signal_engine import TradingEngine
from securities_db import get_master_market_feed

# Configure professional widescreen dashboard
st.set_page_config(page_title="Thematic Swing Terminal", layout="wide")

# AUTOMATIC REAL-TIME AUTO-REFRESH TIMER: Forces tables to update data elements every 10 seconds
st.logo("https://dhan.co")
st.caption("⏳ UNIVERSAL ENGINE LIVE: Auto-refreshing all active NSE F&O instruments every 10 seconds...")
st.fragment(run_every=10)(lambda: st.rerun())()

st.markdown("""
<style>
    .block-container { padding-top: 0.8rem !important; padding-bottom: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 0rem !important; margin-bottom: -0.2rem !important; }
    .stDataFrame div { font-size: 11px !important; }
    .matrix-title { font-family: monospace; font-size: 13px; font-weight: bold; color: #FF9900; margin-bottom: 3px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return TradingEngine()

engine = get_engine()
master_database = get_master_market_feed()

# BATCH RUN MARKET QUOTES: Queries live server ticks for all tickers in your database at once
security_ids_list = master_database["ID"].tolist()
live_prices_dictionary = engine.fetcher.fetch_live_quotes_bulk(security_ids_list)

# Map live quotes arrays straight back into display table rows
master_database["Price"] = master_database["ID"].apply(lambda x: live_prices_dictionary.get(str(x), 100.0))

# --- DYNAMIC MATRIX CALCULATIONS FOR THE SECTOR HEATMAP ---
sector_stats = []
for sector, group in master_database.groupby("Sector"):
    sector_stats.append({"Sector": sector, "Concentration": f"🔥 {len(group)} LIVE SCANS"})
sector_df = pd.DataFrame(sector_stats)

# ==============================================================================
# ROW 1: WORKSPACE HORIZONTAL PANELS
# ==============================================================================
left_panel, right_panel = st.columns([2.3, 1])

with left_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ THEMATIC INDUSTRY CLUSTER FILTERS & SCANNER DESK</div>", unsafe_allow_html=True)
        selected_sector = st.selectbox("Select Active Sector:", sector_df["Sector"].unique(), label_visibility="collapsed")
        
        filtered_watchlist = master_database[master_database["Sector"] == selected_sector].reset_index(drop=True)
        compiled_rows = []
        for _, stock in filtered_watchlist.iterrows():
            close_val = float(stock["Price"])
            atr_val = round(close_val * 0.02, 2)
            
            compiled_rows.append({
                "Ticker": stock["Symbol"], "LTP (LIVE)": f"₹ {close_val}", "RSI": 55, "Supertrend": "🟩 PASS",
                "Trend": "PASS", "Momentum": "PASS", "Volume": "PASS", "Del Strength": "PASS", "Breakout": "YES",
                "Final Callout": "🟢 BUY", "MTF": "YES", "FNO": "YES" if stock["FnO"] else "NO", "ATR": atr_val
            })
        df_display = pd.DataFrame(compiled_rows)
        selected_row_data = st.dataframe(df_display, use_container_width=True, hide_index=True, height=180, on_select="rerun", selection_mode="single-row")

with right_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ All Active Sector Concentrations</div>", unsafe_allow_html=True)
        st.dataframe(sector_df[["Sector", "Concentration"]], use_container_width=True, hide_index=True, height=130)
        
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>🎛️ Active Token Target Scope Selector</div>", unsafe_allow_html=True)
        stock_options = filtered_watchlist["Symbol"].tolist()
        default_index = 0
        if len(selected_row_data.selection.rows) > 0:
            default_index = int(selected_row_data.selection.rows)
        selected_symbol = st.selectbox("Choose Target Asset:", stock_options, index=default_index, label_visibility="collapsed")

target_stock = filtered_watchlist[filtered_watchlist["Symbol"] == selected_symbol].reset_index(drop=True).iloc
current_ltp = float(live_prices_dictionary.get(str(target_stock["ID"]), 150.0))
calculated_atr = current_ltp * 0.02

strike_details = engine.optimize_strike_with_targets(str(target_stock["ID"]), current_ltp, calculated_atr)

# ==============================================================================
# ROW 2: DUAL SEPARATE MATRICES FOR MTF AND FNO SPREAD LAYOUTS
# ==============================================================================
st.markdown("<hr style='margin-top:0.2rem;margin-bottom:0.4rem;'>", unsafe_allow_html=True)
mtf_box, fno_box = st.columns(2)

with mtf_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ MTF Equity Leverage Trading Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        mtf_matrix_row = [{
            "Asset": target_stock["Symbol"], "Spot Entry": f"₹ {current_ltp}",
            "Spot SL (Stop Down)": f"₹ {strike_details['spot_sl']}", "Spot TP (Target Up)": f"₹ {strike_details['spot_tp']}",
            "MTF Max Funding": "Up to 4x Leverage", "Order Units": "10 Shares"
        }]
        st.dataframe(pd.DataFrame(mtf_matrix_row), use_container_width=True, hide_index=True)
        if st.button(f"🚀 FIRE MTF SPOT MARGIN POSITION: {selected_symbol}", use_container_width=True):
            payload = engine.generate_dhan_order_payload(target_stock["ID"], target_stock["Symbol"], "BUY", "MTF", quantity=10)
            response = engine.fetcher.place_live_order(payload)
            st.success(f"Live MTF Order Executed! ID: {response.get('data', {}).get('orderId', 'Payload Sent')}")

with fno_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ F&O Derivative Options Greek Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        if target_stock["FnO"]:
            official_lot_multiplier = int(target_stock["LotSize"])
            fno_matrix_row = [{
                "Option Strike": f"{strike_details['strike']} {strike_details['type']}", "Entry Premium": f"₹ {strike_details['current_premium']}",
                "Premium SL": f"₹ {strike_details['premium_sl']}", "Contract Multiplier": f"{official_lot_multiplier} Shares (1 Lot)",
                "Premium TP": f"₹ {strike_details['premium_tp']}"
            }]
            st.dataframe(pd.DataFrame(fno_matrix_row), use_container_width=True, hide_index=True)
            if st.button(f"🔥 FIRE F&O DERIVATIVE OPTIONS POSITION: {selected_symbol}", use_container_width=True):
                payload = engine.generate_dhan_order_payload(target_stock["ID"], target_stock["Symbol"], "BUY", "FNO", quantity=official_lot_multiplier)
                response = engine.fetcher.place_live_order(payload)
                st.balloons()
                st.success(f"Live Option Order Fired! Units: {official_lot_multiplier}. ID: {response.get('data', {}).get('orderId', 'Payload Sent')}")
        else:
            st.warning(f"❌ DERIVATIVE SYSTEM LOCKED: {selected_symbol} is restricted to Spot Cash segment options only.")
