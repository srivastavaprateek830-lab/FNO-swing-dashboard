"""
Persistent alert log: records every BUY/SELL trigger with its SL/T1/T2, then tracks whether
and when price actually reached those levels. This is what makes the dashboard's signals
auditable - "did TCS's Sell alert from 3-Aug 12PM actually work?" becomes a lookup, not a guess.

STORAGE CAVEAT: this writes to a local CSV file on the app's filesystem. On Streamlit Cloud
that filesystem is EPHEMERAL - it survives ordinary refreshes and reboots-without-redeploy, but
a full redeploy (new code push + reboot) wipes it. Download a backup via the Reports section
before redeploying if you want to keep history. For guaranteed persistence across redeploys,
this would need to write to an external store (Google Sheets, a hosted DB) instead of local CSV.
"""
import os
import pandas as pd

ALERT_LOG_PATH = "alerts_log.csv"

COLUMNS = [
    "symbol", "direction", "trigger_time", "trigger_price", "sl", "t1", "t2",
    "t1_hit", "t1_hit_time", "t2_hit", "t2_hit_time",
    "sl_hit", "sl_hit_time", "status", "last_checked_time",
]

DATE_COLS = ["trigger_time", "t1_hit_time", "t2_hit_time", "sl_hit_time", "last_checked_time"]


def load_alert_log() -> pd.DataFrame:
    if os.path.exists(ALERT_LOG_PATH):
        try:
            df = pd.read_csv(ALERT_LOG_PATH)
            for c in DATE_COLS:
                if c in df.columns:
                    df[c] = pd.to_datetime(df[c], errors="coerce")
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)


def save_alert_log(df: pd.DataFrame) -> None:
    df.to_csv(ALERT_LOG_PATH, index=False)


def append_alert(df: pd.DataFrame, symbol: str, direction: str, trigger_time, trigger_price: float,
                  sl: float, t1: float, t2: float) -> pd.DataFrame:
    new_row = {
        "symbol": symbol, "direction": direction, "trigger_time": trigger_time,
        "trigger_price": trigger_price, "sl": sl, "t1": t1, "t2": t2,
        "t1_hit": False, "t1_hit_time": pd.NaT, "t2_hit": False, "t2_hit_time": pd.NaT,
        "sl_hit": False, "sl_hit_time": pd.NaT, "status": "OPEN", "last_checked_time": trigger_time,
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)


def update_open_alerts(df: pd.DataFrame, current_prices: dict, now) -> pd.DataFrame:
    """Checks every still-active alert (OPEN or already past T1) against the current live price
    and advances its status if SL/T1/T2 has been crossed. SL is only checked before T1 is hit -
    once T1 is reached, the trade is assumed derisked (e.g. SL moved to breakeven), so only
    forward progress toward T2 is tracked from there."""
    if df.empty:
        return df
    active_mask = df["status"].isin(["OPEN", "TARGET1_HIT"])
    for idx in df[active_mask].index:
        row = df.loc[idx]
        price = current_prices.get(row["symbol"])
        if price is None:
            continue
        is_buy = row["direction"] == "BUY"

        if not row["t1_hit"]:
            sl_breached = (price <= row["sl"]) if is_buy else (price >= row["sl"])
            if sl_breached:
                df.at[idx, "sl_hit"] = True
                df.at[idx, "sl_hit_time"] = now
                df.at[idx, "status"] = "STOPPED_OUT"
                df.at[idx, "last_checked_time"] = now
                continue

        t1_breached = (price >= row["t1"]) if is_buy else (price <= row["t1"])
        if not row["t1_hit"] and t1_breached:
            df.at[idx, "t1_hit"] = True
            df.at[idx, "t1_hit_time"] = now
            df.at[idx, "status"] = "TARGET1_HIT"

        t2_breached = (price >= row["t2"]) if is_buy else (price <= row["t2"])
        if not row["t2_hit"] and t2_breached:
            df.at[idx, "t2_hit"] = True
            df.at[idx, "t2_hit_time"] = now
            df.at[idx, "status"] = "TARGET2_HIT"

        df.at[idx, "last_checked_time"] = now
    return df
