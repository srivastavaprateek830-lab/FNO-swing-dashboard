import io
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from signal_engine import TradingEngine
import nifty_sectors

# Force application container to use standard compact width limits
st.set_page_config(page_title="Thematic Swing Terminal", layout="wide")

# How often the live panel refreshes itself, in seconds.
# Change this single number to slow it down further (e.g. 60 for once a minute).
AUTO_REFRESH_SECONDS = 30

with st.sidebar:
    st.markdown("### ⚙️ Refresh Controls")
    auto_refresh_enabled = st.checkbox(
        "Enable auto-refresh",
        value=True,
        help="Turn off to stop background polling entirely and use 'Refresh Now' instead.",
    )
    st.button("🔄 Refresh Now", use_container_width=True)

if auto_refresh_enabled:
    st.caption(f"⏳ UNIVERSAL EXCHANGE ENGINE OPERATIONAL: Streaming all active NSE F&O counters every {AUTO_REFRESH_SECONDS} seconds...")
else:
    st.caption("⏸️ Auto-refresh is OFF. Use 'Refresh Now' in the sidebar to pull live data on demand.")

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


def score_to_label(score: int):
    """Maps a 0-100 composite signal score to a callout label + gauge color band."""
    if score >= 75:
        return "🟢 STRONG BUY", "#1a9c4b"
    elif score >= 50:
        return "🟢 BUY", "#8bc34a"
    elif score >= 25:
        return "🟠 WEAK", "#ff9800"
    else:
        return "🔴 AVOID", "#e53935"


@st.cache_data(ttl=14400)
def fetch_dynamic_nse_fno_universe():
    """Builds the live F&O stock universe by combining:
      - Dhan's official instrument master CSV -> live Security IDs + CURRENT lot sizes
      - A local static sector/theme map (nifty_sectors.py) -> just for the UI grouping label
    Security IDs and lot sizes always come live from Dhan, never hardcoded, since a wrong
    lot size feeding into a real order is a money-risk, not just a cosmetic bug.
    This is cached for 4 hours - it does NOT re-run on every refresh cycle."""
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


# Built once (cached 4h) - the stock universe itself doesn't need to redraw every refresh cycle
static_universe = fetch_dynamic_nse_fno_universe()


# ==============================================================================
# EVERYTHING BELOW THIS POINT LIVES INSIDE ONE FRAGMENT.
# That means: (a) run_every re-executes ONLY this function on a timer, not the whole
# page - no full-dashboard flicker, and (b) clicking the selectbox, dataframe row, or
# Fire buttons inside it also only reruns this fragment, not the whole app.
# ==============================================================================
@st.fragment(run_every=AUTO_REFRESH_SECONDS if auto_refresh_enabled else None)
def live_dashboard(master_database):
    # Single batched call gets us BOTH live price and previous close (for %chg) at once.
    security_ids_list = master_database["ID"].tolist()
    quotes = engine.fetcher.fetch_quotes_bulk(security_ids_list)

    if getattr(engine.fetcher, "quotes_stale", False):
        st.warning(f"⚠️ Showing last known prices (live refresh hit an issue): {engine.fetcher.last_error}")

    master_database = master_database.copy()
    master_database["Price"] = master_database["ID"].apply(lambda x: float(quotes.get(str(x), {}).get("price", 0.0)))
    master_database["PctChg"] = master_database["ID"].apply(lambda x: float(quotes.get(str(x), {}).get("pct_chg", 0.0)))
    master_database = master_database[master_database["Price"] > 0.0].reset_index(drop=True)

    if master_database.empty:
        st.error(
            "No live prices available yet from Dhan (not even a cached price). Common causes: market is "
            "closed, access token expired/not rotated, or Data API isn't subscribed on this Dhan account. "
            f"Last error: {engine.fetcher.last_error}"
        )
        return

    # Sector performance today: equal-weighted average %chg across this dashboard's F&O
    # constituents per sector (not NSE's official weighted index value, just our own universe).
    sector_perf = (
        master_database.groupby("Sector")
        .agg(**{"Live Ticker Count": ("Symbol", "count"), "Avg % Chg": ("PctChg", "mean")})
        .reset_index()
        .sort_values("Avg % Chg", ascending=False)
    )
    sector_perf["Avg % Chg"] = sector_perf["Avg % Chg"].round(2)
    _color_fn = lambda v: f"color: {'#2ecc71' if v >= 0 else '#e74c3c'}"
    _styler = sector_perf.style.format({"Avg % Chg": "{:+.2f}%"})
    # pandas renamed Styler.applymap -> Styler.map in 2.1, then removed the old name later -
    # try the new name first, fall back to the old one so this works across pandas versions.
    if hasattr(_styler, "map"):
        sector_perf_styled = _styler.map(_color_fn, subset=["Avg % Chg"])
    else:
        sector_perf_styled = _styler.applymap(_color_fn, subset=["Avg % Chg"])

    # ==============================================================================
    # ROW 1: WORKSPACE HORIZONTAL PANELS
    # ==============================================================================
    left_panel, right_panel = st.columns([2.3, 1])

    with left_panel:
        with st.container(border=True):
            st.markdown("<div class='matrix-title'>❖ THEMATIC INDUSTRY CLUSTER FILTERS & SCANNER DESK</div>", unsafe_allow_html=True)
            selected_sector = st.selectbox("Select Active Sector Theme Group:", master_database["Sector"].unique(), label_visibility="collapsed")

            filtered_watchlist = master_database[master_database["Sector"] == selected_sector].reset_index(drop=True)

            # Real indicator computation per stock (historical candles cached 6h per symbol,
            # so this is only slow the first time a sector is opened - after that it's instant).
            compiled_rows = []
            scores_by_symbol = {}
            for _, stock in filtered_watchlist.iterrows():
                close_val = float(stock["Price"])
                atr_val = round(close_val * 0.02, 2)
                sig = engine.fetcher.compute_indicator_signals(str(stock["ID"]), close_val)
                scores_by_symbol[stock["Symbol"]] = sig["score"]
                callout_label, _ = score_to_label(sig["score"])

                compiled_rows.append({
                    "Ticker": stock["Symbol"], "LTP (LIVE)": f"₹ {close_val}", "% Chg": f"{stock['PctChg']:+.2f}%",
                    "RSI": sig["rsi"] if sig["rsi"] is not None else "N/A",
                    "Supertrend": sig["supertrend"], "Trend": sig["trend"], "Momentum": sig["momentum"],
                    "Volume": sig["volume"], "Del Strength": "N/A", "Breakout": sig["breakout"],
                    "Final Callout": callout_label, "MTF": "YES", "FNO": "YES", "ATR": atr_val,
                })
            df_display = pd.DataFrame(compiled_rows)
            selected_row_data = st.dataframe(df_display, use_container_width=True, hide_index=True, height=180, on_select="rerun", selection_mode="single-row")

    with right_panel:
        with st.container(border=True):
            st.markdown("<div class='matrix-title'>❖ Sector Performance Today</div>", unsafe_allow_html=True)
            st.dataframe(sector_perf_styled, use_container_width=True, hide_index=True, height=180)
            st.caption("Equal-weighted average across this dashboard's F&O stocks per sector - not NSE's official index value.")

        with st.container(border=True):
            st.markdown("<div class='matrix-title'>🎛️ Active Token Target Scope Selector</div>", unsafe_allow_html=True)
            stock_options = filtered_watchlist["Symbol"].tolist()

            # --- Sync fix: the scanner table's row-selection is the source of truth. Clicking a
            # row here now FORCES the dropdown below to match it, instead of the dropdown holding
            # onto whatever it was last set to (which is what caused the "random" MTF/FNO panels).
            symbol_key = f"selected_symbol_{selected_sector}"
            if symbol_key not in st.session_state or st.session_state[symbol_key] not in stock_options:
                st.session_state[symbol_key] = stock_options[0] if stock_options else None

            if selected_row_data.selection and len(selected_row_data.selection.rows) > 0:
                row_idx = int(next(iter(selected_row_data.selection.rows)))
                if row_idx < len(filtered_watchlist):
                    st.session_state[symbol_key] = filtered_watchlist.iloc[row_idx]["Symbol"]

            selected_symbol = st.selectbox("Choose Target Asset:", stock_options, key=symbol_key, label_visibility="collapsed")

    # Pull target stock record cleanly out of the tracking library arrays matching current index selection states
    target_stock_df = filtered_watchlist[filtered_watchlist["Symbol"] == selected_symbol].reset_index(drop=True)
    target_stock_row = target_stock_df.iloc[0].to_dict()

    current_ltp = float(target_stock_row["Price"])
    calculated_atr = current_ltp * 0.02

    # Query option chain contracts live from Dhan API server network
    strike_details = engine.optimize_strike_with_targets(str(target_stock_row["ID"]), current_ltp, calculated_atr)

    # ==============================================================================
    # ROW 1.5: CONFIDENCE GAUGE FOR THE CURRENTLY SELECTED STOCK
    # ==============================================================================
    gauge_score = scores_by_symbol.get(selected_symbol, 50)
    callout_text, callout_color = score_to_label(gauge_score)

    gauge_col, _spacer = st.columns([1, 2])
    with gauge_col:
        with st.container(border=True):
            st.markdown(f"<div class='matrix-title'>❖ Signal Confidence: {selected_symbol}</div>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=gauge_score,
                number={"suffix": "%", "font": {"size": 28}},
                gauge={
                    "axis": {"range": [0, 100], "tickvals": [0, 25, 50, 75, 100]},
                    "bar": {"color": callout_color},
                    "steps": [
                        {"range": [0, 25], "color": "#e53935"},
                        {"range": [25, 50], "color": "#ff9800"},
                        {"range": [50, 75], "color": "#8bc34a"},
                        {"range": [75, 100], "color": "#1a9c4b"},
                    ],
                },
                title={"text": callout_text, "font": {"size": 16}},
            ))
            fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Composite of Trend / Momentum / Volume / Breakout / Supertrend signals above. "
                "Not investment advice - a mechanical count of how many of these five checks currently pass."
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


live_dashboard(static_universe)
