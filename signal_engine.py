import pandas as pd
import time
import config

class DhanDataFetcher:
    """SIMULATED FEETCHER: Mimics Dhan API responses without making web calls."""
    def __init__(self):
        # We don't need real credentials for testing
        self.headers = {}

    def fetch_delivery_data(self, security_id: str) -> float:
        """Simulates varying delivery percentages based on stock IDs for testing."""
        # Returns high delivery for Reliance, low for TCS, high for Zomato
        mock_delivery_vault = {
            "2885": 48.5,   # RELIANCE -> Passes (>40%)
            "11536": 22.0,  # TCS -> Fails (<40%)
            "5097": 65.0    # ZOMATO -> Passes (>40%)
        }
        return mock_delivery_vault.get(security_id, 35.0)

    def fetch_option_chain(self, underlying_symbol: str) -> list:
        """Simulates a dummy option chain contract structure."""
        # Creates a mock array simulating an At-The-Money Call option contract
        return [
            {
                "strikePrice": 2460.0 if underlying_symbol == "RELIANCE" else 3800.0,
                "expiryDate": "27-Aug-2026",
                "daysToExpiry": 14,
                "delta": 0.52,
                "theta": -1.2400,
                "lastPrice": 42.50,
                "optionType": "CE"
            }
        ]


class TradingEngine:
    """Runs the 5-point scoring framework and asset routing using simulated feeds."""
    def __init__(self):
        self.fetcher = DhanDataFetcher()

    def run_scoring_engine(self, raw_metrics: dict) -> dict:
        """Calculates the 5-Point Swing Score matrix."""
        score = 0
        breakdown = {}

        # 1. Trend Alignment
        trend = raw_metrics.get("close", 0) > raw_metrics.get("ema_20", 0)
        score += 1 if trend else 0
        breakdown["Trend (>20EMA)"] = "PASS" if trend else "FAIL"

        # 2. Momentum
        momentum = raw_metrics.get("rsi", 0) > 50
        score += 1 if momentum else 0
        breakdown["Momentum (RSI>50)"] = "PASS" if momentum else "FAIL"

        # 3. Volume Spike
        vol_spike = raw_metrics.get("volume", 0) > (raw_metrics.get("avg_volume", 1) * 1.5)
        score += 1 if vol_spike else 0
        breakdown["Volume Spike (>1.5x)"] = "PASS" if vol_spike else "FAIL"

        # 4. Delivery Strength
        del_strength = raw_metrics.get("delivery_pct", 0) >= config.MIN_DELIVERY_PCT
        score += 1 if del_strength else 0
        breakdown["Delivery Strength"] = f"{raw_metrics.get('delivery_pct', 0)}%" if del_strength else f"{raw_metrics.get('delivery_pct', 0)}% (FAIL)"

        # 5. Price Action
        pa_breakout = raw_metrics.get("close", 0) > raw_metrics.get("prev_high", 0)
        score += 1 if pa_breakout else 0
        breakdown["Price Breakout"] = "PASS" if pa_breakout else "FAIL"

        return {"total_score": score, "breakdown": breakdown}

    def route_asset(self, symbol: str, security_id: str, is_fno_eligible: bool, raw_metrics: dict) -> dict:
        """Applies auto-routing logic based on simulated metrics."""
        # Fetch the simulated delivery percentage
        delivery_pct = self.fetcher.fetch_delivery_data(security_id)
        raw_metrics["delivery_pct"] = delivery_pct
        
        scoring_results = self.run_scoring_engine(raw_metrics)
        score = scoring_results["total_score"]

        # Routing Logic Rules Matrix
        if score >= 4:
            if is_fno_eligible and raw_metrics.get("iv_rank", 100) <= config.MAX_IV_RANK_FOR_BUYING:
                route = "⚡ F&O (Options Buy / Futures Long)"
            elif is_fno_eligible and raw_metrics.get("iv_rank", 100) > config.MAX_IV_RANK_FOR_BUYING:
                route = "📈 F&O (Futures Long Only - High IV)"
            elif delivery_pct >= config.MIN_DELIVERY_PCT:
                route = "💰 MTF (Margin Trading Facility - 4x Leverage Equity)"
            else:
                route = "💵 Cash Equity (No Leverage - Weak Delivery)"
        elif score == 3:
            route = "🛡️ MTF (Conservative Capital Allocation)"
        else:
            route = "❌ NO TRADE (Score below entry threshold)"

        return {
            "symbol": symbol,
            "score": score,
            "route": route,
            "breakdown": scoring_results["breakdown"]
        }

    def optimize_strike(self, underlying_symbol: str, target_delta: float = 0.5) -> dict:
        """Simulates scanning option chains for the best strike target."""
        chain = self.fetcher.fetch_option_chain(underlying_symbol)
        optimal_contract = chain[0]

        return {
            "status": "Success",
            "strike": optimal_contract['strikePrice'],
            "expiry": optimal_contract['expiryDate'],
            "delta": optimal_contract['delta'],
            "theta": optimal_contract['theta'],
            "premium": optimal_contract['lastPrice'],
            "type": optimal_contract['optionType']
        }
