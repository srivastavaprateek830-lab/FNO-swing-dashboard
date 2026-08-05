import io
import datetime as dt
import threading
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
import requests
from signal_engine import TradingEngine
import nifty_sectors
import alert_log

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
    .buy-title { font-family: monospace; font-size: 13px; font-weight: bold; color: #1a9c4b; margin-bottom: 2px; }
    .sell-title { font-family: monospace; font-size: 13px; font-weight: bold; color: #e53935; margin-bottom: 2px; }
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


@st.cache_resource
def get_signal_history_lock():
    """Guards signal_history_store. It's shared across every session/tab hitting this app, and
    each one's 30s auto-refresh runs on its own thread - without a lock, one session iterating
    the dict (building the Buy/Sell boxes) while another mutates it (a new signal firing) can
    raise 'dictionary changed size during iteration', which is the likely cause of a box
    rendering its heading but no rows: the exception cut the render short mid-way."""
    return threading.Lock()


engine = get_engine()
signal_history_store = get_signal_history_store()
signal_history_lock = get_signal_history_lock()


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




with st.expander("📑 Alerts Report (MIS) - pull a period, validate what actually happened", expanded=False):
    report_df = alert_log.load_alert_log()
    if report_df.empty:
        st.info("No alerts logged yet. Every BUY/SELL trigger from the live dashboard below gets recorded here automatically going forward.")
    else:
        report_df["trigger_time"] = pd.to_datetime(report_df["trigger_time"])
        min_date, max_date = report_df["trigger_time"].min().date(), report_df["trigger_time"].max().date()

        f1, f2, f3 = st.columns([2, 1, 1])
        with f1:
            date_range = st.date_input("Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        with f2:
            direction_filter = st.selectbox("Direction", ["All", "BUY", "SELL"])
        with f3:
            status_filter = st.selectbox("Status", ["All", "OPEN", "TARGET1_HIT", "TARGET2_HIT", "STOPPED_OUT"])

        filtered = report_df.copy()
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_d, end_d = date_range
            filtered = filtered[(filtered["trigger_time"].dt.date >= start_d) & (filtered["trigger_time"].dt.date <= end_d)]
        if direction_filter != "All":
            filtered = filtered[filtered["direction"] == direction_filter]
        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]

        filtered["time_to_t1"] = pd.to_datetime(filtered["t1_hit_time"]) - filtered["trigger_time"]
        filtered["time_to_t2"] = pd.to_datetime(filtered["t2_hit_time"]) - filtered["trigger_time"]

        total = len(filtered)
        t1_n, t2_n, sl_n, open_n = filtered["t1_hit"].sum(), filtered["t2_hit"].sum(), filtered["sl_hit"].sum(), (filtered["status"] == "OPEN").sum()

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Alerts", total)
        m2.metric("Hit T1", f"{t1_n} ({100*t1_n/total:.0f}%)" if total else "0")
        m3.metric("Hit T2", f"{t2_n} ({100*t2_n/total:.0f}%)" if total else "0")
        m4.metric("Stopped Out", f"{sl_n} ({100*sl_n/total:.0f}%)" if total else "0")
        m5.metric("Still Open", open_n)

        display_cols = ["symbol", "direction", "trigger_time", "trigger_price", "sl", "t1", "t2",
                         "status", "t1_hit_time", "t2_hit_time", "time_to_t1", "time_to_t2"]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True, height=300)

        dl1, dl2 = st.columns(2)
        with dl1:
            csv_bytes = filtered[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv_bytes, file_name=f"alerts_report_{dt.date.today()}.csv",
                                mime="text/csv", use_container_width=True)
        with dl2:
            try:
                xlsx_buf = io.BytesIO()
                filtered[display_cols].to_excel(xlsx_buf, index=False, engine="openpyxl")
                st.download_button("⬇️ Download Excel", xlsx_buf.getvalue(), file_name=f"alerts_report_{dt.date.today()}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            except Exception as e:
                st.caption(f"Excel export unavailable: {e}")

        st.caption(
            "This table only updates when the page fully reloads (it's outside the 30s auto-refresh loop by design, "
            "so pulling a report doesn't interrupt the live scanner). Click 'Refresh Now' in the sidebar to pull "
            "in anything logged since you opened this."
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
    # Compute the current IST wall-clock time, then drop the tzinfo immediately. Every downstream
    # datetime we create or store is a naive "IST clock reading" from here on - this avoids
    # aware-vs-naive subtraction errors once these values round-trip through the CSV alert log
    # (open alerts store NaT for t1_hit_time/t2_hit_time, and a column that's part real-timestamp,
    # part NaT can come back from CSV as tz-naive even when the timestamps were tz-aware going in).
    now = dt.datetime.now(IST).replace(tzinfo=None)

    def _targets(price, atr, is_buy):
        sign = 1 if is_buy else -1
        return {
            "SL": round(price - sign * 1.5 * atr, 2),
            "T1": round(price + sign * 1.5 * atr, 2),
            "T2": round(price + sign * 3.0 * atr, 2),
        }

    alerts_df = alert_log.load_alert_log()

    compiled_rows = []
    with st.spinner("Computing live signals across the full F&O universe (first load only)..."):
        for _, stock in master_database.iterrows():
            symbol = stock["Symbol"]
            close_val = float(stock["Price"])
            sig = engine.fetcher.compute_indicator_signals(str(stock["ID"]), close_val)
            atr_val = sig["atr"] if sig.get("atr") else round(close_val * 0.02, 2)
            score = sig["score"]

            with signal_history_lock:
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

            # Alert logging (file I/O) deliberately happens OUTSIDE the lock - no need to
            # serialize disk writes across sessions just because they touch the same in-memory dict.
            if just_flipped and direction in ("BUY", "SELL"):
                tgt = _targets(close_val, atr_val, is_buy=(direction == "BUY"))
                alerts_df = alert_log.append_alert(
                    alerts_df, symbol, direction, now, close_val, tgt["SL"], tgt["T1"], tgt["T2"]
                )

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

    # Check every still-open alert against today's live prices, advance SL/T1/T2 status, persist.
    current_prices = dict(zip(df_all["Ticker"], df_all["_price"]))
    alerts_df = alert_log.update_open_alerts(alerts_df, current_prices, now)
    alert_log.save_alert_log(alerts_df)

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
    #
    # Snapshot the shared store under the lock, THEN release it before building/rendering rows -
    # keeps the lock held for microseconds instead of across an entire render, and means a box
    # can never be cut short mid-render by another session mutating the dict underneath it.
    # ==============================================================================
    with signal_history_lock:
        buy_snapshot = {s: dict(v) for s, v in signal_history_store.items() if v["direction"] == "BUY"}
        sell_snapshot = {s: dict(v) for s, v in signal_history_store.items() if v["direction"] == "SELL"}

    with right_panel:
        with st.container(border=True):
            st.markdown("<div class='buy-title'>🟢 TOP 5 BUY SIGNALS</div>", unsafe_allow_html=True)
            try:
                buy_symbols = sorted(buy_snapshot.keys(), key=lambda s: buy_snapshot[s]["since"], reverse=True)
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
                        "Signal Since": buy_snapshot[sym]["since"].strftime("%d-%b %H:%M"),
                    })
                if buy_rows:
                    st.dataframe(pd.DataFrame(buy_rows), use_container_width=True, hide_index=True, height=215)
                else:
                    st.info("No stocks currently qualify as a BUY signal.")
            except Exception as e:
                st.error(f"Buy box failed to render this cycle: {e}")

        with st.container(border=True):
            st.markdown("<div class='sell-title'>🔴 TOP 5 SELL SIGNALS</div>", unsafe_allow_html=True)
            try:
                sell_symbols = sorted(sell_snapshot.keys(), key=lambda s: sell_snapshot[s]["since"], reverse=True)
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
                        "Signal Since": sell_snapshot[sym]["since"].strftime("%d-%b %H:%M"),
                    })
                if sell_rows:
                    st.dataframe(pd.DataFrame(sell_rows), use_container_width=True, hide_index=True, height=215)
                else:
                    st.info("No stocks currently qualify as a SELL signal.")
            except Exception as e:
                st.error(f"Sell box failed to render this cycle: {e}")

        st.caption(
            "Sorted by most recently triggered first. 'Signal Since' resets after each app reboot - "
            "there's no memory of signals from before the app started watching this session."
        )


live_dashboard(static_universe)
