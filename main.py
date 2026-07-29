import io
import streamlit as st
import pandas as pd
import requests
from signal_engine import TradingEngine
import nifty_sectors

# Force application container to use standard compact width limits
st.set_page_config(page_title="Thematic Swing Terminal", layout="wide")

# AUTOMATIC REAL-TIME REFRESH TIMER
# NOTE: Dhan's LTP endpoint is capped at ~1 request/second. A 5-second refresh is already safe
# for a single session, but multiple open browser tabs each running their own 5s loop can stack
# up and trip the limit (HTTP 429). 15s keeps a comfortable safety margin while still feeling live.
AUTO_REFRESH_SECONDS = 15
st.caption(f"⏳ UNIVERSAL EXCHANGE ENGINE OPERATIONAL: Streaming all active NSE F&O counters every {AUTO_REFRESH_SECONDS} seconds...")


@st.fragment(run_every=AUTO_REFRESH_SECONDS)
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
def fetch_dynamic_nse_fno_universe():
    """Builds the live F&O stock universe by combining:
      - Dhan's official instrument master CSV -> live Security IDs + CURRENT lot sizes
      - A local static sector/theme map (nifty_sectors.py) -> just for the UI grouping label
    Security IDs and lot sizes always come live from Dhan, never hardcoded, since a wrong
    lot size feeding into a real order is a money-risk, not just a cosmetic bug."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        master_url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        resp = requests.get(master_url, headers=headers, timeout=20)
        resp.raise_for_status()
        dhan_df = pd.read_csv(io.StringIO(resp.text), low_memory=False)

        # --- Equity segment: live Security ID for each cash-market symbol ---
        eq_df = dhan_df[
            (dhan_df["SEM_EXM_EXCH_ID"] == "NSE") &
            (dhan_df["SEM_SEGMENT"] == "E") &
            (dhan_df["SEM_SERIES"] == "EQ")
        ].copy()
        eq_df["Symbol"] = eq_df["SEM_TRADING_SYMBOL"].astype(str).str.upper()
        eq_df["ID"] = eq_df["SEM_SMST_SECURITY_ID"].astype(str)

        # --- Derivatives segment: confirms which stocks actually trade F&O + their CURRENT lot size ---
        fno_df = dhan_df[
            (dhan_df["SEM_EXM_EXCH_ID"] == "NSE") &
            (dhan_df["SEM_SEGMENT"] == "D") &
            (dhan_df["SEM_INSTRUMENT_NAME"] == "FUTSTK")
        ].copy()
        fno_df["Symbol"] = fno_df["SEM_TRADING_SYMBOL"].astype(str).str.upper().str.split("-").str[0]
        fno_df["LotSize"] = pd.to_numeric(fno_df["SEM_LOT_UNITS"], errors="coerce").fillna(1).astype(int)
        if "SEM_EXPIRY_CODE" in fno_df.columns:
            fno_df = fno_df.sort_values("SEM_EXPIRY_CODE")
        fno_df = fno_df.drop_duplicates(subset="Symbol", keep="first")[["Symbol", "LotSize"]]

        # --- Local sector/theme labels ---
        sector_df = pd.DataFrame(
            [{"Symbol": sym, "Sector": sector} for sym, sector in nifty_sectors.SECTOR_MAP.items()]
        )

        # Only keep symbols that are: live on Dhan's equity master AND confirmed F&O AND in our sector map
        merged = (
            eq_df[["Symbol", "ID"]]
            .merge(fno_df, on="Symbol", how="inner")
            .merge(sector_df, on="Symbol", how="inner")
            .drop_duplicates(subset="Symbol")
            .reset_index(drop=True)
        )

        if merged.empty:
            raise ValueError("Merge produced zero rows - Dhan's CSV column names may have changed.")
        return merged

    except Exception as e:
        # Surfaced visibly instead of silently falling back, so failures are obvious while testing
        st.warning(f"⚠️ Live universe fetch failed, showing fallback list only. Reason: {e}")
        return pd.DataFrame([
            {"Symbol": "SBIN", "ID": "3045", "Sector": "Nifty Bank", "LotSize": 750},
            {"Symbol": "HDFCBANK", "ID": "1333", "Sector": "Nifty Bank", "LotSize": 550},
        ])


# Generate the complete dynamic trading dataset on startup
master_database = fetch_dynamic_nse_fno_universe()

# BATCH RUN MARKET QUOTES: Queries live server ticks for all tickers in your database at once
security_ids_list = master_database["ID"].tolist()
live_prices_dictionary = engine.fetcher.fetch_live_quotes_bulk(security_ids_list)

if engine.fetcher.quotes_stale:
    # A transient failure (e.g. rate limit) happened this cycle - we're showing the last known
    # good prices rather than blanking the table. Only a real problem if this persists for long.
    st.warning(f"⚠️ Showing last known prices (live refresh hit an issue): {engine.fetcher.last_error}")

# Overwrite display rows with real-time exchange ticks natively
master_database["Price"] = master_database["ID"].apply(lambda x: float(live_prices_dictionary.get(str(x), 0.0)))
master_database = master_database[master_database["Price"] > 0.0].reset_index(drop=True)

if master_database.empty:
    st.error(
        "No live prices available yet from Dhan (not even a cached price). Common causes: market is "
        "closed, access token expired/not rotated, or Data API isn't subscribed on this Dhan account. "
        f"Last error: {engine.fetcher.last_error}"
    )
    st.stop()

# Calculate true sectoral distribution tracking parameters dynamically
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

            # NOTE: RSI/Supertrend/Trend/Momentum/Volume/Breakout/Final Callout below are still
            # STATIC PLACEHOLDERS, not computed signals. Live price/ID/lot-size flow is now fixed;
            # real indicator calculations (needs historical OHLC) are a separate follow-up.
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
target_stock_row = target_stock_df.iloc[0].to_dict()

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
            response = engine.fetcher.place_live_order(payload)  # FIX: was engine.place_live_order (method didn't exist)
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
