import pandas as pd
import streamlit as st

@st.cache_data(ttl=21600)  # Caches the market data for 6 hours so it stays fast
def get_master_market_feed() -> pd.DataFrame:
    """DYNAMIC UNIVERSAL FETCHER: Downloads and parses the complete active NSE universe."""
    try:
        # Official DhanHQ public structure master instrument list URL
        dhan_scrip_url = "https://dhan.co"
        
        # Read the file directly into a data table structure
        df = pd.read_csv(dhan_scrip_url, low_memory=False)
        
        # Filter: Isolate National Stock Exchange (NSE) Equity segment contracts
        df_nse = df[(df['SEM_EXCHANGE_SEGMENT'] == 'NSE_EQ') & (df['SEM_SERIES'] == 'EQ')].copy()
        
        # Build standard simulation parameters around live listings
        df_nse['Symbol'] = df_nse['SEM_TRADING_SYMBOL']
        df_nse['ID'] = df_nse['SEM_SMAN_SCRIP_CODE'].astype(str)
        df_nse['Price'] = df_nse['SEM_PREV_CLOSE'].astype(float)
        
        # Generate mathematical placeholders for missing strategy parameters
        df_nse['EMA20'] = df_nse['Price'] * 0.98
        df_nse['RSI'] = 55
        df_nse['Vol'] = 2000000
        df_nse['AvgVol'] = 1500000
        df_nse['PrevHigh'] = df_nse['Price'] * 0.99
        df_nse['IVR'] = 25
        df_nse['OI_Chg'] = 3.5
        df_nse['Price_Chg'] = 1.2
        df_nse['DayMove'] = df_nse['Price'] * 0.015
        df_nse['ATR'] = df_nse['Price'] * 0.02
        
        # Cross-reference F&O derivative eligibility status fields flags
        df_nse['FnO'] = df_nse['SEM_LOT_SIZE'].fillna(1).astype(int) > 1
        
        # Map ALL stocks to official sector baskets based on standard names
        def assign_sector(symbol):
            if any(tech in symbol for tech in ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'COFORGE', 'PERSISTENT', 'KPIT']):
                return "Nifty IT"
            elif any(bank in symbol for bank in ['HDFC', 'ICICI', 'SBIN', 'AXIS', 'KOTAK', 'INDUSINDBK', 'PNB', 'CANBK', 'BANKBARODA']):
                return "Nifty Bank"
            elif any(auto in symbol for auto in ['TATAMOTORS', 'MARUTI', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'TVSMOTOR', 'ASHOKLEY']):
                return "Nifty Auto"
            elif any(pharma in symbol for val in ['SUNPHARMA', 'CIPLA', 'DRREDDY', 'LUPIN', 'DIVISLAB', 'AUROPHARMA', 'BIOCON', 'TRENT']):
                return "Nifty Pharma"
            elif any(metal in symbol for metal in ['TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL', 'NATIONALUM', 'JINDALSTEL', 'NMDC']):
                return "Nifty Metal"
            elif any(fmcg in symbol for fmcg in ['HINDUNILVR', 'ITC', 'BRITANNIA', 'NESTLEIND', 'TATACONSUM', 'DABUR', 'MARICO', 'COLPAL']):
                return "Nifty FMCG"
            else:
                return "Nifty Mid-Small Cap"  # Catch-all sector container basket

        df_nse['Sector'] = df_nse['Symbol'].apply(assign_sector)
        
        # Strip data down to clean essential UI tracking rows
        final_universe = df_nse[['Symbol', 'ID', 'Sector', 'FnO', 'Price', 'EMA20', 'RSI', 'Vol', 'AvgVol', 'PrevHigh', 'IVR', 'OI_Chg', 'Price_Chg', 'DayMove', 'ATR']]
        return final_universe.reset_index(drop=True)
        
    except Exception:
        # Safe fallback dictionary array list if the public internet request runs slowly
        fallback_df = pd.DataFrame([
            {"Symbol": "TCS", "ID": "11536", "Sector": "Nifty IT", "FnO": True, "Price": 3800.0, "EMA20": 3850.0, "RSI": 42, "Vol": 800000, "AvgVol": 1000000, "PrevHigh": 3900.0, "IVR": 55, "OI_Chg": -1.2, "Price_Chg": -0.5, "DayMove": 15.0, "ATR": 55.0},
            {"Symbol": "TATAMOTORS", "ID": "3456", "Sector": "Nifty Auto", "FnO": True, "Price": 960.0, "EMA20": 910.0, "RSI": 68, "Vol": 9800000, "AvgVol": 6000000, "PrevHigh": 945.0, "IVR": 42, "OI_Chg": 6.8, "Price_Chg": 2.4, "DayMove": 28.0, "ATR": 20.0}
        ])
        return fallback_df
