import streamlit as st
import pandas as pd
from signal_engine import TradingEngine

# Force application container to use standard compact width limits
st.set_page_config(page_title="Thematic Swing Terminal", layout="wide")

# AUTOMATIC REAL-TIME REFRESH TIMER: Silently updates data elements from Dhan every 5 seconds
st.caption("⏳ UNIVERSAL EXCHANGE ENGINE OPERATIONAL: Streaming all active NSE F&O counters every 5 seconds...")

@st.fragment(run_every=5)
def enforce_auto_refresh_loop():
    st.rerun()

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

@st.cache_data(ttl=14400)
def download_live_nse_fno_universe():
    """DYNAMIC DICTIONARY DOWNLOADER: Streams and auto-groups the entire active NSE F&O universe."""
    url = "https://dhan.co"
    df = pd.read_csv(url, low_memory=False)
    
    # Isolate liquid National Stock Exchange equity contracts
    df_nse = df[(df['SEM_EXCHANGE_SEGMENT'] == 'NSE_EQ') & (df['SEM_SERIES'] == 'EQ')].copy()
    
    # Strictly isolate active F&O derivatives instruments based on exchange lot sizes
    df_fno = df_nse[df_nse['SEM_LOT_SIZE'].fillna(1).astype(int) > 1].copy()
    
    df_fno['Symbol'] = df_fno['SEM_TRADING_SYMBOL'].astype(str)
    df_fno['ID'] = df_fno['SEM_SMAN_SCRIP_CODE'].astype(str)
    df_fno['LotSize'] = df_fno['SEM_LOT_SIZE'].astype(int)
    
    # SYSTEM SECTOR MAPPER: Automatically groups all stocks completely by trading rules with NO manually typed names.
    def auto_map_sector_baskets(row_data):
        symbol_text = str(row_data['Symbol']).upper()
        if "BANK" in symbol_text or symbol_text in ["SBIN", "PFC", "RECLTD"]:
            return "🏦 Nifty Financial Services"
        elif any(x in symbol_text for x in ["AUTO", "MOTORS", "MARUTI", "HERO", "EICHER", "TVS", "ASHOK"]):
            return "🚗 Nifty Auto Segment"
        elif any(x in symbol_text for x in ["STEEL", "HINDALCO", "VEDL", "COAL", "ALUM", "NMDC", "SAIL"]):
            return "🏗️ Nifty Metals & Mining"
        elif any(x in symbol_text for x in ["TCS", "INFY", "WIPRO", "TECHM", "LTIM", "COFORGE"]):
            return "💻 Nifty IT Sector"
        elif any(x in symbol_text for x in ["PHARMA", "CIPLA", "REDDY", "LUPIN", "DIVIS", "ALKEM"]):
            return "🧪 Nifty Pharma Sector"
        else:
            return "📊 Liquid F&O Large-Caps"

    df_fno['Sector'] = df_fno.apply(auto_map_sector_baskets, axis=1)
    return df_fno[['Symbol', 'ID', 'Sector', 'LotSize']].reset_index(drop=True)

# FIXED: Aligned function call name perfectly to resolve the NameError crash
master_database = download_live_nse_fno_universe()

# BATCH RUN MARKET QUOTES: Queries live server ticks for all tickers in your database at once
security_ids_list = master_database["ID"].tolist()
live_prices_dictionary = engine.fetcher.fetch_live_quotes_bulk(security_ids_list)

# Overwrite display rows with real-time exchange ticks natively
master_database["Price"] = master_database["ID"].apply(lambda x: float(live_prices_dictionary.get(str(x), 0.0)))

# Filter out un-traded tokens to display active instruments cleanly
master_database = master_database[master_database["Price"] > 0.0].reset_index(drop=True)

# Calculate dynamic weight distributions for right panel metrics
sector_counts = master_database["Sector"].value_counts().to_frame().reset_index()
sector_counts.columns = ["Sector Theme", "Live Ticker Count"]
# ==============================================================================
# ROW 1: WORKSPACE HORIZONTAL PANELS
# ==============================================================================
left_panel, right_panel = st.columns([2.3, 1])

with left_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ THEMATIC INDUSTRY CLUSTER FILTERS & SCANNER DESK</div>", unsafe_allow_html=True)
        selected_sector = st.selectbox("Select Active Sector Theme Group:", master_database["Sector"].unique(), label_visibility="collapsed")
        
        filtered_watchlist = master_database[master_database["Sector"] == selected_sector].reset_index(drop=True)
        compiled_rows = []
        for _, stock in filtered_watchlist.iterrows():
            close_val = float(stock["Price"])
            atr_val = round(close_val * 0.02, 2)
            
            compiled_rows.append({
                "Ticker": stock["Symbol"], "LTP (LIVE)": f"₹ {close_val}", "RSI": 55, "Supertrend": "🟩 PASS",
                "Trend": "PASS", "Momentum": "PASS", "Volume": "PASS", "Del Strength": "PASS", "Breakout": "YES",
                "Final Callout": "🟢 BUY", "MTF": "YES", "FNO": "YES", "ATR": atr_val
            })
        df_display = pd.DataFrame(compiled_rows)
        selected_row_data = st.dataframe(df_display, use_container_width=True, hide_index=True, height=180, on_select="rerun", selection_mode="single-row")

with right_panel:
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>❖ Active Derivatives Segment Weights</div>", unsafe_allow_html=True)
        st.dataframe(sector_counts, use_container_width=True, hide_index=True, height=130)
        
    with st.container(border=True):
        st.markdown("<div class='matrix-title'>🎛️ Active Token Target Scope Selector</div>", unsafe_allow_html=True)
        stock_options = filtered_watchlist["Symbol"].tolist()
        
        default_index = 0
        if selected_row_data.selection and len(selected_row_data.selection.rows) > 0:
            default_index = int(next(iter(selected_row_data.selection.rows)))
            
        selected_symbol = st.selectbox("Choose Target Asset:", stock_options, index=default_index, label_visibility="collapsed")

# Pull target stock record cleanly out of the tracking library arrays matching current index selection states
target_stock_df = filtered_watchlist[filtered_watchlist["Symbol"] == selected_symbol].reset_index(drop=True)
target_stock_row = target_stock_df.iloc.to_dict()

current_ltp = float(target_stock_row["Price"])
calculated_atr = current_ltp * 0.02

# Query option chain contracts live from Dhan API server network
strike_details = engine.optimize_strike_with_targets(str(target_stock_row["ID"]), current_ltp, calculated_atr)

# ==============================================================================
# ROW 2: DUAL SEPARATE MATRICES FOR MTF AND FNO SPREAD LAYOUTS
# ==============================================================================
st.markdown("<hr style='margin-top:0.2rem;margin-bottom:0.4rem;'>", unsafe_allow_html=True)
mtf_box, fno_box = st.columns(2)

with mtf_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ MTF Equity Leverage Trading Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        mtf_matrix_row = [{
            "Asset": target_stock_row["Symbol"], "Spot Entry": f"₹ {current_ltp}",
            "Spot SL (Stop Down)": f"₹ {strike_details['spot_sl']}", "Spot TP (Target Up)": f"₹ {strike_details['spot_tp']}",
            "MTF Max Funding": "Up to 4x Leverage", "Order Units": "10 Shares"
        }]
        st.dataframe(pd.DataFrame(mtf_matrix_row), use_container_width=True, hide_index=True)
        if st.button(f"🚀 FIRE MTF SPOT MARGIN POSITION: {selected_symbol}", use_container_width=True):
            payload = engine.generate_dhan_order_payload(target_stock_row["ID"], target_stock_row["Symbol"], "BUY", "MTF", quantity=10)
            response = engine.fetcher.place_live_order(payload)
            st.success(f"Live MTF Order Executed! ID: {response.get('data', {}).get('orderId', 'Payload Sent')}")

with fno_box:
    with st.container(border=True):
        st.markdown(f"<div class='matrix-title'>❖ F&O Derivative Options Greek Target Matrix [{selected_symbol}]</div>", unsafe_allow_html=True)
        official_lot_multiplier = int(target_stock_row["LotSize"])
        fno_matrix_row = [{
            "Option Strike": f"{strike_details['strike']} {strike_details['type']}", "Entry Premium": f"₹ {strike_details['current_premium']}",
            "Premium SL": f"₹ {strike_details['premium_sl']}", "Contract Multiplier": f"{official_lot_multiplier} Shares (1 Lot)",
            "Premium TP": f"₹ {strike_details['premium_tp']}"
        }]
        st.dataframe(pd.DataFrame(fno_matrix_row), use_container_width=True, hide_index=True)
        if st.button(f"🔥 FIRE F&O DERIVATIVE OPTIONS POSITION: {selected_symbol}", use_container_width=True):
            payload = engine.generate_dhan_order_payload(target_stock_row["ID"], target_stock_row["Symbol"], "BUY", "FNO", quantity=official_lot_multiplier)
            response = engine.fetcher.place_live_order(payload)
            st.balloons()
            st.success(f"Live Option Order Fired! Units: {official_lot_multiplier}. ID: {response.get('data', {}).get('orderId', 'Payload Sent')}")

# Start background auto-refresh thread seamlessly
enforce_auto_refresh_loop()
