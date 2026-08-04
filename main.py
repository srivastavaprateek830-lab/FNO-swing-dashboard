import io
import datetime as dt
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
import requests
from signal_engine import TradingEngine
import nifty_sectors

st.set_page_config(page_title="FNO Universe Scanner", layout="wide")

IST = ZoneInfo("Asia/Kolkata")  # Streamlit Cloud's servers run in UTC, not IST - without this,
                                 # every timestamp on the page is off by +5:30

# How often the live panel refreshes itself, in seconds.
AUTO_REFRESH_SECONDS = 30
BUY_SCORE_THRESHOLD = 60     # score >= this counts as a BUY-side signal
SELL_SCORE_THRESHOLD = 40    # score <= this counts as a SELL-side signal
BUY_EXIT_THRESHOLD = 50      # once BUY, only reverts to neutral if score drops below this
SELL_EXIT_THRESHOLD = 50     # once SELL, only reverts to neutral if score rises above this

with st.sidebar:
    st.markdown("### ⚙️ Refresh Controls")
    auto_refresh_enabled = st.checkbox(
        "Enable auto-refresh", value=True,
        help="Turn off to stop background polling entirely and use 'Refresh Now' instead.",
    )
    st.button("🔄 Refresh Now", use_container_width=True)

    st.markdown("### 📐 Layout Controls")
    scanner_width_pct = st.slider(
        "Scanner panel width", min_value=50, max_value=85, value=70, step=1,
        help="Shrink this to give the Buy/Sell alert boxes more room.",
    )
    compact_columns = st.checkbox(
        "Compact scanner columns", value=True,
        help="Narrows every scanner column to reduce wasted header space.",
    )
    scanner_height_px = st.slider(
        "Scanner panel height (px)", min_value=400, max_value=1200, value=700, step=20,
    )

if auto_refresh_enabled:
    st.caption(f"⏳ Streaming all active NSE F&O counters every {AUTO_REFRESH_SECONDS} seconds...")
else:
    st.caption("⏸️ Auto-refresh is OFF. Use 'Refresh Now' in the sidebar to pull live data on demand.")

st.markdown("""
<style>
    .block-container { padding-top: 0.8rem !important; padding-bottom: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-bottom: 0rem !important; margin-bottom: -0.2rem !important; }
    .matrix-title { font-family: monospace; font-size: 12px; font-weight: bold; color: #FF9900; margin-bottom: 2px; }
    .buy-title { font-family: monospace; font-size: 10px; font-weight: bold; color: #1a9c4b; margin-bottom: 2px; }
    .sell-title { font-family: monospace; font-size: 10px; font-weight: bold; color: #e53935; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine():
    return TradingEngine()


@st.cache_resource
def get_signal_history_store():
    """Persists across all refresh cycles AND all users of this app (until the app is rebooted)
    - this is what lets us say 'this BUY signal has been active since 10:42 AM' instead of just
    'BUY' with no sense of when it actually triggered. Resets on reboot since there's no memory
    of what happened before the app started watching."""
    return {}


engine = get_engine()
signal_history_store = get_signal_history_store()


def dot(pass_value) -> str:
    if pass_value in ("PASS", "YES"):
        return "🟢"
    elif pass_value in ("FAIL", "NO"):
        return "🔴"
    return "⚪"


@st.cache_data(ttl=14400)
def fetch_dynamic_nse_fno_universe():
    """Builds the live F&O stock universe by combining:
      - Dhan's official instrument master CSV -> live Security IDs + CURRENT lot sizes
      - A local static sector/theme map (nifty_sectors.py) -> kept only for internal reference
    Security IDs and lot sizes always come live from Dhan, never hardcoded."""
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


BACKTEST_HORIZONS = (1, 3, 5, 10, 15, 20)  # trading days held after the signal fires


@st.cache_data(ttl=21600, show_spinner=False)
def compute_backtest_summary(_engine, universe_df, horizons):
    """Real, verifiable accuracy check: walks EVERY stock's historical daily candles through
    the exact same scoring logic the live scanner uses, then checks what actually happened to
    price over SEVERAL different holding periods. No live_price/lookahead leakage - each day's
    score only ever sees data up to that day. Cached for 6h - this is a research number, not
    something that needs to be live."""
    band_defs = [("0-20 (Strong Sell)", 0, 20), ("20-40 (Sell)", 20, 40), ("40-60 (Neutral)", 40, 60),
                 ("60-80 (Buy)", 60, 80), ("80-100 (Strong Buy)", 80, 101)]
    # {band: {horizon: [returns...]}}
    buckets = {band: {h: [] for h in horizons} for band, _, _ in band_defs}

    for _, stock in universe_df.iterrows():
        hist = _engine.fetcher.fetch_historical_daily(str(stock["ID"]))
        if not hist:
            continue
        multi = _engine.fetcher.backtest_signal_scores_multi_horizon(hist, horizons=horizons)
        for h, pairs in multi.items():
            for score, fwd_ret in pairs:
                for band, lo, hi in band_defs:
                    if lo <= score < hi:
                        buckets[band][h].append(fwd_ret)
                        break

    rows = []
    for band, _, _ in band_defs:
        row = {"Score Band": band}
        best_h, best_win_rate = None, -1
        for h in horizons:
            rets = buckets[band][h]
            if not rets:
                row[f"{h}d Win Rate"] = None
                row[f"{h}d Avg Return"] = None
                continue
            win_rate = round(100 * sum(1 for r in rets if r > 0) / len(rets), 1)
            avg_ret = round(sum(rets) / len(rets), 2)
            row[f"{h}d Win Rate"] = win_rate
            row[f"{h}d Avg Return"] = f"{avg_ret:+.2f}%"
            if win_rate > best_win_rate:
                best_h, best_win_rate = h, win_rate
        row["Signals Tested"] = len(buckets[band][horizons[0]])
        row["Best Horizon"] = f"{best_h}d ({best_win_rate}%)" if best_h else "N/A"
        rows.append(row)
    return pd.DataFrame(rows)


with st.expander("📊 Backtested Signal Accuracy (real, computed from this dashboard's own logic)", expanded=False):
    st.caption(
        "For every stock in the universe, walks through its full price history day-by-day, computes what this "
        "dashboard's score WOULD have shown using only data available as of that day (no lookahead), and checks "
        "what price actually did over several different holding periods. This is OUR system's own verifiable "
        "track record - not a third party's marketing claim."
    )
    with st.spinner("Running backtest across the full universe and multiple holding periods (first load only, cached for 6h after)..."):
        backtest_df = compute_backtest_summary(engine, static_universe, BACKTEST_HORIZONS)
    st.dataframe(backtest_df, use_container_width=True, hide_index=True)
    st.caption(
        "Read a row as: 'historically, when the score was in this band, here's the win rate and average return "
        "for holding 1/3/5/10/15/20 trading days.' The 'Best Horizon' column shows which holding period had the "
        "highest win rate for that band - use this to decide how long to hold after an alert fires, rather than "
        "guessing. A rising win-rate/return from Strong Sell to Strong Buy is what would make this logic look "
        "genuinely useful; a flat or inconsistent pattern means it isn't adding real predictive value yet."
    )




# ==============================================================================
# EVERYTHING BELOW LIVES INSIDE ONE FRAGMENT - run_every re-executes ONLY this function
# on a timer, and widget clicks inside it also only rerun this fragment, not the whole page.
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
    # Compute real signals for every stock, and update the persistent "since when has this
    # stock been on the BUY/SELL side" timestamp store.
    #
    # Hysteresis: a stock only ENTERS Buy/Sell at the 60/40 thresholds, but only EXITS back to
    # Neutral once it crosses back past 50. Without this, a score sitting right at the boundary
    # (e.g. flickering between 59 and 61 on live price noise) would flip direction - and reset
    # its "Signal Since" timestamp - almost every refresh cycle, which defeats the whole point
    # of tracking "how long has this actually been a live signal."
    # ==============================================================================
    now = dt.datetime.now(IST)
    compiled_rows = []
    with st.spinner("Computing live signals across the full F&O universe (first load only)..."):
        for _, stock in master_database.iterrows():
            symbol = stock["Symbol"]
            close_val = float(stock["Price"])
            sig = engine.fetcher.compute_indicator_signals(str(stock["ID"]), close_val)
            atr_val = sig["atr"] if sig.get("atr") else round(close_val * 0.02, 2)
            score = sig["score"]

            prev = signal_history_store.get(symbol)
            prev_direction = prev["direction"] if prev else "NEUTRAL"
            if prev_direction == "BUY":
                direction = "NEUTRAL" if score < BUY_EXIT_THRESHOLD else "BUY"
            elif prev_direction == "SELL":
                direction = "NEUTRAL" if score > SELL_EXIT_THRESHOLD else "SELL"
            else:
                direction = "BUY" if score >= BUY_SCORE_THRESHOLD else ("SELL" if score <= SELL_SCORE_THRESHOLD else "NEUTRAL")

            just_flipped = prev is None or prev_direction != direction
            if just_flipped:
                signal_history_store[symbol] = {"direction": direction, "since": now, "score": score}
            else:
                prev["score"] = score  # keep the original "since" timestamp, just refresh the score

            # Combined categorical label - "Turning Bullish/Bearish" only on the cycle a stock
            # actually crosses into Buy/Sell territory, otherwise a static score-band label.
            if just_flipped and direction == "BUY":
                signal_label = "🔵 Turning Bullish"
            elif just_flipped and direction == "SELL":
                signal_label = "🟠 Turning Bearish"
            elif score >= 80:
                signal_label = "🟢 Strong Buy"
            elif score >= 60:
                signal_label = "🟢 Buy"
            elif score <= 20:
                signal_label = "🔴 Strong Sell"
            elif score <= 40:
                signal_label = "🔴 Sell"
            else:
                signal_label = "⚪ Neutral"

            compiled_rows.append({
                "Ticker": symbol, "LTP": f"₹ {close_val}", "% Chg": f"{stock['PctChg']:+.2f}%",
                "RSI": sig["rsi"] if sig["rsi"] is not None else "N/A",
                "Supertrend": dot(sig["supertrend"]), "Momentum": dot(sig["momentum"]),
                "Volume": dot(sig["volume"]), "Breakout": dot(sig["breakout"]),
                "Signal": signal_label, "ATR": atr_val,
                "_score": score, "_atr": atr_val, "_price": close_val, "_id": stock["ID"],
            })

    df_all = pd.DataFrame(compiled_rows).sort_values("_score", ascending=False).reset_index(drop=True)
    df_scanner_visible = df_all.drop(columns=["_score", "_atr", "_price", "_id"])

    st.caption(f"🕒 Last updated: {now.strftime('%d-%b-%Y %H:%M:%S')} IST - if this timestamp isn't moving, auto-refresh isn't running.")

    left_panel, right_panel = st.columns([scanner_width_pct, 100 - scanner_width_pct])

    with left_panel:
        with st.container(border=True):
            st.markdown("<div class='matrix-title'>❖ FNO UNIVERSE SCANNER</div>", unsafe_allow_html=True)
            if compact_columns:
                narrow = st.column_config.Column(width="small")
                col_config = {c: narrow for c in df_scanner_visible.columns if c != "Ticker"}
            else:
                col_config = None
            st.dataframe(
                df_scanner_visible, use_container_width=True, hide_index=True,
                height=scanner_height_px, column_config=col_config,
            )

    # ==============================================================================
    # Top 5 BUY / Top 5 SELL alert boxes - sorted by MOST RECENT trigger time first
    # (a real alert feed, not just a static ranked list), each with ATR-based T1/T2/SL.
    # ==============================================================================
    def _targets(price, atr, is_buy):
        sign = 1 if is_buy else -1
        return {
            "SL": round(price - sign * 1.5 * atr, 2),
            "T1": round(price + sign * 1.5 * atr, 2),
            "T2": round(price + sign * 3.0 * atr, 2),
        }

    with right_panel:
        with st.container(border=True):
            st.markdown("<div class='buy-title'>🟢 TOP 5 BUY SIGNALS</div>", unsafe_allow_html=True)
            buy_symbols = [s for s, v in signal_history_store.items() if v["direction"] == "BUY"]
            buy_symbols.sort(key=lambda s: signal_history_store[s]["since"], reverse=True)
            buy_rows = []
            for sym in buy_symbols[:5]:
                match = df_all[df_all["Ticker"] == sym]
                if match.empty:
                    continue
                r = match.iloc[0]
                tgt = _targets(r["_price"], r["_atr"], is_buy=True)
                buy_rows.append({
                    "Ticker": sym, "LTP": f"₹ {r['_price']}", "Score": r["_score"],
                    "SL": f"₹ {tgt['SL']}", "T1": f"₹ {tgt['T1']}", "T2": f"₹ {tgt['T2']}",
                    "Signal Since": signal_history_store[sym]["since"].strftime("%d-%b %H:%M"),
                })
            if buy_rows:
                st.dataframe(pd.DataFrame(buy_rows), use_container_width=True, hide_index=True, height=215)
            else:
                st.caption("No stocks currently qualify as a BUY signal.")

        with st.container(border=True):
            st.markdown("<div class='sell-title'>🔴 TOP 5 SELL SIGNALS</div>", unsafe_allow_html=True)
            sell_symbols = [s for s, v in signal_history_store.items() if v["direction"] == "SELL"]
            sell_symbols.sort(key=lambda s: signal_history_store[s]["since"], reverse=True)
            sell_rows = []
            for sym in sell_symbols[:5]:
                match = df_all[df_all["Ticker"] == sym]
                if match.empty:
                    continue
                r = match.iloc[0]
                tgt = _targets(r["_price"], r["_atr"], is_buy=False)
                sell_rows.append({
                    "Ticker": sym, "LTP": f"₹ {r['_price']}", "Score": r["_score"],
                    "SL": f"₹ {tgt['SL']}", "T1": f"₹ {tgt['T1']}", "T2": f"₹ {tgt['T2']}",
                    "Signal Since": signal_history_store[sym]["since"].strftime("%d-%b %H:%M"),
                })
            if sell_rows:
                st.dataframe(pd.DataFrame(sell_rows), use_container_width=True, hide_index=True, height=215)
            else:
                st.caption("No stocks currently qualify as a SELL signal.")

        st.caption(
            "Sorted by most recently triggered first. 'Signal Since' resets after each app reboot - "
            "there's no memory of signals from before the app started watching this session."
        )


live_dashboard(static_universe)
