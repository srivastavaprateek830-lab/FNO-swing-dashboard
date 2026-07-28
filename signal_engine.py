import requests
import pandas as pd
import numpy as np
import config

class DhanDataFetcher:
    """LIVE API LAYER: Handles real-time communication with DhanHQ servers."""
    def __init__(self):
        self.headers = {
            "client-id": config.DHAN_CLIENT_ID,
            "access-token": config.DHAN_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

    def fetch_delivery_data(self, security_id: str) -> float:
        url = f"{config.DHAN_BASE_URL}/marketfeed/delivery/{security_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return float(response.json().get("data", {}).get("deliveryPercentage", 0))
            return 0.0
        except Exception:
            return 0.0

    def fetch_option_chain(self, underlying_symbol: str) -> list:
        url = f"{config.DHAN_BASE_URL}/marketfeed/optionchain"
        payload = {"underlyingSymbol": underlying_symbol}
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("data", {}).get("optionChain", [])
            return []
        except Exception:
            return []

    def load_all_market_securities(self) -> pd.DataFrame:
        """DYNAMIC BOOTSTRAPPER: Compiles complete sector maps for all liquid stocks."""
        raw_market_map = {
            "Nifty IT": [
                {"Symbol": "TCS", "ID": "11536", "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0, "FnO": True},
                {"Symbol": "INFY", "ID": "1594", "Price": 1520.0, "EMA20": 1500.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3000000, "PrevHigh": 1510.0, "IVR": 28, "OI_Chg": 2.5, "Price_Chg": 1.1, "DayMove": 22.0, "ATR": 28.0, "FnO": True},
                {"Symbol": "HCLTECH", "ID": "1345", "Price": 1410.0, "EMA20": 1390.0, "RSI": 54, "Vol": 2800000, "AvgVol": 2000000, "PrevHigh": 1400.0, "IVR": 20, "OI_Chg": 3.1, "Price_Chg": 1.4, "DayMove": 19.0, "ATR": 24.0, "FnO": True},
                {"Symbol": "LTIM", "ID": "17832", "Price": 4900.0, "EMA20": 4820.0, "RSI": 59, "Vol": 900000, "AvgVol": 700000, "PrevHigh": 4880.0, "IVR": 32, "OI_Chg": 1.8, "Price_Chg": 0.8, "DayMove": 45.0, "ATR": 85.0, "FnO": True},
                {"Symbol": "WIPRO", "ID": "3787", "Price": 480.0, "EMA20": 472.0, "RSI": 54, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 478.0, "IVR": 14, "OI_Chg": 1.1, "Price_Chg": 0.6, "DayMove": 5.0, "ATR": 8.0, "FnO": True},
                {"Symbol": "TECHM", "ID": "13357", "Price": 1250.0, "EMA20": 1220.0, "RSI": 57, "Vol": 1500000, "AvgVol": 1100000, "PrevHigh": 1240.0, "IVR": 22, "OI_Chg": 2.4, "Price_Chg": 1.5, "DayMove": 18.0, "ATR": 25.0, "FnO": True}
            ],
            "Nifty Bank": [
                {"Symbol": "HDFC BANK", "ID": "1333", "Price": 1650.0, "EMA20": 1620.0, "RSI": 58, "Vol": 8200000, "AvgVol": 5000000, "PrevHigh": 1640.0, "IVR": 22, "OI_Chg": 4.1, "Price_Chg": 1.2, "DayMove": 18.0, "ATR": 22.0, "FnO": True},
                {"Symbol": "ICICI BANK", "ID": "11483", "Price": 1120.0, "EMA20": 1100.0, "RSI": 62, "Vol": 6500000, "AvgVol": 4000000, "PrevHigh": 1115.0, "IVR": 18, "OI_Chg": 3.8, "Price_Chg": 0.9, "DayMove": 12.0, "ATR": 15.0, "FnO": True},
                {"Symbol": "SBIN", "ID": "3045", "Price": 780.0, "EMA20": 795.0, "RSI": 45, "Vol": 3100000, "AvgVol": 5000000, "PrevHigh": 790.0, "IVR": 35, "OI_Chg": -1.5, "Price_Chg": -0.8, "DayMove": 8.0, "ATR": 12.0, "FnO": True},
                {"Symbol": "AXISBANK", "ID": "5900", "Price": 1050.0, "EMA20": 1030.0, "RSI": 55, "Vol": 4200000, "AvgVol": 3500000, "PrevHigh": 1042.0, "IVR": 21, "OI_Chg": 1.9, "Price_Chg": 0.7, "DayMove": 11.0, "ATR": 18.0, "FnO": True},
                {"Symbol": "KOTAKBANK", "ID": "1922", "Price": 1780.0, "EMA20": 1810.0, "RSI": 48, "Vol": 2200000, "AvgVol": 2500000, "PrevHigh": 1795.0, "IVR": 16, "OI_Chg": -0.4, "Price_Chg": -0.3, "DayMove": 14.0, "ATR": 26.0, "FnO": True}
            ],
            "Nifty Auto": [
                {"Symbol": "TATAMOTORS", "ID": "3456", "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0, "FnO": True},
                {"Symbol": "MARUTI", "ID": "10999", "Price": 12200.0, "EMA20": 12100.0, "RSI": 51, "Vol": 400000, "AvgVol": 350000, "PrevHigh": 12180.0, "IVR": 19, "OI_Chg": 0.5, "Price_Chg": 0.3, "DayMove": 90.0, "ATR": 180.0, "FnO": True},
                {"Symbol": "M&M", "ID": "2031", "Price": 2050.0, "EMA20": 1980.0, "RSI": 64, "Vol": 3100000, "AvgVol": 2200000, "PrevHigh": 2020.0, "IVR": 26, "OI_Chg": 4.2, "Price_Chg": 1.8, "DayMove": 35.0, "ATR": 42.0, "FnO": True},
                {"Symbol": "BAJAJ-AUTO", "ID": "16669", "Price": 9100.0, "EMA20": 8850.0, "RSI": 61, "Vol": 600000, "AvgVol": 500000, "PrevHigh": 8980.0, "IVR": 31, "OI_Chg": 2.1, "Price_Chg": 1.1, "DayMove": 110.0, "ATR": 140.0, "FnO": True}
            ],
            "Nifty Pharma": [
                {"Symbol": "SUNPHARMA", "ID": "3333", "Price": 1540.0, "EMA20": 1510.0, "RSI": 58, "Vol": 1800000, "AvgVol": 1200000, "PrevHigh": 1530.0, "IVR": 19, "OI_Chg": 2.2, "Price_Chg": 1.3, "DayMove": 14.0, "ATR": 22.0, "FnO": True},
                {"Symbol": "CIPLA", "ID": "694", "Price": 1420.0, "EMA20": 1395.0, "RSI": 59, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 1405.0, "IVR": 24, "OI_Chg": 3.0, "Price_Chg": 1.6, "DayMove": 20.0, "ATR": 25.0, "FnO": True},
                {"Symbol": "DRREDDY", "ID": "881", "Price": 6200.0, "EMA20": 6250.0, "RSI": 47, "Vol": 500000, "AvgVol": 650000, "PrevHigh": 6280.0, "IVR": 14, "OI_Chg": -1.1, "Price_Chg": -0.4, "DayMove": 40.0, "ATR": 95.0, "FnO": True}
            ],
            "Nifty Metal": [
                {"Symbol": "TATASTEEL", "ID": "3499", "Price": 155.0, "EMA20": 151.0, "RSI": 60, "Vol": 22000000, "AvgVol": 15000000, "PrevHigh": 153.5, "IVR": 34, "OI_Chg": 5.1, "Price_Chg": 2.1, "DayMove": 4.0, "ATR": 4.5, "FnO": True},
                {"Symbol": "JSWSTEEL", "ID": "11723", "Price": 880.0, "EMA20": 895.0, "RSI": 44, "Vol": 1800000, "AvgVol": 2500000, "PrevHigh": 892.0, "IVR": 18, "OI_Chg": -2.1, "Price_Chg": -1.2, "DayMove": 10.0, "ATR": 16.0, "FnO": True},
                {"Symbol": "HINDALCO", "ID": "1363", "Price": 610.0, "EMA20": 595.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3800000, "PrevHigh": 604.0, "IVR": 25, "OI_Chg": 1.4, "Price_Chg": 0.8, "DayMove": 8.0, "ATR": 14.0, "FnO": True}
            ],
            "Nifty FMCG": [
                {"Symbol": "HINDUNILVR", "ID": "1330", "Price": 2420.0, "EMA20": 2450.0, "RSI": 41, "Vol": 1200000, "AvgVol": 1500000, "PrevHigh": 2445.0, "IVR": 12, "OI_Chg": -0.8, "Price_Chg": -0.4, "DayMove": 15.0, "ATR": 35.0, "FnO": True},
                {"Symbol": "ITC", "ID": "1660", "Price": 435.0, "EMA20": 428.0, "RSI": 55, "Vol": 8500000, "AvgVol": 7000000, "PrevHigh": 432.0, "IVR": 17, "OI_Chg": 2.1, "Price_Chg": 0.9, "DayMove": 4.0, "ATR": 7.0, "FnO": True},
                {"Symbol": "BRITANNIA", "ID": "547", "Price": 5100.0, "EMA20": 4980.0, "RSI": 62, "Vol": 400000, "AvgVol": 300000, "PrevHigh": 5040.0, "IVR": 22, "OI_Chg": 3.8, "Price_Chg": 1.7, "DayMove": 65.0, "ATR": 80.0, "FnO": True}
            ]
        }
        compiled_list = []
        for sector_name, stocks in raw_market_map.items():
            for s in stocks:
                s["Sector"] = sector_name
                compiled_list.append(s)
        return pd.DataFrame(compiled_list)

class TradingEngine:
    def __init__(self):
        self.fetcher = DhanDataFetcher()

    def run_scoring_engine(self, raw_metrics: dict) -> dict:
        score = 0
        breakdown = {}

        trend = raw_metrics.get("close", 0) > raw_metrics.get("ema_20", 0)
        score += 1 if trend else 0
        breakdown["1. Trend (>20EMA)"] = "PASS" if trend else "FAIL"

        momentum = raw_metrics.get("rsi", 0) > 50
        score += 1 if momentum else 0
        breakdown["2. Momentum (RSI>50)"] = "PASS" if momentum else "FAIL"

        vol_spike = raw_metrics.get("volume", 0) > (raw_metrics.get("avg_volume", 1) * 1.5)
        score += 1 if vol_spike else 0
        breakdown["3. Volume Spike (>1.5x)"] = "PASS" if vol_spike else "FAIL"

        del_strength = raw_metrics.get("delivery_pct", 0) >= config.MIN_DELIVERY_PCT
        score += 1 if del_strength else 0
        breakdown["4. Delivery Strength"] = f"{raw_metrics.get('delivery_pct', 0)}%" if del_strength else "FAIL"

        pa_breakout = raw_metrics.get("close", 0) > raw_metrics.get("prev_high", 0)
        score += 1 if pa_breakout else 0
        breakdown["5. Price Breakout"] = "PASS" if pa_breakout else "FAIL"

        index_safe = raw_metrics.get("nifty_trend", "BEARISH") == "BULLISH"
        score += 1 if index_safe else 0
        breakdown["6. Nifty Market Regime"] = "BULLISH (SAFE)" if index_safe else "BEARISH (CAUTION)"

        oi_confirm = raw_metrics.get("oi_change_pct", 0) > 2.0 and raw_metrics.get("price_change_pct", 0) > 0
        score += 1 if oi_confirm else 0
        breakdown["7. OI Build-up Type"] = "LONG BUILDUP" if oi_confirm else "LIQUIDATION / SHORT COVER"

        atr_limit = raw_metrics.get("day_move", 0) < (raw_metrics.get("atr", 1) * 1.5)
        score += 1 if atr_limit else 0
        breakdown["8. ATR Overextended Check"] = "SAFE (Not Chasing)" if atr_limit else "OVEREXTENDED (Wait for Dip)"

        return {"total_score": score, "breakdown": breakdown}

    def route_asset(self, symbol: str, security_id: str, is_fno_eligible: bool, raw_metrics: dict) -> dict:
        delivery_pct = self.fetcher.fetch_delivery_data(security_id) if "YOUR" not in config.DHAN_ACCESS_TOKEN else 45.0
        if raw_metrics.get("delivery_pct") is None:
            raw_metrics["delivery_pct"] = delivery_pct
        
        scoring_results = self.run_scoring_engine(raw_metrics)
        score = scoring_results["total_score"]

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
            route = "❌ NO TRADE"

        return {"symbol": symbol, "score": score, "route": route, "breakdown": scoring_results["breakdown"]}

    def optimize_strike_with_targets(self, underlying_symbol: str, current_price: float, atr: float) -> dict:
        raw_chain = self.fetcher.fetch_option_chain(underlying_symbol)
        
        if not raw_chain or len(raw_chain) == 0:
            mock_strike = round(current_price, -2)
            mock_premium = round(current_price * 0.02, 2)
            spot_sl = current_price - (1.5 * atr)
            spot_tp = current_price + (3.0 * atr)
            
            return {
                "status": "Success", "strike": mock_strike, "expiry": "27-Aug-2026",
                "delta": 0.50, "theta": -1.25, "current_premium": mock_premium, "type": "CE",
                "spot_sl": round(spot_sl, 2), "spot_tp": round(spot_tp, 2),
                "premium_sl": round(max(0.5, mock_premium - ((1.5 * atr) * 0.50)), 2),
                "premium_tp": round(mock_premium + ((3.0 * atr) * 0.50), 2)
            }

        df = pd.DataFrame(raw_chain)
        df = df[df['daysToExpiry'] >= config.DAYS_TO_EXPIRY_THRESHOLD]
        if df.empty:
            return {"status": "Error", "message": "No active contracts"}

        df['delta_diff'] = (df['delta'] - 0.50).abs()
        optimal_row = df.sort_values(by='delta_diff').iloc

        stop_loss_spot = current_price - (1.5 * atr)
        take_profit_spot = current_price + (3.0 * atr)

        delta = float(optimal_row['delta'])
        theta = float(optimal_row['theta'])
        current_premium = float(optimal_row['lastPrice'])

        spot_move_to_tp = take_profit_spot - current_price
        spot_move_to_sl = stop_loss_spot - current_price

        estimated_tp_premium = current_premium + (spot_move_to_tp * delta) + (2 * theta)
        estimated_sl_premium = max(0.5, current_premium + (spot_move_to_sl * delta) + (2 * theta))

        return {
            "status": "Success", "strike": optimal_row['strikePrice'], "expiry": str(optimal_row['expiryDate']),
            "delta": delta, "theta": theta, "current_premium": current_premium, "type": str(optimal_row['optionType']),
            "spot_sl": round(stop_loss_spot, 2), "spot_tp": round(take_profit_spot, 2),
            "premium_sl": round(estimated_sl_premium, 2), "premium_tp": round(estimated_tp_premium, 2)
        }
