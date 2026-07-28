import requests
import pandas as pd
import config

class DhanDataFetcher:
    def __init__(self):
        self.headers = {
            "client-id": config.DHAN_CLIENT_ID,
            "access-token": config.DHAN_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

    def fetch_delivery_data(self, security_id: str) -> float:
        url = f"{config.DHAN_BASE_URL}/marketfeed/delivery/{security_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return float(response.json().get("data", {}).get("deliveryPercentage", 0))
            return 0.0
        except Exception:
            return 0.0

class TradingEngine:
    def __init__(self):
        self.fetcher = DhanDataFetcher()

    def run_scoring_engine(self, raw_metrics: dict) -> dict:
        score = 0
        breakdown = {}

        trend = raw_metrics.get("close", 0) > raw_metrics.get("ema_20", 0)
        score += 1 if trend else 0
        breakdown["Trend (>20EMA)"] = "PASS" if trend else "FAIL"

        momentum = raw_metrics.get("rsi", 0) > 50
        score += 1 if momentum else 0
        breakdown["Momentum (RSI>50)"] = "PASS" if momentum else "FAIL"

        vol_spike = raw_metrics.get("volume", 0) > (raw_metrics.get("avg_volume", 1) * 1.5)
        score += 1 if vol_spike else 0
        breakdown["Volume Spike (>1.5x)"] = "PASS" if vol_spike else "FAIL"

        del_strength = raw_metrics.get("delivery_pct", 0) >= config.MIN_DELIVERY_PCT
        score += 1 if del_strength else 0
        breakdown["Delivery Strength"] = f"{raw_metrics.get('delivery_pct', 0)}%" if del_strength else "FAIL"

        pa_breakout = raw_metrics.get("close", 0) > raw_metrics.get("prev_high", 0)
        score += 1 if pa_breakout else 0
        breakdown["Price Breakout"] = "PASS" if pa_breakout else "FAIL"

        return {"total_score": score, "breakdown": breakdown}

    def route_asset(self, symbol: str, security_id: str, is_fno_eligible: bool, raw_metrics: dict) -> dict:
        delivery_pct = self.fetcher.fetch_delivery_data(security_id)
        raw_metrics["delivery_pct"] = delivery_pct
        
        scoring_results = self.run_scoring_engine(raw_metrics)
        score = scoring_results["total_score"]

        if score >= 4:
            if is_fno_eligible and raw_metrics.get("iv_rank", 100) <= config.MAX_IV_RANK_FOR_BUYING:
                route = "F&O (Options Buy / Futures Long)"
            elif is_fno_eligible and raw_metrics.get("iv_rank", 100) > config.MAX_IV_RANK_FOR_BUYING:
                route = "F&O (Futures Long Only - High IV)"
            elif delivery_pct >= config.MIN_DELIVERY_PCT:
                route = "MTF (Margin Trading Facility)"
            else:
                route = "Cash Equity (No Leverage)"
        elif score == 3:
            route = "MTF (Conservative Capital Allocation)"
        else:
            route = "NO TRADE (Score too low)"

        return {"symbol": symbol, "score": score, "route": route, "breakdown": scoring_results["breakdown"]}
