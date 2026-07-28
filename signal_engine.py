import requests
import pandas as pd
import numpy as np
import config

class DhanDataFetcher:
    """LIVE API LAYER: Communicates with DhanHQ endpoints to aggregate market telemetry."""
    def __init__(self):
        self.headers = {
            "client-id": config.DHAN_CLIENT_ID,
            "access-token": config.DHAN_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

    def fetch_delivery_data(self, security_id: str) -> float:
        """Fetches live delivery allocation data."""
        url = f"{config.DHAN_BASE_URL}/marketfeed/delivery/{security_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return float(response.json().get("data", {}).get("deliveryPercentage", 0))
            return 0.0
        except Exception:
            return 0.0

    def fetch_option_chain(self, underlying_symbol: str) -> list:
        """Fetches active derivative chains for optimization routines."""
        url = f"{config.DHAN_BASE_URL}/marketfeed/optionchain"
        payload = {"underlyingSymbol": underlying_symbol}
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("data", {}).get("optionChain", [])
            return []
        except Exception:
            return []


class TradingEngine:
    """ADVANCED 8-POINT ENGINE: Processes technicals, market regime, OI, and Greeks."""
    def __init__(self):
        self.fetcher = DhanDataFetcher()

    def run_scoring_engine(self, raw_metrics: dict) -> dict:
        """Calculates the expanded 8-Point Swing Score Matrix."""
        score = 0
        breakdown = {}

        # 1. Trend Alignment
        trend = raw_metrics.get("close", 0) > raw_metrics.get("ema_20", 0)
        score += 1 if trend else 0
        breakdown["1. Trend (>20EMA)"] = "PASS" if trend else "FAIL"

        # 2. Momentum
        momentum = raw_metrics.get("rsi", 0) > 50
        score += 1 if momentum else 0
        breakdown["2. Momentum (RSI>50)"] = "PASS" if momentum else "FAIL"

        # 3. Volume Spike
        vol_spike = raw_metrics.get("volume", 0) > (raw_metrics.get("avg_volume", 1) * 1.5)
        score += 1 if vol_spike else 0
        breakdown["3. Volume Spike (>1.5x)"] = "PASS" if vol_spike else "FAIL"

        # 4. Delivery Strength
        del_strength = raw_metrics.get("delivery_pct", 0) >= config.MIN_DELIVERY_PCT
        score += 1 if del_strength else 0
        breakdown["4. Delivery Strength"] = f"{raw_metrics.get('delivery_pct', 0)}%" if del_strength else "FAIL"

        # 5. Price Breakout
        pa_breakout = raw_metrics.get("close", 0) > raw_metrics.get("prev_high", 0)
        score += 1 if pa_breakout else 0
        breakdown["5. Price Breakout"] = "PASS" if pa_breakout else "FAIL"

        # 6. Index Safety Filter (New)
        index_safe = raw_metrics.get("nifty_trend", "BEARISH") == "BULLISH"
        score += 1 if index_safe else 0
        breakdown["6. Nifty Market Regime"] = "BULLISH (SAFE)" if index_safe else "BEARISH (CAUTION)"

        # 7. Open Interest Build-up Confirmation (New)
        oi_confirm = raw_metrics.get("oi_change_pct", 0) > 2.0 and raw_metrics.get("price_change_pct", 0) > 0
        score += 1 if oi_confirm else 0
        breakdown["7. OI Build-up Type"] = "LONG BUILDUP" if oi_confirm else "LIQUIDATION / SHORT COVER"

        # 8. ATR Risk Proximity Check (New)
        atr_limit = raw_metrics.get("day_move", 0) < (raw_metrics.get("atr", 1) * 1.5)
        score += 1 if atr_limit else 0
        breakdown["8. ATR Overextended Check"] = "SAFE (Not Chasing)" if atr_limit else "OVEREXTENDED (Wait for Dip)"

        return {"total_score": score, "breakdown": breakdown}

    def route_asset(self, symbol: str, security_id: str, is_fno_eligible: bool, raw_metrics: dict) -> dict:
        """Determines execution routing paths based on systemic parameters."""
        delivery_pct = self.fetcher.fetch_delivery_data(security_id)
        raw_metrics["delivery_pct"] = delivery_pct
        
        scoring_results = self.run_scoring_engine(raw_metrics)
        score = scoring_results["total_score"]

        # Multi-Path Allocator Matrix
        if score >= 6:
            if is_fno_eligible and raw_metrics.get("iv_rank", 100) <= config.MAX_IV_RANK_FOR_BUYING:
                route = "⚡ F&O (Options Buy Loop Unlocked)"
            elif is_fno_eligible:
                route = "📈 F&O (Futures Long / Options Spread due to High IV)"
            else:
                route = "💰 MTF (Margin Trading Facility - High conviction Spot Buy)"
        elif 4 <= score <= 5:
            route = "🛡️ MTF / Cash Equity (Conservative Capital Footprint)"
        else:
            route = "❌ NO TRADE (Alpha score falls below structural risk floor)"

        return {
            "symbol": symbol,
            "score": score,
            "route": route,
            "breakdown": scoring_results["breakdown"]
        }

    def optimize_strike_with_targets(self, underlying_symbol: str, current_price: float, atr: float, target_delta: float = 0.5) -> dict:
        """Maps out the optimal strike contract, Stop-Loss zones, and estimated Premium Take-Profits."""
        raw_chain = self.fetcher.fetch_option_chain(underlying_symbol)
        if not raw_chain:
            return {"status": "Error", "message": "Failed to pull live option chains from Dhan"}

        df = pd.DataFrame(raw_chain)
        df = df[df['daysToExpiry'] >= config.DAYS_TO_EXPIRY_THRESHOLD]

        if df.empty:
            return {"status": "Error", "message": "No active contracts cleared expiry filter constraints"}

        # Select closest option contract matching our target Delta (0.50 for At-The-Money)
        df['delta_diff'] = (df['delta'] - target_delta).abs()
        optimal_row = df.sort_values(by='delta_diff').iloc[0]

        # Calculate mathematical Spot boundaries using ATR volatility bands
        stop_loss_spot = current_price - (1.5 * atr)
        take_profit_spot = current_price + (3.0 * atr)  # Structured 1:2 Risk-to-Reward Ratio

        # Calculate Greek-adjusted target premiums
        delta = float(optimal_row['delta'])
        theta = float(optimal_row['theta'])
        current_premium = float(optimal_row['lastPrice'])

        spot_move_to_tp = take_profit_spot - current_price
        spot_move_to_sl = stop_loss_spot - current_price

        # Premium pricing formulas incorporating Delta movement and 2 days of estimated time decay
        estimated_tp_premium = current_premium + (spot_move_to_tp * delta) + (2 * theta)
        estimated_sl_premium = max(0.5, current_premium + (spot_move_to_sl * delta) + (2 * theta))

        return {
            "status": "Success",
            "strike": optimal_row['strikePrice'],
            "expiry": str(optimal_row['expiryDate']),
            "delta": delta,
            "theta": theta,
            "current_premium": current_premium,
            "type": str(optimal_row['optionType']),
            "spot_sl": round(stop_loss_spot, 2),
            "spot_tp": round(take_profit_spot, 2),
            "premium_sl": round(estimated_sl_premium, 2),
            "premium_tp": round(estimated_tp_premium, 2)
        }
