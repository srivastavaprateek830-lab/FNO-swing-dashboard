import pandas as pd

def get_master_market_feed() -> pd.DataFrame:
    """MASTER INSTALMENT METADATA: Houses the entire active NSE liquid derivative stock universe."""
    raw_market_map = {
        "Nifty Bank": [
            {"Symbol": "HDFCBANK", "ID": "1333", "Price": 1650.0, "EMA20": 1620.0, "RSI": 58, "Vol": 8200000, "AvgVol": 5000000, "PrevHigh": 1640.0, "IVR": 22, "OI_Chg": 4.1, "Price_Chg": 1.2, "DayMove": 18.0, "ATR": 22.0, "FnO": True},
            {"Symbol": "ICICIBANK", "ID": "11483", "Price": 1120.0, "EMA20": 1100.0, "RSI": 62, "Vol": 6500000, "AvgVol": 4000000, "PrevHigh": 1115.0, "IVR": 18, "OI_Chg": 3.8, "Price_Chg": 0.9, "DayMove": 12.0, "ATR": 15.0, "FnO": True},
            {"Symbol": "SBIN", "ID": "3045", "Price": 780.0, "EMA20": 795.0, "RSI": 45, "Vol": 3100000, "AvgVol": 5000000, "PrevHigh": 790.0, "IVR": 35, "OI_Chg": -1.5, "Price_Chg": -0.8, "DayMove": 8.0, "ATR": 12.0, "FnO": True},
            {"Symbol": "AXISBANK", "ID": "5900", "Price": 1050.0, "EMA20": 1030.0, "RSI": 55, "Vol": 4200000, "AvgVol": 3500000, "PrevHigh": 1042.0, "IVR": 21, "OI_Chg": 1.9, "Price_Chg": 0.7, "DayMove": 11.0, "ATR": 18.0, "FnO": True},
            {"Symbol": "KOTAKBANK", "ID": "1922", "Price": 1780.0, "EMA20": 1810.0, "RSI": 48, "Vol": 2200000, "AvgVol": 2500000, "PrevHigh": 1795.0, "IVR": 16, "OI_Chg": -0.4, "Price_Chg": -0.3, "DayMove": 14.0, "ATR": 26.0, "FnO": True},
            {"Symbol": "INDUSINDBK", "ID": "5258", "Price": 1450.0, "EMA20": 1430.0, "RSI": 52, "Vol": 1800000, "AvgVol": 1500000, "PrevHigh": 1440.0, "IVR": 24, "OI_Chg": 2.1, "Price_Chg": 0.5, "DayMove": 15.0, "ATR": 28.0, "FnO": True},
            {"Symbol": "BANKBARODA", "ID": "4668", "Price": 250.0, "EMA20": 242.0, "RSI": 56, "Vol": 5500000, "AvgVol": 4200000, "PrevHigh": 248.0, "IVR": 19, "OI_Chg": 3.4, "Price_Chg": 1.1, "DayMove": 3.5, "ATR": 5.2, "FnO": True},
            {"Symbol": "PNB", "ID": "10666", "Price": 125.0, "EMA20": 121.0, "RSI": 54, "Vol": 12000000, "AvgVol": 9000000, "PrevHigh": 124.0, "IVR": 27, "OI_Chg": 1.2, "Price_Chg": 0.8, "DayMove": 2.1, "ATR": 3.8, "FnO": True},
            {"Symbol": "CANBK", "ID": "10794", "Price": 115.0, "EMA20": 112.0, "RSI": 53, "Vol": 8000000, "AvgVol": 6500000, "PrevHigh": 114.2, "IVR": 22, "OI_Chg": 2.2, "Price_Chg": 0.6, "DayMove": 1.8, "ATR": 2.9, "FnO": True},
            {"Symbol": "FEDERALBNK", "ID": "10242", "Price": 160.0, "EMA20": 155.0, "RSI": 57, "Vol": 4100000, "AvgVol": 3200000, "PrevHigh": 158.5, "IVR": 15, "OI_Chg": 4.1, "Price_Chg": 1.4, "DayMove": 2.2, "ATR": 4.1, "FnO": True},
            {"Symbol": "IDFCFIRSTB", "ID": "11184", "Price": 82.0, "EMA20": 84.0, "RSI": 44, "Vol": 9500000, "AvgVol": 11000000, "PrevHigh": 83.5, "IVR": 31, "OI_Chg": -1.8, "Price_Chg": -0.9, "DayMove": 1.1, "ATR": 2.1, "FnO": True},
            {"Symbol": "AUBANK", "ID": "21238", "Price": 620.0, "EMA20": 605.0, "RSI": 55, "Vol": 1100000, "AvgVol": 900000, "PrevHigh": 614.0, "IVR": 20, "OI_Chg": 2.8, "Price_Chg": 1.2, "DayMove": 8.5, "ATR": 14.5, "FnO": True},
            {"Symbol": "BANDHANBNK", "ID": "22622", "Price": 190.0, "EMA20": 195.0, "RSI": 46, "Vol": 3400000, "AvgVol": 4000000, "PrevHigh": 193.0, "IVR": 28, "OI_Chg": -0.5, "Price_Chg": -0.4, "DayMove": 3.1, "ATR": 6.2, "FnO": True}
        ],
        "Nifty Auto": [
            {"Symbol": "TATAMOTORS", "ID": "3456", "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0, "FnO": True},
            {"Symbol": "MARUTI", "ID": "10999", "Price": 12200.0, "EMA20": 12100.0, "RSI": 51, "Vol": 400000, "AvgVol": 350000, "PrevHigh": 12180.0, "IVR": 19, "OI_Chg": 0.5, "Price_Chg": 0.3, "DayMove": 90.0, "ATR": 180.0, "FnO": True},
            {"Symbol": "M&M", "ID": "2031", "Price": 2050.0, "EMA20": 1980.0, "RSI": 64, "Vol": 3100000, "AvgVol": 2200000, "PrevHigh": 2020.0, "IVR": 26, "OI_Chg": 4.2, "Price_Chg": 1.8, "DayMove": 35.0, "ATR": 42.0, "FnO": True},
            {"Symbol": "BAJAJ-AUTO", "ID": "16669", "Price": 9100.0, "EMA20": 8850.0, "RSI": 61, "Vol": 600000, "AvgVol": 500000, "PrevHigh": 8980.0, "IVR": 31, "OI_Chg": 2.1, "Price_Chg": 1.1, "DayMove": 110.0, "ATR": 140.0, "FnO": True},
            {"Symbol": "HEROMOTOCO", "ID": "1348", "Price": 4600.0, "EMA20": 4510.0, "RSI": 55, "Vol": 800000, "AvgVol": 720000, "PrevHigh": 4580.0, "IVR": 23, "OI_Chg": 1.4, "Price_Chg": 0.8, "DayMove": 55.0, "ATR": 85.0, "FnO": True},
            {"Symbol": "EICHERMOT", "ID": "910", "Price": 4150.0, "EMA20": 4020.0, "RSI": 59, "Vol": 750000, "AvgVol": 600000, "PrevHigh": 4110.0, "IVR": 20, "OI_Chg": 3.1, "Price_Chg": 1.6, "DayMove": 48.0, "ATR": 72.0, "FnO": True},
            {"Symbol": "TVSMOTOR", "ID": "8442", "Price": 2100.0, "EMA20": 2020.0, "RSI": 63, "Vol": 1200000, "AvgVol": 900000, "PrevHigh": 2078.0, "IVR": 29, "OI_Chg": 5.2, "Price_Chg": 2.1, "DayMove": 32.0, "ATR": 44.0, "FnO": True},
            {"Symbol": "ASHOKLEY", "ID": "212", "Price": 175.0, "EMA20": 171.0, "RSI": 54, "Vol": 6500000, "AvgVol": 5200000, "PrevHigh": 174.0, "IVR": 18, "OI_Chg": 0.8, "Price_Chg": 0.5, "DayMove": 2.4, "ATR": 4.1, "FnO": True},
            {"Symbol": "BHARATFORG", "ID": "410", "Price": 1220.0, "EMA20": 1195.0, "RSI": 56, "Vol": 1100000, "AvgVol": 950000, "PrevHigh": 1212.0, "IVR": 25, "OI_Chg": 2.9, "Price_Chg": 1.2, "DayMove": 16.0, "ATR": 24.0, "FnO": True},
            {"Symbol": "EXIDEIND", "ID": "958", "Price": 320.0, "EMA20": 305.0, "RSI": 65, "Vol": 3800000, "AvgVol": 2500000, "PrevHigh": 314.0, "IVR": 34, "OI_Chg": 6.1, "Price_Chg": 3.2, "DayMove": 7.5, "ATR": 11.2, "FnO": True}
        ],
        "Nifty IT": [
            {"Symbol": "TCS", "ID": "11536", "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0, "FnO": True},
            {"Symbol": "INFY", "ID": "1594", "Price": 1520.0, "EMA20": 1500.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3000000, "PrevHigh": 1510.0, "IVR": 28, "OI_Chg": 2.5, "Price_Chg": 1.1, "DayMove": 22.0, "ATR": 28.0, "FnO": True},
            {"Symbol": "HCLTECH", "ID": "1345", "Price": 1410.0, "EMA20": 1390.0, "RSI": 54, "Vol": 2800000, "AvgVol": 2000000, "PrevHigh": 1400.0, "IVR": 20, "OI_Chg": 3.1, "Price_Chg": 1.4, "DayMove": 19.0, "ATR": 24.0, "FnO": True},
            {"Symbol": "LTIM", "ID": "17832", "Price": 4900.0, "EMA20": 4820.0, "RSI": 59, "Vol": 900000, "AvgVol": 700000, "PrevHigh": 4880.0, "IVR": 32, "OI_Chg": 1.8, "Price_Chg": 0.8, "DayMove": 45.0, "ATR": 85.0, "FnO": True},
            {"Symbol": "WIPRO", "ID": "3787", "Price": 480.0, "EMA20": 472.0, "RSI": 54, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 478.0, "IVR": 14, "OI_Chg": 1.1, "Price_Chg": 0.6, "DayMove": 5.0, "ATR": 8.0, "FnO": True},
            {"Symbol": "TECHM", "ID": "13357", "Price": 1250.0, "EMA20": 1220.0, "RSI": 57, "Vol": 1500000, "AvgVol": 1100000, "PrevHigh": 1240.0, "IVR": 22, "OI_Chg": 2.4, "Price_Chg": 1.5, "DayMove": 18.0, "ATR": 25.0, "FnO": True},
            {"Symbol": "COFORGE", "ID": "11543", "Price": 5200.0, "EMA20": 5050.0, "RSI": 58, "Vol": 450000, "AvgVol": 380000, "PrevHigh": 5140.0, "IVR": 31, "OI_Chg": 4.1, "Price_Chg": 2.1, "DayMove": 85.0, "ATR": 115.0, "FnO": True},
            {"Symbol": "PERSISTENT", "ID": "18365", "Price": 3650.0, "EMA20": 3510.0, "RSI": 61, "Vol": 600000, "AvgVol": 450000, "PrevHigh": 3600.0, "IVR": 29, "OI_Chg": 4.8, "Price_Chg": 1.9, "DayMove": 48.0, "ATR": 74.0, "FnO": True}
        ],
        "Nifty Pharma": [
            {"Symbol": "SUNPHARMA", "ID": "3333", "Price": 1540.0, "EMA20": 1510.0, "RSI": 58, "Vol": 1800000, "AvgVol": 1200000, "PrevHigh": 1530.0, "IVR": 19, "OI_Chg": 2.2, "Price_Chg": 1.3, "DayMove": 14.0, "ATR": 22.0, "FnO": True},
            {"Symbol": "CIPLA", "ID": "694", "Price": 1420.0, "EMA20": 1395.0, "RSI": 59, "Vol": 2100000, "AvgVol": 1500000, "PrevHigh": 1405.0, "IVR": 24, "OI_Chg": 3.0, "Price_Chg": 1.6, "DayMove": 20.0, "ATR": 25.0, "FnO": True},
            {"Symbol": "DRREDDY", "ID": "881", "Price": 6200.0, "EMA20": 6250.0, "RSI": 47, "Vol": 500000, "AvgVol": 650000, "PrevHigh": 6280.0, "IVR": 14, "OI_Chg": -1.1, "Price_Chg": -0.4, "DayMove": 40.0, "ATR": 95.0, "FnO": True},
            {"Symbol": "LUPIN", "ID": "1994", "Price": 1610.0, "EMA20": 1540.0, "RSI": 64, "Vol": 1500000, "AvgVol": 1100000, "PrevHigh": 1595.0, "IVR": 28, "OI_Chg": 5.1, "Price_Chg": 2.2, "DayMove": 25.0, "ATR": 38.0, "FnO": True},
            {"Symbol": "DIVISLAB", "ID": "10940", "Price": 3750.0, "EMA20": 3680.0, "RSI": 54, "Vol": 450000, "AvgVol": 400000, "PrevHigh": 3720.0, "IVR": 21, "OI_Chg": 1.5, "Price_Chg": 0.8, "DayMove": 42.0, "ATR": 65.0, "FnO": True},
            {"Symbol": "AUROPHARMA", "ID": "275", "Price": 1080.0, "EMA20": 1045.0, "RSI": 57, "Vol": 1900000, "AvgVol": 1400000, "PrevHigh": 1072.0, "IVR": 26, "OI_Chg": 2.9, "Price_Chg": 1.1, "DayMove": 15.0, "ATR": 24.0, "FnO": True}
        ],
        "Nifty Metal": [
            {"Symbol": "TATASTEEL", "ID": "3499", "Price": 155.0, "EMA20": 151.0, "RSI": 60, "Vol": 22000000, "AvgVol": 15000000, "PrevHigh": 153.5, "IVR": 34, "OI_Chg": 5.1, "Price_Chg": 2.1, "DayMove": 4.0, "ATR": 4.5, "FnO": True},
            {"Symbol": "JSWSTEEL", "ID": "11723", "Price": 880.0, "EMA20": 895.0, "RSI": 44, "Vol": 1800000, "AvgVol": 2500000, "PrevHigh": 892.0, "IVR": 18, "OI_Chg": -2.1, "Price_Chg": -1.2, "DayMove": 10.0, "ATR": 16.0, "FnO": True},
            {"Symbol": "HINDALCO", "ID": "1363", "Price": 610.0, "EMA20": 595.0, "RSI": 56, "Vol": 4500000, "AvgVol": 3800000, "PrevHigh": 604.0, "IVR": 25, "OI_Chg": 1.4, "Price_Chg": 0.8, "DayMove": 8.0, "ATR": 14.0, "FnO": True},
            {"Symbol": "VEDL", "ID": "3521", "Price": 280.0, "EMA20": 268.0, "RSI": 61, "Vol": 9500000, "AvgVol": 7000000, "PrevHigh": 276.5, "IVR": 38, "OI_Chg": 4.9, "Price_Chg": 2.2, "DayMove": 6.5, "ATR": 9.2, "FnO": True},
            {"Symbol": "JINDALSTEL", "ID": "11725", "Price": 840.0, "EMA20": 810.0, "RSI": 58, "Vol": 2100000, "AvgVol": 1600000, "PrevHigh": 832.0, "IVR": 27, "OI_Chg": 3.8, "Price_Chg": 1.4, "DayMove": 14.5, "ATR": 21.0, "FnO": True}
        ],
        "Nifty FMCG": [
            {"Symbol": "HINDUNILVR", "ID": "1330", "Price": 2420.0, "EMA20": 2450.0, "RSI": 41, "Vol": 1200000, "AvgVol": 1500000, "PrevHigh": 2445.0, "IVR": 12, "OI_Chg": -0.8, "Price_Chg": -0.4, "DayMove": 15.0, "ATR": 35.0, "FnO": True},
            {"Symbol": "ITC", "ID": "1660", "Price": 435.0, "EMA20": 428.0, "RSI": 55, "Vol": 8500000, "AvgVol": 7000000, "PrevHigh": 432.0, "IVR": 17, "OI_Chg": 2.1, "Price_Chg": 0.9, "DayMove": 4.0, "ATR": 7.0, "FnO": True},
            {"Symbol": "BRITANNIA", "ID": "547", "Price": 5100.0, "EMA20": 4980.0, "RSI": 62, "Vol": 400000, "AvgVol": 300000, "PrevHigh": 5040.0, "IVR": 22, "OI_Chg": 3.8, "Price_Chg": 1.7, "DayMove": 65.0, "ATR": 80.0, "FnO": True},
            {"Symbol": "NESTLEIND", "ID": "17963", "Price": 2500.0, "EMA20": 2460.0, "RSI": 54, "Vol": 550000, "AvgVol": 480000, "PrevHigh": 2488.0, "IVR": 16, "OI_Chg": 1.4, "Price_Chg": 0.5, "DayMove": 22.0, "ATR": 41.0, "FnO": True},
            {"Symbol": "TATACONSUM", "ID": "3432", "Price": 1120.0, "EMA20": 1080.0, "RSI": 59, "Vol": 1800000, "AvgVol": 1300000, "PrevHigh": 1105.0, "IVR": 24, "OI_Chg": 4.1, "Price_Chg": 1.5, "DayMove": 18.0, "ATR": 26.0, "FnO": True},
            {"Symbol": "DABUR", "ID": "772", "Price": 530.0, "EMA20": 542.0, "RSI": 46, "Vol": 2100000, "AvgVol": 2400000, "PrevHigh": 538.0, "IVR": 14, "OI_Chg": -0.6, "Price_Chg": -0.3, "DayMove": 4.8, "ATR": 9.1, "FnO": True},
            {"Symbol": "MARICO", "ID": "2140", "Price": 515.0, "EMA20": 502.0, "RSI": 56, "Vol": 1400000, "AvgVol": 1100000, "PrevHigh": 511.0, "IVR": 18, "OI_Chg": 1.9, "Price_Chg": 0.8, "DayMove": 5.2, "ATR": 9.8, "FnO": True}
        ],
        "Nifty Oil & Gas": [
            {"Symbol": "RELIANCE", "ID": "2885", "Price": 2450.0, "EMA20": 2400.0, "RSI": 58, "Vol": 4200000, "AvgVol": 3100000, "PrevHigh": 2440.0, "IVR": 35, "OI_Chg": 4.5, "Price_Chg": 1.2, "DayMove": 25.0, "ATR": 35.0, "FnO": True},
            {"Symbol": "ONGC", "ID": "2475", "Price": 270.0, "EMA20": 255.0, "RSI": 61, "Vol": 8500000, "AvgVol": 6200000, "PrevHigh": 266.0, "IVR": 28, "OI_Chg": 5.1, "Price_Chg": 2.4, "DayMove": 4.5, "ATR": 7.2, "FnO": True},
            {"Symbol": "BPCL", "ID": "526", "Price": 610.0, "EMA20": 585.0, "RSI": 57, "Vol": 4800000, "AvgVol": 3900000, "PrevHigh": 602.0, "IVR": 22, "OI_Chg": 3.2, "Price_Chg": 1.5, "DayMove": 9.2, "ATR": 14.1, "FnO": True}
        ],
        "Nifty Power & Infra": [
            {"Symbol": "NTPC", "ID": "11630", "Price": 345.0, "EMA20": 328.0, "RSI": 62, "Vol": 6800000, "AvgVol": 5000000, "PrevHigh": 341.2, "IVR": 29, "OI_Chg": 5.2, "Price_Chg": 2.1, "DayMove": 5.5, "ATR": 9.1, "FnO": True},
            {"Symbol": "POWERGRID", "ID": "14977", "Price": 285.0, "EMA20": 272.0, "RSI": 61, "Vol": 7200000, "AvgVol": 5500000, "PrevHigh": 281.8, "IVR": 25, "OI_Chg": 4.6, "Price_Chg": 1.9, "DayMove": 4.2, "ATR": 6.9, "FnO": True},
            {"Symbol": "TATAPOWER", "ID": "3426", "Price": 395.0, "EMA20": 378.0, "RSI": 63, "Vol": 5200000, "AvgVol": 4100000, "PrevHigh": 391.0, "IVR": 32, "OI_Chg": 4.9, "Price_Chg": 2.2, "DayMove": 6.8, "ATR": 11.5, "FnO": True}
        ],
        "Nifty Commodities": [
            {"Symbol": "ACC", "ID": "22", "Price": 2550.0, "EMA20": 2490.0, "RSI": 56, "Vol": 600000, "AvgVol": 480000, "PrevHigh": 2532.0, "IVR": 24, "OI_Chg": 2.8, "Price_Chg": 1.1, "DayMove": 32.0, "ATR": 48.0, "FnO": True},
            {"Symbol": "AMBUJACEM", "ID": "63", "Price": 615.0, "EMA20": 592.0, "RSI": 58, "Vol": 3200000, "AvgVol": 2500000, "PrevHigh": 608.0, "IVR": 27, "OI_Chg": 3.9, "Price_Chg": 1.5, "DayMove": 8.5, "ATR": 14.1, "FnO": True},
            {"Symbol": "GRASIM", "ID": "1233", "Price": 2240.0, "EMA20": 2180.0, "RSI": 57, "Vol": 800000, "AvgVol": 650000, "PrevHigh": 2215.0, "IVR": 21, "OI_Chg": 2.4, "Price_Chg": 1.2, "DayMove": 28.0, "ATR": 45.0, "FnO": True}
        ],
        "Nifty Services": [
            {"Symbol": "DLF", "ID": "14732", "Price": 880.0, "EMA20": 842.0, "RSI": 62, "Vol": 3500000, "AvgVol": 2500000, "PrevHigh": 868.0, "IVR": 34, "OI_Chg": 5.4, "Price_Chg": 2.5, "DayMove": 14.0, "ATR": 21.0, "FnO": True},
            {"Symbol": "GODREJPROP", "ID": "17823", "Price": 2350.0, "EMA20": 2240.0, "RSI": 61, "Vol": 800000, "AvgVol": 620000, "PrevHigh": 2310.0, "IVR": 31, "OI_Chg": 4.8, "Price_Chg": 2.1, "DayMove": 38.0, "ATR": 56.0, "FnO": True}
        ]
    }
    compiled_list = []
    for sector_name, stocks in raw_market_map.items():
        for s in stocks:
            s["Sector"] = sector_name
            compiled_list.append(s)
    return pd.DataFrame(compiled_list)
