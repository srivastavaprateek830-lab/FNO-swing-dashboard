import requests
import time
import datetime as dt
import config


class DhanDataFetcher:
    """PRODUCTION DATA PIPELINE: Streams real-time exchange ticks via secure broker routes."""

    def __init__(self):
        self.headers = {
            "client-id": str(config.DHAN_CLIENT_ID),
            "access-token": str(config.DHAN_ACCESS_TOKEN),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # Last error message, surfaced in the UI so failures are visible instead of silent
        self.last_error = None
        self._expiry_cache = {}   # {security_id: (expiry_list, fetched_at)}
        self._chain_cache = {}    # {(security_id, expiry): (chain_rows, fetched_at)}
        self._hist_cache = {}     # {security_id: (historical_data_dict, fetched_at)}

        # --- Quote throttling / stale-fallback state ---
        # Dhan caps /v2/marketfeed/ohlc at roughly 1 request/second. Multiple browser tabs or a
        # too-fast auto-refresh can blow past that and get you a 429 (or a temporary block if it
        # keeps happening). We enforce a minimum gap client-side, and on any failure we serve the
        # last known-good quotes instead of wiping the table to zero.
        self._MIN_QUOTE_INTERVAL = 1.5   # seconds between actual calls to the OHLC endpoint
        self._last_quote_call_time = 0.0
        self._quote_cache = {}           # {security_id: {"price":.., "prev_close":.., "pct_chg":..}}
        self.quotes_stale = False        # True when the UI is showing cached, not fresh, quotes

    def fetch_quotes_bulk(self, security_ids: list, exchange_segment: str = "NSE_EQ") -> dict:
        """Queries Dhan's Market Quote OHLC endpoint in bulk - gives last traded price AND the
        previous close in the SAME call, so we can show live price + %chg-for-the-day from a
        single request instead of two. Dhan expects security IDs grouped BY SEGMENT, e.g.
        {"NSE_EQ": [11536, 3045]}, and caps at 1000 IDs per request, so we chunk."""
        if not security_ids:
            return {}

        ids_str = [str(sid) for sid in security_ids]

        # Client-side throttle: if we called this too recently, don't risk another 429 -
        # just serve whatever we last successfully fetched.
        now = time.monotonic()
        if now - self._last_quote_call_time < self._MIN_QUOTE_INTERVAL:
            self.quotes_stale = True
            return {sid: self._quote_cache[sid] for sid in ids_str if sid in self._quote_cache}

        url = f"{config.DHAN_BASE_URL}/v2/marketfeed/ohlc"
        result = {}
        had_failure = False
        try:
            for i in range(0, len(security_ids), 1000):
                batch = [int(sid) for sid in security_ids[i:i + 1000]]
                payload = {exchange_segment: batch}
                res = requests.post(url, json=payload, headers=self.headers, timeout=8)
                self._last_quote_call_time = time.monotonic()

                if res.status_code == 200:
                    seg_data = res.json().get("data", {}).get(exchange_segment, {})
                    for sec_id, quote in seg_data.items():
                        price = float(quote.get("last_price", 0.0))
                        prev_close = float(quote.get("ohlc", {}).get("close", 0.0) or 0.0)
                        pct_chg = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
                        entry = {"price": price, "prev_close": prev_close, "pct_chg": round(pct_chg, 2)}
                        result[str(sec_id)] = entry
                        self._quote_cache[str(sec_id)] = entry
                elif res.status_code == 429:
                    self.last_error = (
                        f"Rate limited (429) by Dhan's OHLC endpoint - {res.text[:200]}. "
                        "Close any duplicate browser tabs/sessions running this app."
                    )
                    had_failure = True
                else:
                    self.last_error = f"Quote fetch failed: HTTP {res.status_code} - {res.text[:200]}"
                    had_failure = True
        except Exception as e:
            self.last_error = f"Quote fetch exception: {e}"
            had_failure = True

        if had_failure:
            self.quotes_stale = True
            # Backfill anything missing this cycle from the last known good quote, so a
            # transient rate-limit doesn't zero out the whole table.
            for sid in ids_str:
                if sid not in result and sid in self._quote_cache:
                    result[sid] = self._quote_cache[sid]
        else:
            self.quotes_stale = False

        return result

    def fetch_historical_daily(self, security_id: str, exchange_segment: str = "NSE_EQ",
                                instrument: str = "EQUITY", lookback_days: int = 400):
        """Fetches daily OHLCV candles for indicator math AND the daily chart widget. Cached for
        6 hours per symbol since the daily candle only changes once the market closes. Default
        lookback covers a full year (for the chart's '1Y' view) plus buffer for indicator math -
        fetched once, reused for both, so switching chart timeframes doesn't trigger new API calls."""
        cached = self._hist_cache.get(security_id)
        if cached and (time.time() - cached[1] < 6 * 3600):
            return cached[0]
        try:
            to_date = dt.date.today()
            from_date = to_date - dt.timedelta(days=lookback_days)
            url = f"{config.DHAN_BASE_URL}/v2/charts/historical"
            payload = {
                "securityId": str(security_id),
                "exchangeSegment": exchange_segment,
                "instrument": instrument,
                "expiryCode": 0,
                "oi": False,
                "fromDate": from_date.isoformat(),
                "toDate": to_date.isoformat(),
            }
            res = requests.post(url, json=payload, headers=self.headers, timeout=10)
            if res.status_code != 200:
                self.last_error = f"Historical data fetch failed: HTTP {res.status_code} - {res.text[:200]}"
                return None
            data = res.json()
            if not data.get("close"):
                return None
            self._hist_cache[security_id] = (data, time.time())
            time.sleep(0.25)  # be gentle when looping this across many symbols in one sector
            return data
        except Exception as e:
            self.last_error = f"Historical data exception: {e}"
            return None

    @staticmethod
    def _compute_atr(highs, lows, closes, period=14) -> float:
        """Real Wilder's ATR from actual daily true-range history. Returns the latest value.
        This replaces the old placeholder of 'current_price * 0.02', which gave every stock
        the exact same 2% band regardless of how volatile it actually is."""
        n = len(closes)
        if n < period + 2:
            return 0.0
        trs = [0.0] * n
        for i in range(1, n):
            trs[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        atr = sum(trs[1:period + 1]) / period
        for i in range(period + 1, n):
            atr = (atr * (period - 1) + trs[i]) / period
        return atr

    @staticmethod
    def _supertrend_is_bullish(highs, lows, closes, period=10, multiplier=3.0) -> bool:
        """Standard Supertrend (ATR-band with flip logic). Returns True if the most recent
        close is in an uptrend (price above the Supertrend line)."""
        n = len(closes)
        if n < period + 2:
            return True  # not enough data to judge - default neutral/bullish rather than block the UI

        trs = [0.0] * n
        for i in range(1, n):
            trs[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))

        atr = [0.0] * n
        atr[period] = sum(trs[1:period + 1]) / period
        for i in range(period + 1, n):
            atr[i] = (atr[i - 1] * (period - 1) + trs[i]) / period

        hl2 = [(highs[i] + lows[i]) / 2 for i in range(n)]
        upper = [hl2[i] + multiplier * atr[i] for i in range(n)]
        lower = [hl2[i] - multiplier * atr[i] for i in range(n)]
        final_upper, final_lower = upper[:], lower[:]
        trend_up = True

        for i in range(period + 1, n):
            final_upper[i] = upper[i] if (upper[i] < final_upper[i - 1] or closes[i - 1] > final_upper[i - 1]) else final_upper[i - 1]
            final_lower[i] = lower[i] if (lower[i] > final_lower[i - 1] or closes[i - 1] < final_lower[i - 1]) else final_lower[i - 1]
            if closes[i] > final_upper[i - 1]:
                trend_up = True
            elif closes[i] < final_lower[i - 1]:
                trend_up = False

        return trend_up

    @staticmethod
    def _score_at_index(closes, highs, lows, volumes, i):
        """Computes Trend/Momentum/Volume/Breakout/Supertrend/RSI using ONLY data up to and
        including index i - no lookahead. This is the single source of truth for signal logic,
        used both for today's live score AND for walk-forward backtesting, so the backtest is
        actually testing the exact same rules the dashboard uses, not an approximation of them."""
        if i < 20:
            return None
        window_closes = closes[:i + 1]
        window_highs = highs[:i + 1]
        window_lows = lows[:i + 1]
        window_vol = volumes[:i + 1] if volumes else []

        deltas = [window_closes[j] - window_closes[j - 1] for j in range(1, len(window_closes))]
        period = 14
        if len(deltas) < period:
            return None
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        rsi = 100.0 if avg_loss == 0 else 100 - (100 / (1 + (avg_gain / avg_loss)))

        sma20 = sum(window_closes[-20:]) / 20
        trend_pass = window_closes[-1] > sma20

        roc = ((window_closes[-1] - window_closes[-6]) / window_closes[-6]) * 100 if len(window_closes) > 6 else 0.0
        momentum_pass = roc > 0

        if window_vol and len(window_vol) >= 5:
            avg_vol = sum(window_vol[-20:]) / min(20, len(window_vol))
            volume_pass = window_vol[-1] > avg_vol
        else:
            volume_pass = None

        prior_window = window_highs[-21:-1] if len(window_highs) > 21 else window_highs[:-1]
        prior_high = max(prior_window) if prior_window else window_closes[-1]
        breakout_pass = window_closes[-1] > prior_high

        supertrend_pass = DhanDataFetcher._supertrend_is_bullish(window_highs, window_lows, window_closes)

        signals = [trend_pass, momentum_pass, breakout_pass, supertrend_pass]
        if volume_pass is not None:
            signals.append(volume_pass)
        score = round(100 * sum(1 for s in signals if s) / len(signals))

        return {
            "rsi": round(rsi, 1), "trend": trend_pass, "momentum": momentum_pass,
            "volume": volume_pass, "breakout": breakout_pass, "supertrend": supertrend_pass, "score": score,
        }

    def compute_indicator_signals(self, security_id: str, live_price: float) -> dict:
        """Today's live signal read: fetches cached historical candles, appends the live price
        as 'today', and scores it using the exact same logic the backtest validates.

        NOTE: 'Del Strength' (NSE delivery %) is NOT available from Dhan's market data APIs -
        it needs NSE's separate bhavcopy/delivery-position files, so it stays labeled N/A rather
        than being faked as a pass/fail."""
        default = {"rsi": None, "trend": "N/A", "momentum": "N/A", "volume": "N/A",
                   "breakout": "N/A", "supertrend": "N/A", "score": 50, "atr": None}

        hist = self.fetch_historical_daily(security_id)
        if not hist or not hist.get("close"):
            return default

        closes = list(hist["close"]) + [live_price]
        highs = list(hist["high"]) + [live_price]
        lows = list(hist["low"]) + [live_price]
        volumes = list(hist.get("volume", []))

        if len(closes) < 16:
            return default

        atr_val = self._compute_atr(highs, lows, closes)
        sig = self._score_at_index(closes, highs, lows, volumes, len(closes) - 1)
        if sig is None:
            return default

        return {
            "rsi": sig["rsi"],
            "trend": "PASS" if sig["trend"] else "FAIL",
            "momentum": "PASS" if sig["momentum"] else "FAIL",
            "volume": ("PASS" if sig["volume"] else "FAIL") if sig["volume"] is not None else "N/A",
            "breakout": "YES" if sig["breakout"] else "NO",
            "supertrend": "PASS" if sig["supertrend"] else "FAIL",
            "score": sig["score"],
            "atr": round(atr_val, 2),
        }

    def backtest_signal_scores(self, hist: dict, lookahead_days: int = 5) -> list:
        """Walk-forward backtest: for every historical day (with enough warmup data), computes
        what THIS dashboard's score would have been using only data available as of that day,
        then checks the actual forward return over the next `lookahead_days` trading days.
        Returns a list of (score, forward_return_pct) tuples - the raw material for computing
        a real, verifiable hit-rate per score band."""
        if not hist or not hist.get("close"):
            return []
        closes, highs, lows = list(hist["close"]), list(hist["high"]), list(hist["low"])
        volumes = list(hist.get("volume", []))
        n = len(closes)
        results = []
        for i in range(20, n - lookahead_days):
            sig = self._score_at_index(closes, highs, lows, volumes, i)
            if sig is None or closes[i] == 0:
                continue
            fwd_return = (closes[i + lookahead_days] - closes[i]) / closes[i] * 100
            results.append((sig["score"], fwd_return))
        return results

    def _get_nearest_expiry(self, security_id: str, underlying_seg: str):
        """Option chain requires an explicit expiry date, fetched from a separate endpoint.
        Cached for an hour since expiries don't change intraday."""
        cached = self._expiry_cache.get(security_id)
        if cached and (time.time() - cached[1] < 3600):
            return cached[0][0] if cached[0] else None
        try:
            url = f"{config.DHAN_BASE_URL}/v2/optionchain/expirylist"
            payload = {"UnderlyingScrip": int(security_id), "UnderlyingSeg": underlying_seg}
            res = requests.post(url, json=payload, headers=self.headers, timeout=8)
            if res.status_code == 200:
                expiries = res.json().get("data", [])
                self._expiry_cache[security_id] = (expiries, time.time())
                return expiries[0] if expiries else None
            self.last_error = f"Expiry list fetch failed: HTTP {res.status_code} - {res.text[:200]}"
            return None
        except Exception as e:
            self.last_error = f"Expiry list exception: {e}"
            return None

    def fetch_option_chain(self, underlying_symbol_id: str, underlying_seg: str = "NSE_FNO") -> list:
        """Queries Dhan's Option Chain API. Dhan rate-limits this to 1 request / 3 seconds,
        so results are cached for 10s to survive the dashboard's auto-refresh loop."""
        expiry = self._get_nearest_expiry(underlying_symbol_id, underlying_seg)
        if not expiry:
            return []

        cache_key = (underlying_symbol_id, expiry)
        cached = self._chain_cache.get(cache_key)
        if cached and (time.time() - cached[1] < 10):
            return cached[0]

        try:
            url = f"{config.DHAN_BASE_URL}/v2/optionchain"
            payload = {
                "UnderlyingScrip": int(underlying_symbol_id),
                "UnderlyingSeg": underlying_seg,
                "Expiry": expiry,
            }
            res = requests.post(url, json=payload, headers=self.headers, timeout=8)
            if res.status_code != 200:
                self.last_error = f"Option chain fetch failed: HTTP {res.status_code} - {res.text[:200]}"
                return []

            oc_map = res.json().get("data", {}).get("oc", {})
            rows = []
            for strike_str, legs in oc_map.items():
                for opt_type in ("ce", "pe"):
                    leg = legs.get(opt_type)
                    if leg:
                        rows.append({
                            "strikePrice": float(strike_str),
                            "type": opt_type.upper(),
                            "lastPrice": leg.get("last_price", 0.0),
                            "securityId": leg.get("security_id"),
                            "oi": leg.get("oi", 0),
                            "expiryDate": expiry,
                        })
            self._chain_cache[cache_key] = (rows, time.time())
            return rows
        except Exception as e:
            self.last_error = f"Option chain exception: {e}"
            return []

    def place_live_order(self, payload: dict) -> dict:
        """Routes order instructions to Dhan's live order-execution endpoint."""
        url = f"{config.DHAN_BASE_URL}/v2/orders"
        try:
            res = requests.post(url, json=payload, headers=self.headers, timeout=8)
            return res.json()
        except Exception as e:
            self.last_error = f"Order placement exception: {e}"
            return {"status": "failure", "remarks": str(e)}

    def get_call_put_oi_bias(self, underlying_symbol_id: str) -> dict:
        """Real Call vs Put Open Interest split from the option chain we already fetch.
        NOTE: this is OI-based sentiment, not literal bid/ask order-book depth - true Level-2
        market depth on Dhan requires a separate websocket feed (20-level depth), not a simple
        REST call, so this is intentionally labeled as OI bias rather than 'market depth'."""
        raw_chain = self.fetch_option_chain(underlying_symbol_id)
        if not raw_chain:
            return {"call_pct": None, "put_pct": None}
        call_oi = sum(r["oi"] for r in raw_chain if r["type"] == "CE")
        put_oi = sum(r["oi"] for r in raw_chain if r["type"] == "PE")
        total = call_oi + put_oi
        if total <= 0:
            return {"call_pct": None, "put_pct": None}
        call_pct = round(100 * call_oi / total, 1)
        return {"call_pct": call_pct, "put_pct": round(100 - call_pct, 1)}


class TradingEngine:
    """PRODUCTION LOGIC ENGINE: Computes target metrics directly from live data strings."""

    def __init__(self):
        self.fetcher = DhanDataFetcher()

    def optimize_strike_with_targets(self, underlying_symbol_id: str, current_price: float, atr: float) -> dict:
        raw_chain = self.fetcher.fetch_option_chain(underlying_symbol_id)

        spot_sl = round(current_price - (1.5 * atr), 2)
        spot_tp = round(current_price + (3.0 * atr), 2)

        # Premium SL/TP used to be a flat x0.5 / x2.0 of the premium for EVERY stock, regardless
        # of the underlying's actual volatility - which is exactly why it always looked like a
        # suspicious flat "double the premium" pattern. Real option Greeks (delta) aren't available
        # without a live per-strike Greeks feed, so this uses a standard rough approximation instead:
        # a near-the-money option's premium moves at roughly half the underlying's price move
        # (delta ~ 0.5). That ties the premium target to THIS stock's real ATR-based spot move,
        # so it varies stock-to-stock instead of being a fixed multiplier.
        ASSUMED_ATM_DELTA = 0.5

        def _premium_targets(premium: float) -> tuple:
            tp = round(premium + ASSUMED_ATM_DELTA * (spot_tp - current_price), 2)
            sl = round(max(premium - ASSUMED_ATM_DELTA * (current_price - spot_sl), 0.05), 2)
            return sl, tp

        if not raw_chain:
            # Option chain unavailable (market closed, rate-limited, or no F&O contract) - use a
            # clearly-labeled estimate so it's never mistaken for a live quote.
            mock_strike = round(current_price / 100) * 100
            mock_premium = round(current_price * 0.015, 2)
            premium_sl, premium_tp = _premium_targets(mock_premium)
            return {
                "strike": mock_strike, "expiry": "N/A (est.)", "current_premium": mock_premium, "type": "CE",
                "spot_sl": spot_sl, "spot_tp": spot_tp,
                "premium_sl": premium_sl, "premium_tp": premium_tp,
            }

        # Pick the Call strike nearest to the current spot price (closest to at-the-money)
        ce_rows = [r for r in raw_chain if r["type"] == "CE"] or raw_chain
        optimal_row = min(ce_rows, key=lambda r: abs(r["strikePrice"] - current_price))
        current_premium = float(optimal_row.get("lastPrice") or (current_price * 0.015))
        premium_sl, premium_tp = _premium_targets(current_premium)

        return {
            "strike": optimal_row["strikePrice"],
            "expiry": optimal_row.get("expiryDate", "N/A"),
            "current_premium": current_premium, "type": "CE",
            "spot_sl": spot_sl, "spot_tp": spot_tp,
            "premium_sl": premium_sl, "premium_tp": premium_tp,
        }

    def generate_dhan_order_payload(self, security_id: str, symbol: str, transaction_type: str,
                                     product_type: str, quantity: int = 1) -> dict:
        return {
            "dhanClientId": config.DHAN_CLIENT_ID,
            "correlationId": f"terminal_{symbol.lower()}",
            "transactionType": transaction_type.upper(),
            "exchangeSegment": "NSE_EQ" if product_type == "MTF" else "NSE_FNO",
            "productType": "MARGIN",
            "orderType": "MARKET",
            "validity": "DAY",
            "securityId": str(security_id),
            "quantity": int(quantity),
        }
