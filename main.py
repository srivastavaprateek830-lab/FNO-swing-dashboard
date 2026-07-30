import io
import math
import streamlit as st
import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from signal_engine import TradingEngine
import nifty_sectors

# Force application container to use standard compact width limits
st.set_page_config(page_title="FNO Universe Scanner", layout="wide")

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
    .active-selection-box {
        font-family: monospace; font-size: 22px; font-weight: bold; color: #FFFFFF;
        background-color: #1a1c23; border: 1px solid #333; border-radius: 6px;
        padding: 10px 14px; text-align: center;
    }
    /* Floating adjustable block sizing: drag the bottom-right corner of any bordered panel
       to resize it manually. This is a native browser resize handle, not a drag-reposition
       grid - each panel can be made bigger/smaller in place. */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        resize: both;
        overflow: auto;
        min-width: 260px;
        min-height: 120px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine():
    return TradingEngine()


engine = get_engine()


def score_to_label(score: int):
    """Maps a 0-100 composite signal score to a 5-tier buy/sell label + gauge color."""
    if score >= 80:
        return "🟢 STRONG BUY", "#1a9c4b"
    elif score >= 60:
        return "🟩 BUY", "#8bc34a"
    elif score >= 40:
        return "🟡 NEUTRAL", "#ffd54f"
    elif score >= 20:
        return "🟠 SELL", "#ff9800"
    else:
        return "🔴 STRONG SELL", "#e53935"


def dot(pass_value) -> str:
    """Converts a PASS/FAIL/YES/NO/N-A style value into a colored dot indicator."""
    if pass_value in ("PASS", "YES"):
        return "🟢"
    elif pass_value in ("FAIL", "NO"):
        return "🔴"
    return "⚪"


def draw_confidence_gauge(score: int, label: str):
    """Speedometer-style gauge with a real pointing needle, rendered with matplotlib
    (tested directly in development to confirm the needle angle lines up with the bands)."""
    fig, ax = plt.subplots(figsize=(4, 2.6), subplot_kw={"aspect": "equal"})
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    bands = [
        (0, 20, "#e53935"), (20, 40, "#ff9800"), (40, 60, "#ffd54f"),
        (60, 80, "#8bc34a"), (80, 100, "#1a9c4b"),
    ]
    for lo, hi, color in bands:
        theta1 = 180 - (hi / 100) * 180
        theta2 = 180 - (lo / 100) * 180
        ax.add_patch(mpatches.Wedge((0, 0), 1.0, theta1, theta2, width=0.35, facecolor=color, edgecolor="#0e1117", linewidth=1))

    angle_rad = math.radians(180 - (score / 100) * 180)
    needle_len = 0.82
    x_tip, y_tip = needle_len * math.cos(angle_rad), needle_len * math.sin(angle_rad)
    ax.plot([0, x_tip], [0, y_tip], color="white", linewidth=3, solid_capstyle="round", zorder=5)
    ax.add_patch(mpatches.Circle((0, 0), 0.06, facecolor="white", edgecolor="white", zorder=6))

    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.15, 1.15)
    ax.axis("off")
    ax.text(0, -0.05, label, ha="center", va="top", fontsize=13, fontweight="bold", color="white")
    ax.text(0, 0.45, f"{score}%", ha="center", va="center", fontsize=20, fontweight="bold", color="white")
    fig.tight_layout()
    return fig


@st.cache_data(ttl=14400)
def fetch_dynamic_nse_fno_universe():
    """Builds the live F&O stock universe by combining:
      - Dhan's official instrument master CSV -> live Security IDs + CURRENT lot sizes
      - A local static sector/theme map (nifty_sectors.py) -> kept only for internal reference
    Security IDs and lot sizes always come live from Dhan, never hardcoded, since a wrong
    lot size feeding into a real order is a money-risk, not just a cosmetic bug.
    This is cached for 4 hours - it does NOT re-run on every refresh cycle."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        master_url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        resp = requests.get(master_url, headers=headers, timeout=20)
        resp.raise_for_status()
        dhan_df = pd.read_csv(io.StringIO(resp.text), low_memory=False)

        eq_df = dhan_df[
            (dhan_df["SEM_EXM_EXCH_ID"] == "NSE") &
            (dhan_df["SEM_SEGMENT"] == "E") &
            (dhan_df["SEM_SERIES"] == "EQ")
        ].copy()
        eq_df["Symbol"] = eq_df["SEM_TRADING_SYMBOL"].astype(str).str.upper()
        eq_df["ID"] = eq_df["SEM_SMST_SECURITY_ID"].astype(str)

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

        sector_df = pd.DataFrame(
            [{"Symbol": sym, "Sector": sector} for sym, sector in nifty_sectors.SECTOR_MAP.items()]
        )

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
        st.warning(f"⚠️ Live universe fetch failed, showing fallback list only. Reason: {e}")
        return pd.DataFrame([
            {"Symbol": "SBIN", "ID": "3045", "Sector": "Nifty Bank", "LotSize": 750},
            {"Symbol": "HDFCBANK", "ID": "1333", "Sector": "Nifty Bank", "LotSize": 550},
        ])


static_universe = fetch_dynamic_nse_fno_universe()


# ==============================================================================
# EVERYTHING BELOW THIS POINT LIVES INSIDE ONE FRAGMENT - run_every re-executes ONLY
# this function on a timer, and widget clicks inside it also only rerun this fragment,
# not the whole page.
# ==============================================================================
@st.fragment(run_every=AUTO_REFRESH_SECONDS if auto_refresh_enabled else None)
def live_dashboard(master_database):
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

    # ==============================================================================
    # ROW 1: FULL FNO UNIVERSE SCANNER (no sector filter - every F&O stock, one long list)
    # ==============================================================================
    left_panel, right_panel = st.columns([2.3, 1])

    with left_panel:
        with st.container(border=True):
            st.markdown("<div class='matrix-title'>❖ FNO UNIVERSE SCANNER</div>", unsafe_allow_html=True)

            # Real indicator computation per stock. Historical candles are cached 6h per symbol
            # and shared across all users, so this is only slow the very first time - after that
            # it's instant. First load of the FULL universe can take a while; a spinner shows why.
            compiled_rows = []
            with st.spinner("Computing live signals across the full F&O universe (first load only)..."):
                for _, stock in master_database.iterrows():
                    close_val = float(stock["Price"])
                    atr_val = round(close_val * 0.02, 2)
                    sig = engine.fetcher.compute_indicator_signals(str(stock["ID"]), close_val)
                    callout_label, _ = score_to_label(sig["score"])

                    compiled_rows.append({
                        "Ticker": stock["Symbol"], "LTP (LIVE)": f"₹ {close_val}", "% Chg": f"{stock['PctChg']:+.2f}%",
                        "RSI": sig["rsi"] if sig["rsi"] is not None else "N/A",
                        "Supertrend": dot(sig["supertrend"]), "Trend": dot(sig["trend"]),
                        "Momentum": dot(sig["momentum"]), "Volume": dot(sig["volume"]),
                        "Breakout": dot(sig["breakout"]), "Final Callout": callout_label,
                        "MTF": "YES", "FNO": "YES", "ATR": atr_val, "_score": sig["score"],
                    })

            df_display = pd.DataFrame(compiled_rows).sort_values("_score", ascending=False).reset_index(drop=True)
            scores_by_symbol = dict(zip(df_display["Ticker"], df_display["_score"]))
            df_display_visible = df_display.drop(columns=["_score"])

            selected_row_data = st.dataframe(
                df_display_visible, use_container_width=True, hide_index=True, height=520,
                on_select="rerun", selection_mode="single-row",
            )

    with right_panel:
        with st.container(border=True):
            st.markdown("<div class='matrix-title'>🎯 Active Selection</div>", unsafe_allow_html=True)

            all_symbols_ranked = df_display["Ticker"].tolist()
            symbol_key = "selected_symbol"
            if symbol_key not in st.session_state or st.session_state[symbol_key] not in all_symbols_ranked:
                # Default to the top-ranked (highest confidence) stock if nothing picked yet
                st.session_state[symbol_key] = all_symbols_ranked[0] if all_symbols_ranked else None

            if selected_row_data.selection and len(selected_row_data.selection.rows) > 0:
                row_idx = int(next(iter(selected_row_data.selection.rows)))
                if row_idx < len(df_display):
                    st.session_state[symbol_key] = df_display.iloc[row_idx]["Ticker"]

            selected_symbol = st.session_state[symbol_key]
            st.markdown(f"<div class='active-selection-box'>{selected_symbol}</div>", unsafe_allow_html=True)
            st.caption("Click any row in the scanner to change this.")

        with st.container(border=True):
            gauge_score = scores_by_symbol.get(selected_symbol, 50)
            callout_text, _ = score_to_label(gauge_score)
            st.markdown(f"<div class='matrix-title'>❖ Signal Confidence: {selected_symbol}</div>", unsafe_allow_html=True)
            fig = draw_confidence_gauge(gauge_score, callout_text)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.caption("Composite of Trend / Momentum / Volume / Breakout / Supertrend. Not investment advice.")

    # Pull target stock record for the MTF/FNO panels below
    target_stock_df = master_database[master_database["Symbol"] == selected_symbol].reset_index(drop=True)
    if target_stock_df.empty:
        return
    target_stock_row = target_stock_df.iloc[0].to_dict()

    current_ltp = float(target_stock_row["Price"])
    calculated_atr = current_ltp * 0.02
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


live_dashboard(static_universe)
