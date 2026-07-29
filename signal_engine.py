import requests
import time
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

        # --- LTP throttling / stale-fallback state ---
        # Dhan caps /v2/marketfeed/ltp at roughly 1 request/second. Multiple browser tabs or a
        # too-fast auto-refresh can blow past that and get you a 429 (or a temporary block if it
        # keeps happening). We enforce a minimum gap client-side, and on any failure we serve the
        # last known-good prices instead of wiping the table to zero.
        self._MIN_QUOTE_INTERVAL = 1.5   # seconds between actual calls to the LTP endpoint
        self._last_quote_call_time = 0.0
        self._quote_cache = {}           # {security_id: last_known_price}
        self.quotes_stale = False        # True when the UI is showing cached, not fresh, prices

    def fetch_live_quotes_bulk(self, security_ids: list, exchange_segment: str = "NSE_EQ") -> dict:
        """Queries Dhan's Market Quote LTP endpoint in bulk.
        Dhan expects security IDs grouped BY SEGMENT, e.g. {"NSE_EQ": [11536, 3045]},
        and returns them nested the same way. Also caps at 1000 IDs per request, so we chunk."""
        if not security_ids:
            return {}

        ids_str = [str(sid) for sid in security_ids]

        # Client-side throttle: if we called this too recently, don't risk another 429 -
        # just serve whatever we last successfully fetched.
        now = time.monotonic()
        if now - self._last_quote_call_time < self._MIN_QUOTE_INTERVAL:
            self.quotes_stale = True
            return {sid: self._quote_cache[sid] for sid in ids_str if sid in self._quote_cache}

        url = f"{config.DHAN_BASE_URL}/v2/marketfeed/ltp"
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
                        result[str(sec_id)] = price
                        self._quote_cache[str(sec_id)] = price
                elif res.status_code == 429:
                    self.last_error = (
                        f"Rate limited (429) by Dhan's LTP endpoint - {res.text[:200]}. "
                        "Close any duplicate browser tabs/sessions running this app."
                    )
                    had_failure = True
                else:
                    self.last_error = f"LTP fetch failed: HTTP {res.status_code} - {res.text[:200]}"
                    had_failure = True
        except Exception as e:
            self.last_error = f"LTP fetch exception: {e}"
            had_failure = True

        if had_failure:
            self.quotes_stale = True
            # Backfill anything missing this cycle from the last known good price, so a
            # transient rate-limit doesn't zero out the whole table.
            for sid in ids_str:
                if sid not in result and sid in self._quote_cache:
                    result[sid] = self._quote_cache[sid]
        else:
            self.quotes_stale = False

        return result

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
        so results are cached for 10s to survive the dashboard's 5-second auto-refresh loop."""
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


class TradingEngine:
    """PRODUCTION LOGIC ENGINE: Computes target metrics directly from live data strings."""

    def __init__(self):
        self.fetcher = DhanDataFetcher()

    def optimize_strike_with_targets(self, underlying_symbol_id: str, current_price: float, atr: float) -> dict:
        raw_chain = self.fetcher.fetch_option_chain(underlying_symbol_id)

        if not raw_chain:
            # Option chain unavailable (market closed, rate-limited, or no F&O contract) - use a
            # clearly-labeled estimate so it's never mistaken for a live quote.
            mock_strike = round(current_price / 100) * 100
            mock_premium = round(current_price * 0.015, 2)
            return {
                "strike": mock_strike, "expiry": "N/A (est.)", "current_premium": mock_premium, "type": "CE",
                "spot_sl": round(current_price - (1.5 * atr), 2), "spot_tp": round(current_price + (3.0 * atr), 2),
                "premium_sl": round(mock_premium * 0.50, 2), "premium_tp": round(mock_premium * 2.0, 2),
            }

        # Pick the Call strike nearest to the current spot price (closest to at-the-money)
        ce_rows = [r for r in raw_chain if r["type"] == "CE"] or raw_chain
        optimal_row = min(ce_rows, key=lambda r: abs(r["strikePrice"] - current_price))
        current_premium = float(optimal_row.get("lastPrice") or (current_price * 0.015))

        return {
            "strike": optimal_row["strikePrice"],
            "expiry": optimal_row.get("expiryDate", "N/A"),
            "current_premium": current_premium, "type": "CE",
            "spot_sl": round(current_price - (1.5 * atr), 2), "spot_tp": round(current_price + (3.0 * atr), 2),
            "premium_sl": round(current_premium * 0.50, 2), "premium_tp": round(current_premium * 2.0, 2),
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
